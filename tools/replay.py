#!/usr/bin/env python3
"""Regression replay for the native Tales of Destiny build.

    python3 tools/replay.py [--port N] [--disc PATH] [--out DIR]

Launches build/psx_runtime headless, drives the pad over the TCP debug server
and walks STEPS.  A step presses a pad word and then waits, measured in GUEST
frames (the `frame` command), until the screen matches a reference image from
evidence/.  Fixed wall-clock sleeps do not work: the guest runs ~300 fps and
its pace varies with host load.  Exit 0 only if every step passed.

Each run uses a private cwd and memory-card dir under OUT, so the saves in
build/ cannot change what the menu shows and psx_last_run_report.json (written
to the runtime's cwd) is always this run's.  The run dir is deleted when every
step passes and kept (log, report) when one fails.

Comparison: fraction of pixels in `box` whose bright/dark state (luma > LUM)
differs from the reference.  Raw mean abs diff does not work on the main menu:
the water/foliage behind it animates and the raw diff in the box cycles between
2.6 and 4.8 (measured over 700 samples), so a "< 2" test only passes at one
animation phase.  The bright mask is 0.0000 across the whole cycle, while the
title screen (PRESS START) scores 0.05.
"""
import argparse, json, os, shutil, socket, subprocess, sys, tempfile, time
from PIL import Image, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START, CIRCLE, CROSS = 0xFFF7, 0xDFFF, 0xBFFF     # raw active-low PS1 pad words
HOLD = 6          # frames a press is held
GAP = 90          # guest frames between re-presses of a `repeat` step
LUM, TOL = 180, 0.005
WALL_CAP = 180    # seconds per step, only so a wedged guest cannot hang the run

# name: label | press: pad word sent when the step starts | repeat: re-press every
# GAP frames until matched | ref: reference PNG under the repo | box: (x0,y0,x1,y1)
# compared | timeout: guest frames the step may take.  Append new steps here.
STEPS = [
    dict(name="main-menu", press=START, repeat=True, ref="evidence/02-menu.png",
         box=(60, 120, 200, 185), timeout=3000),
    dict(name="name-entry", press=CIRCLE, repeat=False, ref="evidence/04-name-entry.png",
         box=(16, 88, 304, 222), timeout=600),
]


def req(port, proc, **k):
    """One request, one connection: the server closes after each reply."""
    end = time.time() + 30
    while True:
        try:
            s = socket.create_connection(("127.0.0.1", port), timeout=2)
            break
        except OSError:
            if proc.poll() is not None:
                raise RuntimeError("runtime exited with code %s" % proc.returncode)
            if time.time() > end:
                raise RuntimeError("debug server not reachable on port %d" % port)
            time.sleep(0.25)
    with s:
        s.settimeout(40)       # the server waits up to 30 s for the emu thread
        s.sendall((json.dumps(k) + "\n").encode())
        buf = b""
        while not buf.endswith(b"\n"):
            c = s.recv(65536)
            if not c:
                break
            buf += c
    return json.loads(buf) if buf.strip() else {}


def mismatch(img, ref, box):
    """Fraction of pixels in box whose luma > LUM state differs; 1.0 if sizes differ."""
    if img.size != ref.size:
        return 1.0
    lut = [0] * (LUM + 1) + [255] * (255 - LUM)
    a, b = (i.crop(box).convert("L").point(lut) for i in (img, ref))
    return ImageChops.difference(a, b).histogram()[255] / ((box[2] - box[0]) * (box[3] - box[1]))


def run_step(port, proc, step, run, out):
    """Returns (ok, frame, message)."""
    ref = Image.open(os.path.join(ROOT, step["ref"])).convert("RGB")
    shot = os.path.join(run, "poll.png")
    f0 = req(port, proc, cmd="frame")["frame"]
    last, img, d = None, None, 1.0
    wall_end = time.time() + WALL_CAP
    while True:
        f = req(port, proc, cmd="frame")["frame"]
        if last is None or (step["repeat"] and f - last >= GAP):
            req(port, proc, cmd="press", buttons="0x%04X" % step["press"], frames=HOLD)
            last = f
        r = req(port, proc, cmd="screenshot_file", path=shot)
        if r.get("ok"):                       # not ok while the display is disabled
            img = Image.open(shot).convert("RGB")
            d = mismatch(img, ref, step["box"])
            if d <= TOL:
                return True, f, "diff=%.4f" % d
        if f - f0 > step["timeout"] or time.time() > wall_end:
            msg = "no match within %d frames (last diff=%.4f, size=%s)" % (
                f - f0, d, "%dx%d" % img.size if img else "none")
            if img:
                p = os.path.join(out, "FAIL-%s.png" % step["name"])
                img.save(p)
                msg += "; screenshot: " + p
            return False, f, msg
        time.sleep(0.02)


def telemetry(run):
    try:
        r = json.load(open(os.path.join(run, "psx_last_run_report.json")))
    except (OSError, ValueError) as e:
        return "telemetry: unavailable (%s)" % e
    iu = r.get("interp_unsupported", {})
    return ("telemetry: frame=%s autocompile_degraded=%s interp_unsupported.midblock_count=%s "
            "pc=%s reason=%s dispatch_depth=%s exit_origin=%s" % (
                r.get("frame"), r.get("autocompile_degraded"), iu.get("midblock_count"),
                iu.get("pc"), iu.get("reason"), r.get("dispatch_depth"), r.get("exit_origin")))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--port", type=int, default=4372)
    ap.add_argument("--disc", default=os.environ.get("TOD_DISC") or os.path.join(
        ROOT, "..", "isos", "Tales of Destiny (USA)", "Tales of Destiny (USA).cue"))
    ap.add_argument("--out", default=os.path.join(tempfile.gettempdir(), "tod-replay"))
    a = ap.parse_args()
    exe, disc, out = os.path.join(ROOT, "build", "psx_runtime"), os.path.abspath(a.disc), os.path.abspath(a.out)
    for p in (exe, disc):
        if not os.path.exists(p):
            sys.exit("replay: missing " + p)
    with socket.socket() as s:                # never drive somebody else's runtime
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   # TIME_WAIT from a previous run is not "in use"
        try:
            s.bind(("127.0.0.1", a.port))
        except OSError:
            sys.exit("replay: port %d is already in use" % a.port)
    os.makedirs(out, exist_ok=True)
    run = tempfile.mkdtemp(prefix="run-", dir=out)
    os.mkdir(os.path.join(run, "memcard"))
    log = open(os.path.join(run, "run.log"), "w")
    proc = subprocess.Popen(
        [exe, "--game", os.path.join(ROOT, "game.toml"), "--disc", disc, "--headless",
         "--debug-port", str(a.port), "--memcard-dir", os.path.join(run, "memcard")],
        cwd=run, env=dict(os.environ, PSX_DEBUG_SERVER="1"), stdout=log, stderr=subprocess.STDOUT)
    passed = 0
    try:
        for step in STEPS:
            try:
                ok, f, msg = run_step(a.port, proc, step, run, out)
            except (RuntimeError, OSError, ValueError, KeyError) as e:
                ok, f, msg = False, -1, "error: %s" % e
            print("%s  %-12s frame=%d  %s" % ("PASS" if ok else "FAIL", step["name"], f, msg), flush=True)
            if not ok:
                break
            passed += 1
        try:    # game text the interpreter ran instead of recompiled code (physical PCs)
            r = req(a.port, proc, cmd="dirty_ram_stats", lo="0xA0000", hi="0x1B9800")
            rows = r.get("per_pc", [])
            print("interpreted game text: %d blocks, %d instructions%s" % (
                len(rows), sum(x.get("insns", 0) for x in rows),
                "".join(" %s" % x.get("pc") for x in rows[:16])), flush=True)
        except (RuntimeError, OSError, ValueError, KeyError) as e:
            print("interpreted game text: unavailable (%s)" % e, flush=True)
    finally:
        proc.terminate()
        try:
            proc.wait(15)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        log.close()
    print(telemetry(run))
    print("replay: %d/%d steps passed" % (passed, len(STEPS)))
    if passed == len(STEPS):
        shutil.rmtree(run, ignore_errors=True)
        return 0
    print("replay: run dir kept: " + run)
    return 1


if __name__ == "__main__":
    sys.exit(main())

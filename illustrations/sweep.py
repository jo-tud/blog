#!/usr/bin/env python3
"""Parameter sweeps on Replicate image models, for the blog's illustrations.

The idea: take an unusual model and push its parameters far past the usual
range (e.g. classifier-free guidance of 30-50 instead of 5-11), then pick
single images or build collages from the results. Every image is saved with
a JSON file holding the model version, prompt, all inputs and the seed, so
each published illustration can state exactly how it was made.

Setup: put REPLICATE_API_TOKEN=... into illustrations/.env (ignored by git).
Raw runs go to illustrations/runs/ (also ignored); only selected images are
copied to static/images/.

Usage:
    # Show a model's inputs, with defaults and allowed ranges
    python illustrations/sweep.py schema stability-ai/sdxl

    # Sweep: every combination of the --sweep values and --seeds
    python illustrations/sweep.py run stability-ai/sdxl \\
        --prompt "a containment argument, abstract" \\
        --set num_inference_steps=20 \\
        --sweep guidance_scale=15,30,50 --seeds 1,2,3 --max 12

    # Contact sheet for a finished run
    python illustrations/sweep.py contact illustrations/runs/<run>
"""

import argparse
import itertools
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs"
API = "https://api.replicate.com/v1"
FONT = HERE.parent / "static" / "fonts" / "IBMPlexMono-Regular.ttf"
# Replicate sits behind Cloudflare, which rejects the default Python-urllib user agent
USER_AGENT = "sparserewards-illustrations/1.0"


def token():
    tok = os.environ.get("REPLICATE_API_TOKEN")
    env = HERE / ".env"
    if not tok and env.exists():
        for line in env.read_text().splitlines():
            key, _, val = line.partition("=")
            if key.strip() == "REPLICATE_API_TOKEN":
                tok = val.strip().strip('"').strip("'")
    if not tok:
        sys.exit("No REPLICATE_API_TOKEN (environment or illustrations/.env).")
    return tok


def api(method, path, body=None, wait=False):
    url = path if path.startswith("http") else API + path
    req = urllib.request.Request(url, method=method,
                                 data=json.dumps(body).encode() if body is not None else None)
    req.add_header("Authorization", f"Bearer {token()}")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", USER_AGENT)
    if wait:
        req.add_header("Prefer", "wait=60")
    for attempt in range(10):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")
            if e.code == 429:
                # Throttled (e.g. 6 predictions/minute while the account has < $5 credit)
                try:
                    wait_s = int(json.loads(detail).get("retry_after", 10))
                except ValueError:
                    wait_s = 10
                print(f"  rate limited, waiting {wait_s + 1} s")
                time.sleep(wait_s + 1)
                continue
            sys.exit(f"{method} {url}: HTTP {e.code}: {detail[:500]}")
    sys.exit(f"{method} {url}: still rate limited after 10 attempts")


def download(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as r:
        path.write_bytes(r.read())


def latest_version(model):
    info = api("GET", f"/models/{model}")
    version = info.get("latest_version") or {}
    if not version:
        sys.exit(f"{model}: no version found")
    return version


def input_schema(version):
    schemas = version.get("openapi_schema", {}).get("components", {}).get("schemas", {})
    return schemas.get("Input", {}).get("properties", {})


def parse_value(text):
    """'30' -> 30, '0.5' -> 0.5, 'true' -> True, anything else stays a string."""
    for cast in (int, float):
        try:
            return cast(text)
        except ValueError:
            pass
    return {"true": True, "false": False}.get(text.lower(), text)


def cmd_schema(args):
    version = latest_version(args.model)
    print(f"{args.model} @ {version['id']}\n")
    for name, spec in sorted(input_schema(version).items(), key=lambda kv: kv[1].get("x-order", 99)):
        bounds = [f"{k}={spec[k]}" for k in ("minimum", "maximum", "default") if k in spec]
        if "allOf" in spec or "enum" in spec:
            bounds.append("choices")
        print(f"  {name:28} {spec.get('type', ''):8} {' '.join(bounds)}")
        if spec.get("description"):
            print(f"  {'':28} {spec['description'][:100]}")


def cmd_run(args):
    version = latest_version(args.model)
    schema = input_schema(version)
    fixed = {"prompt": args.prompt} if args.prompt else {}
    for item in args.set or []:
        key, _, val = item.partition("=")
        fixed[key] = parse_value(val)
    sweep = {}
    for item in args.sweep or []:
        key, _, vals = item.partition("=")
        sweep[key] = [parse_value(v) for v in vals.split(",")]
    if args.seeds:
        sweep[args.seed_param] = [parse_value(v) for v in args.seeds.split(",")]

    for key in list(fixed) + list(sweep):
        if schema and key not in schema:
            sys.exit(f"{args.model} has no input '{key}'. See: sweep.py schema {args.model}")
        spec = schema.get(key, {})
        values = [fixed[key]] if key in fixed else sweep[key]
        for v in values:
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                if ("maximum" in spec and v > spec["maximum"]) or ("minimum" in spec and v < spec["minimum"]):
                    sys.exit(f"{key}={v} is outside {spec.get('minimum')}..{spec.get('maximum')} for {args.model}")

    keys = list(sweep)
    combos = [dict(zip(keys, vals)) for vals in itertools.product(*sweep.values())] or [{}]
    print(f"{len(combos)} image(s) planned with {args.model}")
    if len(combos) > args.max:
        sys.exit(f"That is more than --max {args.max}. Narrow the sweep or raise --max.")
    if args.dry_run:
        for c in combos:
            print("  ", c)
        return

    slug = re.sub(r"[^a-z0-9]+", "-", (args.name or args.model.split("/")[-1]).lower()).strip("-")
    run_dir = RUNS / f"{datetime.now():%Y-%m-%d-%H%M%S}-{slug}"
    run_dir.mkdir(parents=True)
    (run_dir / "run.json").write_text(json.dumps({
        "model": args.model, "version": version["id"], "fixed": fixed, "sweep": sweep,
        "started": datetime.now().isoformat(timespec="seconds")}, indent=2))

    total_time = 0.0
    for n, combo in enumerate(combos, 1):
        inputs = {**fixed, **combo}
        pred = api("POST", "/predictions", {"version": version["id"], "input": inputs}, wait=True)
        while pred.get("status") not in ("succeeded", "failed", "canceled"):
            time.sleep(2)
            pred = api("GET", pred["urls"]["get"])
        label = ", ".join(f"{k}={v}" for k, v in combo.items())
        if pred["status"] != "succeeded":
            print(f"[{n}/{len(combos)}] {label}: {pred['status']} {pred.get('error') or ''}")
            continue
        outputs = pred["output"] if isinstance(pred["output"], list) else [pred["output"]]
        files = []
        for i, url in enumerate(outputs):
            ext = Path(url.split("?")[0]).suffix or ".png"
            name = f"{n:03d}" + (f"-{i}" if len(outputs) > 1 else "") + ext
            download(url, run_dir / name)
            files.append(name)
        seconds = (pred.get("metrics") or {}).get("predict_time") or 0
        total_time += seconds
        (run_dir / f"{n:03d}.json").write_text(json.dumps({
            "model": args.model, "version": version["id"], "input": inputs, "varied": combo,
            "files": files, "prediction": pred["id"], "predict_time": seconds}, indent=2))
        print(f"[{n}/{len(combos)}] {label}: {', '.join(files)} ({seconds:.1f} s)")

    print(f"\n{run_dir}\nGPU time: {total_time:.0f} s (see replicate.com/account for the cost)")
    make_contact_sheet(run_dir)


def make_contact_sheet(run_dir, thumb=320):
    from PIL import Image, ImageDraw, ImageFont
    entries = []
    for meta_file in sorted(run_dir.glob("[0-9][0-9][0-9].json")):
        meta = json.loads(meta_file.read_text())
        for f in meta["files"]:
            if Path(f).suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"):
                label = "\n".join([Path(f).stem] + [f"{k}={v}" for k, v in meta["varied"].items()])
                entries.append((run_dir / f, label))
    if not entries:
        return
    cols = min(4, len(entries))
    rows = -(-len(entries) // cols)
    pad = 12
    text_h = 8 + 15 * max(label.count("\n") + 1 for _, label in entries)
    sheet = Image.new("RGB", (cols * (thumb + pad) + pad, rows * (thumb + text_h + pad) + pad), "#e9e9e4")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(str(FONT), 12) if FONT.exists() else ImageFont.load_default()
    for i, (path, label) in enumerate(entries):
        img = Image.open(path).convert("RGB")
        img.thumbnail((thumb, thumb))
        x = pad + (i % cols) * (thumb + pad)
        y = pad + (i // cols) * (thumb + text_h + pad)
        sheet.paste(img, (x, y))
        draw.multiline_text((x, y + thumb + 4), label, fill="#56564f", font=font, spacing=3)
    out = run_dir / "contact.jpg"
    sheet.save(out, quality=90)
    print(f"Contact sheet: {out}")


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("schema", help="show a model's inputs")
    s.add_argument("model", help="owner/name on Replicate")
    r = sub.add_parser("run", help="run a parameter sweep")
    r.add_argument("model", help="owner/name on Replicate")
    r.add_argument("--prompt")
    r.add_argument("--set", action="append", metavar="KEY=VALUE", help="fixed input (repeatable)")
    r.add_argument("--sweep", action="append", metavar="KEY=V1,V2", help="varied input (repeatable)")
    r.add_argument("--seeds", help="comma-separated seeds")
    r.add_argument("--seed-param", default="seed", help="name of the model's seed input")
    r.add_argument("--name", help="name for the run folder")
    r.add_argument("--max", type=int, default=12, help="refuse sweeps with more images (default 12)")
    r.add_argument("--dry-run", action="store_true", help="only list the planned combinations")
    c = sub.add_parser("contact", help="(re)build the contact sheet of a run")
    c.add_argument("run_dir", type=Path)
    args = p.parse_args()
    if args.cmd == "schema":
        cmd_schema(args)
    elif args.cmd == "run":
        cmd_run(args)
    else:
        make_contact_sheet(args.run_dir)


if __name__ == "__main__":
    main()

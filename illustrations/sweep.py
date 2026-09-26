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

Per post (the normal workflow):
    # 1. A contact sheet of 12 variations from the presets that have worked so far
    python illustrations/sweep.py post hubris-without-a-mind --prompt "hubris"
    # 2. Pick 0-3 favourites by number; they go to static/images/<slug>/ with a caption
    python illustrations/sweep.py select illustrations/runs/hubris-without-a-mind/<run> 004 007
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
IMAGES = HERE.parent / "static" / "images"
MAX_PER_POST = 3  # never more illustrations than this in one post

# Settings that produced usable images in the first experiments (2026-09-26).
# Few steps with high guidance make the model break down in different ways per sampler.
POST_MODEL = "stability-ai/sdxl"
POST_PRESETS = [
    {"scheduler": "K_EULER", "guidance_scale": 25, "num_inference_steps": 10},           # calm, architectural
    {"scheduler": "K_EULER", "guidance_scale": 25, "num_inference_steps": 15},           # illustrative, darker
    {"scheduler": "DDIM", "guidance_scale": 50, "num_inference_steps": 4},               # shards, lone figures
    {"scheduler": "K_EULER_ANCESTRAL", "guidance_scale": 50, "num_inference_steps": 5},  # blurs, points of light
]
POST_FIXED = {"width": 1024, "height": 1024, "disable_safety_checker": True}
MODEL_NAMES = {"stability-ai/sdxl": "SDXL", "stability-ai/stable-diffusion": "Stable Diffusion"}


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
    execute(args.model, version, fixed, combos, RUNS / f"{datetime.now():%Y-%m-%d-%H%M%S}-{slug}",
            {"fixed": fixed, "sweep": sweep})


def execute(model, version, fixed, combos, run_dir, plan):
    """Run one prediction per combination, save images with their metadata, build the contact sheet."""
    run_dir.mkdir(parents=True)
    (run_dir / "run.json").write_text(json.dumps({
        "model": model, "version": version["id"], **plan,
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
            "model": model, "version": version["id"], "input": inputs, "varied": combo,
            "files": files, "prediction": pred["id"], "predict_time": seconds}, indent=2))
        print(f"[{n}/{len(combos)}] {label}: {', '.join(files)} ({seconds:.1f} s)")

    print(f"\n{run_dir}\nGPU time: {total_time:.0f} s (see replicate.com/account for the cost)")
    make_contact_sheet(run_dir)


def cmd_post(args):
    """The standard contact sheet for one post: every preset with every seed."""
    slug = re.sub(r"[^a-z0-9]+", "-", args.slug.lower()).strip("-")
    seeds = [int(x) for x in args.seeds.split(",")]
    combos = [{**preset, "seed": seed} for preset in POST_PRESETS for seed in seeds]
    fixed = {"prompt": args.prompt, **POST_FIXED}
    print(f"{len(combos)} image(s) planned for '{slug}' with {POST_MODEL}")
    if args.dry_run:
        for c in combos:
            print("  ", c)
        return
    version = latest_version(POST_MODEL)
    execute(POST_MODEL, version, fixed, combos, RUNS / slug / f"{datetime.now():%Y-%m-%d-%H%M%S}",
            {"post": slug, "fixed": fixed, "presets": POST_PRESETS, "seeds": seeds})


def caption(meta):
    """One line saying how the image was made, e.g. 'SDXL · "hubris" · CFG 25 · 10 steps · K_EULER · seed 1'."""
    inp = meta["input"]
    parts = [MODEL_NAMES.get(meta["model"], meta["model"])]
    if inp.get("prompt"):
        parts.append(f"“{inp['prompt']}”")
    if "guidance_scale" in inp:
        parts.append(f"CFG {inp['guidance_scale']:g}")
    if "num_inference_steps" in inp:
        parts.append(f"{inp['num_inference_steps']} steps")
    if inp.get("scheduler"):
        parts.append(inp["scheduler"])
    if "seed" in inp:
        parts.append(f"seed {inp['seed']}")
    return " · ".join(parts)


def cmd_select(args):
    """Copy chosen images of a run into static/images/<slug>/ and print the Markdown for the post."""
    from PIL import Image
    run_dir = args.run_dir.resolve()
    plan = json.loads((run_dir / "run.json").read_text())
    slug = args.post or plan.get("post")
    if not slug:
        sys.exit("Which post? Use --post <slug> (runs made with 'post' know it already).")
    target = IMAGES / slug
    existing = sorted(target.glob("*.jpg")) if target.exists() else []
    if len(existing) + len(args.numbers) > MAX_PER_POST:
        sys.exit(f"'{slug}' would have {len(existing) + len(args.numbers)} illustrations; "
                 f"the limit is {MAX_PER_POST}. Remove some from {target} first.")
    target.mkdir(parents=True, exist_ok=True)
    for number in args.numbers:
        meta = json.loads((run_dir / f"{int(number):03d}.json").read_text())
        src = run_dir / meta["files"][0]
        index = len(sorted(target.glob("*.jpg"))) + 1
        dest = target / f"{index}.jpg"
        Image.open(src).convert("RGB").save(dest, quality=88, optimize=True, progressive=True)
        (target / f"{index}.json").write_text(json.dumps({**meta, "source_run": run_dir.name}, indent=2))
        alt = args.alt or "Illustration"
        print(f'![{alt}](/static/images/{slug}/{index}.jpg "{caption(meta)}")')
    print(f"\nCopied to {target}. Paste the line(s) above into the post; the title becomes the caption.")


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
    po = sub.add_parser("post", help="standard contact sheet for one post (presets x seeds)")
    po.add_argument("slug", help="the post's slug, e.g. hubris-without-a-mind")
    po.add_argument("--prompt", required=True, help="usually one word from the post")
    po.add_argument("--seeds", default="1,2,3")
    po.add_argument("--dry-run", action="store_true")
    se = sub.add_parser("select", help=f"take 0-{MAX_PER_POST} favourites from a run into the post")
    se.add_argument("run_dir", type=Path)
    se.add_argument("numbers", nargs="+", help="image numbers from the contact sheet, e.g. 004 007")
    se.add_argument("--post", help="slug (only needed for runs not made with 'post')")
    se.add_argument("--alt", help="alt text for screen readers")
    args = p.parse_args()
    {"schema": cmd_schema, "run": cmd_run, "post": cmd_post, "select": cmd_select,
     "contact": lambda a: make_contact_sheet(a.run_dir)}[args.cmd](args)


if __name__ == "__main__":
    main()

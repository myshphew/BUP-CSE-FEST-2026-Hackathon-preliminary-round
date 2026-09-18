"""Render the solution video from recorded local evidence; no API calls or secrets.

Windows-only narration uses the installed Microsoft David voice. Media packages
are optional authoring tools in tmp/media-tools, never runtime dependencies.
"""

import json
import os
import subprocess
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tmp/media-tools"))
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

OUT = ROOT / "output/submission/1.0.1"
FRAMES = OUT / "video-assets"
FRAMES.mkdir(parents=True, exist_ok=True)
sample = json.loads((OUT / "sample-01-response.json").read_text())
benchmark = json.loads((ROOT / "docs/audit-verification.json").read_text())
live = benchmark["docker_http"]
assert live["passed"] == live["total"] == 30
assert abs(sample["total_cost_bdt"] - 38365) < 0.01

W, H = 1920, 1080
BG, PANEL, WHITE, MUTED, GREEN, CYAN = "#091522", "#132637", "#f1f6fb", "#a9bdcd", "#65e0b1", "#70cbff"
FONT = Path(os.environ["WINDIR"]) / "Fonts"


def font(size, bold=False, mono=False):
    return ImageFont.truetype(str(FONT / ("consola.ttf" if mono else "segoeuib.ttf" if bold else "segoeui.ttf")), size)


def text(draw, xy, value, size=34, fill=WHITE, bold=False, mono=False):
    draw.text(xy, value, font=font(size, bold, mono), fill=fill, spacing=12)


def wrap(draw, value, x, y, width, size=34, fill=WHITE, bold=False):
    words, line = value.split(), ""
    for word in words:
        candidate = (line + " " + word).strip()
        if draw.textlength(candidate, font=font(size, bold)) > width and line:
            text(draw, (x, y), line, size, fill, bold)
            y += int(size * 1.5)
            line = word
        else:
            line = candidate
    if line:
        text(draw, (x, y), line, size, fill, bold)
    return y + int(size * 1.5)


def card(draw, box):
    draw.rounded_rectangle(box, radius=24, fill=PANEL)


def base(index, title, subtitle):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 8), fill=GREEN)
    text(d, (80, 42), "GRIDWISE  /  BUP CSE FEST 2026", 27, GREEN, True)
    text(d, (80, 119), title, 66, WHITE, True)
    wrap(d, subtitle, 84, 219, 1750, 31, MUTED)
    d.line((80, 993, 1840, 993), fill="#274053", width=2)
    text(d, (82, 1015), "Smart Campus Energy Optimization  |  Version 1.0.1 candidate | verified container execution", 24, MUTED)
    text(d, (1740, 1012), f"0{index} / 07", 28, GREEN)
    return im, d


narrations = [
    "GridWise turns twenty four hours of demand, solar forecasts, electricity tariffs, a battery, and operator notes into a valid minimum cost plan. Correctness comes first. Every operational instruction must be interpreted and applied, every hour must balance, and the battery must return to its initial energy at day end. Our objective is the campus electricity bill, not model token cost.",
    "The architecture separates language from mathematics. OpenAI Terra interprets all notes in one structured response. Deterministic Python guardrails validate note mappings, types, hours, and numeric bounds. CBC solves the resulting linear program. A separate validator reconstructs the rules and replays every returned hour. The language model never calculates schedules, battery trajectories, totals, or bills.",
    "This example is an actual version one point zero point one container response using the unchanged official sample. Panel cleaning leaves twenty five percent of forecast solar between noon and two PM. That means hours twelve and thirteen, factor zero point two five. The unrelated registration note becomes no operation. Validation rejects invented fields or invalid directives; provider failure is never silently changed into no operation.",
    "The first linear program proves the minimum electricity cost. A second solve keeps that bill fixed and minimizes peak grid import among equally cheap schedules. For sample one, peak import falls from one hundred eighty seven point five to one hundred seventy five kilowatt-hours, while the bill remains thirty eight thousand three hundred sixty five taka. Hard constraints and independent replay remain mandatory. If optional refinement fails, the proven primary optimum is retained.",
    "All two hundred forty three tests passed on Windows and inside Linux Docker. The official minimum costs still match in all ten cases. Independent dynamic programming checks additional directive combinations. Thirty uncached real model requests passed, and all ten cases also passed with up to eight concurrent requests. Terra with no reasoning, Terra with low reasoning, and Sol with low reasoning each passed fifty six language checks. These finite tests cannot prove hidden-case perfection.",
    "Docker runs the API as an unprivileged user. Credentials are injected only at runtime. The README supplies exact pull and run commands, a health check, and an official sample command. The returned sample one plan contains twenty four independently verified rows. Errors contain fixed safe messages. One short retry can recover a transient provider failure within the existing deadline; invalid credentials and insufficient quota are not retried.",
    "The candidate uses Terra with low reasoning and a normal cache of one hundred twenty eight successful interpretations. Uncached container p ninety five was two point six seven seconds. Low reasoning is a measured option, not a promise of perfect language understanding. The exact image and verification reports support reproducibility. Free hosting can sleep after inactivity, so continuous availability and accessible submission artifacts still matter during judging."
]

images = []
im, d = base(1, "A valid plan. Then the lowest cost.", "24 hours of campus energy, interpreted and optimized in one API request.")
for i, (big, small) in enumerate([("24 hours", "Demand + solar + tariffs"), ("1–3 notes", "Real language interpretation"), ("0.01", "kWh / BDT verification tolerance")]):
    x = 80 + i * 595
    card(d, (x, 350, x + 565, 570))
    text(d, (x + 32, 382), big, 59, GREEN, True)
    wrap(d, small, x + 32, 477, 510, 29, MUTED)
card(d, (80, 620, 1840, 905))
text(d, (120, 660), "Objective", 31, CYAN, True)
text(d, (120, 719), "Minimize the daily grid electricity bill", 48, WHITE, True)
text(d, (120, 804), "Honor every valid directive, every physical limit, and end-of-day neutrality.", 32, MUTED)
images.append(im)

im, d = base(2, "Language → guardrails → optimization", "Each stage has one responsibility. Every returned schedule passes independent replay.")
stages = [("01", "OpenAI", "Interpret notes"), ("02", "Validator", "Check structured data"), ("03", "CBC solver", "Minimize grid cost"), ("04", "Replay", "Verify every hour")]
for i, (n, label, detail) in enumerate(stages):
    x = 80 + i * 450
    card(d, (x, 355, x + 410, 640))
    text(d, (x + 28, 387), n, 34, GREEN, True)
    text(d, (x + 28, 456), label, 43, WHITE, True)
    wrap(d, detail, x + 28, 539, 354, 28, MUTED)
    if i < 3:
        text(d, (x + 416, 461), "→", 37, CYAN)
text(d, (90, 713), "Supported semantics", 33, CYAN, True)
wrap(d, "Solar reduction • minimum battery reserve • no-charge window • no-discharge window • maximum grid window • no operation", 90, 778, 1710, 36)
images.append(im)

im, d = base(3, "An official note, interpreted precisely", "SAMPLE-01  |  Actual output from the local production container and real OpenAI API")
card(d, (80, 340, 910, 910)); card(d, (950, 340, 1840, 910))
text(d, (115, 381), "Operator note", 31, CYAN, True)
wrap(d, "Facilities will wash the rooftop solar panels from noon until 2 PM. During cleaning, usable solar should be treated as roughly 25% of the forecast.", 115, 453, 750, 37)
text(d, (990, 381), "Validated interpretation", 31, GREEN, True)
text(d, (990, 458), 'type:   solar_reduction\nhours:  [12, 13]\nfactor: 0.25\napplies: true', 34, WHITE, mono=True)
wrap(d, "Registration deadline note → no_op; adjustment = null; applies = false.", 990, 724, 790, 31, MUTED)
images.append(im)

im, d = base(4, "Deterministic optimization and replay", "The LLM supplies meaning. Application code supplies every flow, state, total, and cost.")
card(d, (80, 343, 1040, 923)); card(d, (1080, 343, 1840, 923))
text(d, (120, 382), "LINEAR PROGRAM", 29, GREEN, True)
for y, formula in [(455, "minimize  Σ tariff[h] × grid[h]"), (537, "grid + solar = demand + battery flow"), (619, "energy[h] = energy[h−1] + flow[h]"), (701, "energy[23] = initial energy")]:
    text(d, (120, y), formula, 34)
wrap(d, "Bounds enforce solar, battery capacity, rates, reserves, windows, and grid caps.", 120, 800, 850, 29, MUTED)
text(d, (1120, 382), "COST FIRST, THEN PEAK", 28, CYAN, True)
for y, line in [(461, "Fix the proven minimum bill"), (543, "Then minimize peak import"), (625, "SAMPLE-01: 187.5 → 175 kWh"), (707, "Unchanged cost: 38,365 BDT")]:
    text(d, (1120, y), line, 32)
text(d, (1120, 819), "Overlap rules + replay still enforced", 28, GREEN, True)
images.append(im)

im, d = base(5, "Measured correctness, with real model calls", "Official inputs remain unchanged. Live and offline verification are reported separately.")
for i, (value, label) in enumerate([("243 / 243", "Linux Docker tests"), ("10 / 10", "Official optimal costs"), ("30 / 30", "Uncached live HTTP cases")]):
    x = 80 + i * 595; card(d, (x, 345, x + 565, 560))
    text(d, (x + 31, 379), value, 57, GREEN, True)
    text(d, (x + 31, 475), label, 29, MUTED)
card(d, (80, 607, 1840, 916))
text(d, (120, 648), "Each official request checks:", 35, CYAN, True)
text(d, (120, 717), "Interpretation semantics  •  all 24 hourly constraints  •  reference optimal cost", 34)
text(d, (120, 789), "56 live language checks per model profile; independent DP cost oracles", 32)
text(d, (120, 855), "Finite local evidence; hidden-note accuracy and hosted latency require separate evaluation.", 27, MUTED)
images.append(im)

im, d = base(6, "Run the same service in Docker", "Recorded 1.0.1 container evidence  |  secrets are injected at runtime and excluded from the image")
card(d, (80, 340, 1040, 923)); card(d, (1080, 340, 1840, 923))
text(d, (120, 381), "START + VERIFY", 29, GREEN, True)
text(d, (120, 454), 'docker compose up -d --build --wait\n\nGET /health\n200  {"status": "ok"}\n\nPOST /optimize-energy\n200  application/json', 32, WHITE, mono=True)
text(d, (1120, 381), "SAMPLE-01 RESPONSE", 29, CYAN, True)
text(d, (1120, 458), "38,365 BDT", 61, GREEN, True)
text(d, (1120, 559), "24 rows | peak 175 kWh", 35)
wrap(d, "Real model interpretation. Independently verified energy balance and optimal cost.", 1120, 644, 655, 32, MUTED)
wrap(d, "Non-root UID 10001 • healthy container • no baked-in .env", 1120, 808, 655, 28, MUTED)
images.append(im)

im, d = base(7, "Ready for reproducible deployment", "A measured model profile, explicit configuration, and a deterministic scheduling core.")
card(d, (80, 345, 760, 910)); card(d, (800, 345, 1840, 910))
text(d, (120, 390), f"{live['p95_seconds']:.3f} s", 89, GREEN, True)
text(d, (120, 514), "Uncached container p95", 34)
text(d, (120, 593), f"Maximum: {live['max_seconds']:.3f} s", 31, MUTED)
wrap(d, "30 real requests; OpenAI Terra / low. Application cache = 0 during measurement.", 120, 690, 590, 31, MUTED)
text(d, (840, 391), "Production profile", 34, CYAN, True)
text(d, (840, 465), "gpt-5.6-terra  /  low", 42, WHITE, True)
text(d, (840, 548), "INTERPRETATION_CACHE_SIZE=128", 34, WHITE, mono=True)
wrap(d, "Keep the cost optimum; reduce peak among equal-cost plans. Verify availability and judge access. Free hosting may sleep after idle.", 840, 650, 910, 34, MUTED)
text(d, (840, 846), "Code + README + tests + Docker + this video", 30, GREEN, True)
images.append(im)

manifest = []
for i, (im, narration) in enumerate(zip(images, narrations), 1):
    im.save(FRAMES / f"scene-{i:02}.png")
    manifest.append({"audio": str(FRAMES / f"scene-{i:02}.wav"), "narration": narration})
(FRAMES / "narration.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden", "-File",
                str(Path(__file__).with_name("narrate.ps1")), "-Manifest", str(FRAMES / "narration.json")], check=True, creationflags=flags)
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
durations, clips = [], []
for item in manifest:
    with wave.open(item["audio"], "rb") as wav:
        duration = wav.getnframes() / wav.getframerate() + 1.2
    durations.append(duration)
assert sum(durations) < 180, "Video exceeds the organizer's three-minute maximum"
for i, (item, duration) in enumerate(zip(manifest, durations), 1):
    clip = FRAMES / f"scene-{i:02}.mp4"
    command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-loop", "1", "-framerate", "24", "-i",
               str(FRAMES / f"scene-{i:02}.png"), "-i", item["audio"], "-t", str(duration), "-vf", "format=yuv420p",
               "-c:v", "libx264", "-preset", "fast", "-tune", "stillimage", "-crf", "21", "-c:a", "aac", "-b:a", "128k",
               "-af", "apad", "-movflags", "+faststart", str(clip)]
    subprocess.run(command, check=True, creationflags=flags)
    clips.append(clip)
    print(f"Rendered scene {i}/7 ({duration:.1f}s)", flush=True)
assert sum(durations) < 180, "Video exceeds the organizer's three-minute maximum"
concat = FRAMES / "concat.txt"
concat.write_text("\n".join(f"file '{p.name}'" for p in clips), encoding="utf-8")
target = OUT / "gridwise-solution.mp4"
subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
                "-c", "copy", "-movflags", "+faststart", str(target)], check=True, creationflags=flags)
(OUT / "video-metadata.json").write_text(json.dumps({"duration_seconds":sum(durations),"resolution":"1920x1080", "fps":24,
    "narration":"Microsoft David Desktop synthetic voice", "evidence":"Recorded 1.0.1 Docker HTTP responses and actual audit results",
    "public_deployment_claimed":False}, indent=2) + "\n")
transcript = "# Solution video transcript\n\nNarration is synthesized using the installed Microsoft David voice. API examples are recorded version 1.0.1 container results; they are not a hosted 1.0.1 benchmark.\n\n"
for i, paragraph in enumerate(narrations, 1):
    transcript += f"## Scene {i}\n\n{paragraph}\n\n"
Path(__file__).with_name("TRANSCRIPT.md").write_text(transcript, encoding="utf-8")
sheet = Image.new("RGB", (960 * 2, 540 * 4), BG)
for i, im in enumerate(images):
    sheet.paste(im.resize((960,540)), ((i%2)*960, (i//2)*540))
sheet.save(FRAMES / "contact-sheet.png")
print(json.dumps({"video":str(target),"duration_seconds":round(sum(durations),2)}), flush=True)

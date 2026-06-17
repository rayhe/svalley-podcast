#!/usr/bin/env python3
"""AI Steve + AI Jensen podcast on the Livermore rodeo.
   Steve = design/vision/UX (Jobs-like). Jensen = GPU/AI/scale (Huang-like)."""

import os
import subprocess
import tempfile

ENV_FILE = os.path.expanduser("~/.openclaw/agents/main/agent/elevenlabs.env")
OUT_DIR  = "/Users/jerclaw/.openclaw/workspace/.cache/podcast"
os.makedirs(OUT_DIR, exist_ok=True)

with open(ENV_FILE) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v

VOICE_STEVE  = os.environ["ELEVENLABS_VOICE_STEVE"]
VOICE_JENSEN = os.environ["ELEVENLABS_VOICE_JENSEN"]

# (voice_id, rate, text)
LINES = [
    # Intro
    (VOICE_JENSEN, 165, "Welcome to The Physical AI Hour. A podcast about America, by two of us who got lost on the way to a CES keynote."),
    (VOICE_STEVE,  165, "Steve."),
    (VOICE_JENSEN, 160, "Jensen."),
    (VOICE_STEVE,  180, "Today, the Livermore rodeo."),
    (VOICE_JENSEN, 155, "The more you watch, the more you save."),
    (VOICE_STEVE,  175, "Think different."),
    # Steve opens
    (VOICE_STEVE,  170, "Look — there's something the industry has been missing. A rodeo is the original product launch. The cowboys ship to a hostile audience every weekend. No beta. No A-B test. Just a bull, and eight seconds."),
    (VOICE_STEVE,  170, "Bull riding. Insanely great. The bull is the problem. The cowboy is the solution. The crowd is the press. The whole thing has been in beta for a hundred and fifty years."),
    # Jensen responds
    (VOICE_JENSEN, 160, "Steve. Love the framing. But you forgot the most important part. The bull is a GPU. Two thousand pounds of compute. The cowboy is running inference on a moving platform, and the SLA is his life. This is the iPhone moment of rodeo."),
    (VOICE_JENSEN, 160, "Bull riding. Ten out of ten. The cowboy is running a transformer on a bull. Real-time inference. No cloud. No datacenters. Just a man, a rope, and a hat. This is edge AI at its finest."),
    # Quick ratings
    (VOICE_STEVE,  180, "Mutton bustin'. The kids get on the sheep. The sheep does not want them. This is the entire Apple product line. Beautiful design. The customer has not quite figured out they need it yet."),
    (VOICE_JENSEN, 165, "Mutton bustin'. Ten out of ten. The sheep is the GPU. The kid is the kernel. The whole thing is compute at the edge. The more sheep, the more you save."),
    # The disagreement
    (VOICE_JENSEN, 150, "Steer wrestling. Four out of ten. A two-hundred-pound man tackling a six-hundred-pound steer. The math does not scale. Single-node operation. No distributed training. It will not work in a datacenter."),
    (VOICE_STEVE,  180, "Jensen. I respect the steer wrestler. He has clearly studied design. I can tell by the way he grabs the horns. The unit economics are his career. Some products ship without a roadmap. Some products are the roadmap."),
    (VOICE_JENSEN, 145, "Steve. That is not a product. That is a lawsuit."),
    # Closing
    (VOICE_STEVE,  180, "Go to the rodeo. Tip the mutton-bustin' parents. Pet a horse. And remember — in America, the bull is just a product you have not shipped yet."),
    (VOICE_JENSEN, 150, "Long-term, I am bullish on rodeo. The bull is just a GPU with horns. The more rodeos, the more you save."),
    (VOICE_STEVE,  175, "Think different."),
    (VOICE_JENSEN, 155, "Buy more, save more."),
]

# Synthesize each line
temp_dir = tempfile.mkdtemp(prefix="podcast_v7_")
mp3_files = []

for i, (voice, rate, text) in enumerate(LINES):
    out_path = os.path.join(temp_dir, f"line_{i:02d}.mp3")
    print(f"  {i+1:2d}/{len(LINES)}  voice={voice[:8]}.. @{rate}: {text[:60]}...")
    result = subprocess.run([
        "sag", "speak",
        "-v", voice,
        "-r", str(rate),
        "--model-id", "eleven_turbo_v2_5",
        "-o", out_path,
        text
    ], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  FAILED: {result.stderr[-300:]}")
        raise SystemExit(1)
    mp3_files.append(out_path)

# Concat → AAC m4a
concat_file = os.path.join(temp_dir, "concat.txt")
with open(concat_file, "w") as f:
    for af in mp3_files:
        f.write(f"file '{af}'\n")

final_path = os.path.join(OUT_DIR, "livermore_rodeo_podcast_v7.m4a")
result = subprocess.run([
    "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file,
    "-c:a", "aac", "-b:a", "128k", final_path
], capture_output=True, text=True)
if result.returncode != 0:
    print("FFMPEG STDERR:", result.stderr[-500:])
    raise SystemExit(1)

probe = subprocess.run([
    "ffprobe", "-v", "error", "-show_entries", "format=duration",
    "-of", "default=noprint_wrappers=1:nokey=1", final_path
], capture_output=True, text=True)

print(f"\nOK: {final_path}")
print(f"Size: {os.path.getsize(final_path):,} bytes")
print(f"Duration: {probe.stdout.strip()} seconds")

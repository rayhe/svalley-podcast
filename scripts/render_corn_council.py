#!/usr/bin/env python3
"""Corn Council: How Four Centi-Billionaires (and a fake Steve) Over-Optimize a Corn Decision.
   Voices: Steve Jobs (host), Jensen Huang, Mark Zuckerberg, Jeff B (Jeremy clone as Jeff Bezos), Bill G (Elon sub)."""

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

VOICE_STEVE  = os.environ["ELEVENLABS_VOICE_STEVE"]      # Steve Jobs clone (host)
VOICE_JENSEN = os.environ["ELEVENLABS_VOICE_JENSEN"]     # Jensen Huang clone
VOICE_MARK   = os.environ["ELEVENLABS_VOICE_MARK"]       # Mark Zuckerberg v2
VOICE_JEFF   = os.environ["ELEVENLABS_VOICE_JEFF"]       # Jeff B (Jeremy clone) standing in for Jeff Bezos
VOICE_BILLG  = "7uXYi4h2YXmavU1mNpgv"                    # Bill Gates clone

# (voice_id, rate, text, label)
LINES = [
    # Open - Steve (host)
    (VOICE_STEVE, 175, "Welcome to Corn Council. A podcast about groceries, by people who have never been to one.",                          "STEVE:open"),
    (VOICE_STEVE, 175, "I'm Steve. Today's topic: a Livermore man must choose between two grocery stores for corn. Six ears at Lucky for a dollar. Eight ears at Safeway for a dollar. He drives a 2017 Volvo XC90.",  "STEVE:setup"),
    # Jensen
    (VOICE_JENSEN, 155, "This is a compute problem. Two stores, two price points, two distances. The throughput favors Lucky. The memory bandwidth — ears per cubic foot of trunk — favors Safeway.",                "JENSEN:open"),
    (VOICE_JENSEN, 160, "But here's the thing. The more corn you buy, the more you save. Buy forty-eight ears. Buy a pallet. Vertical integration. We're not thinking big enough. This is the iPhone moment of corn.", "JENSEN:thesis"),
    # Mark
    (VOICE_MARK, 145, "Mm. We ran a model. He should buy the corn at whichever store has the better checkout experience. People like feeling fast. So Lucky. Done.",                                                 "MARK:thesis"),
    (VOICE_MARK, 150, "Also. Open source the corn protocol. Make the recipe a public good. Build a community.",                                                                                          "MARK:recipe"),
    # Jeff B standing in for Bezos
    (VOICE_JEFF, 165, "I have a different framework. What does the customer really want? He wants corn. So give him corn. It does not matter where. Forward. With bias for action. Also — I own a Volvo dealership, kind of. Buy from me.",  "JEFF:thesis"),
    (VOICE_JEFF, 170, "Long term, I am bullish on corn. I have been bullish on corn since two thousand and seven.",                                                                                       "JEFF:closing"),
    # Bill G subbing for Elon (Elon's voice clone was deleted from the ElevenLabs account)
    (VOICE_BILLG, 165, "The real question is not corn. It is whether humans are even meant to eat corn. I have funded two hundred and seventy million dollars of GMO research. I know the answer. The answer is yellow.",  "BILLG:thesis"),
    (VOICE_BILLG, 170, "Also. The corn is a distraction. The real product is the autonomous driving stack. The Volvo is already a robot. The corn is just payload. The car does not care. The car wants you to be free. The corn is irrelevant.",  "BILLG:distract"),
    # Fake Steve returns
    (VOICE_STEVE, 180, "One more thing.",                                                                                                                                                                "STEVE:omt"),
    (VOICE_STEVE, 180, "The corn is a lie. There is no corn. There is only the hunger. Buy the bigger bag. Trust your gut. Reality is malleable. The stores are inside you.",                          "STEVE:thesis"),
    (VOICE_STEVE, 185, "Jensen is right about one thing. You are not thinking big enough. The corn is the platform. The grocery store is the App Store. The Volvo is the developer kit. You are not buying corn. You are buying a future where corn is free.", "STEVE:platform"),
    (VOICE_STEVE, 190, "Think different.",                                                                                                                                                              "STEVE:tag"),
]

# Synthesize each line
temp_dir = tempfile.mkdtemp(prefix="corn_council_")
mp3_files = []
failures = []

for i, (voice, rate, text, label) in enumerate(LINES):
    out_path = os.path.join(temp_dir, f"line_{i:02d}.mp3")
    print(f"  {i+1:2d}/{len(LINES)}  voice={voice[:8]}.. @{rate}  [{label}]: {text[:60]}...")
    result = subprocess.run([
        "sag", "speak",
        "-v", voice,
        "-r", str(rate),
        "--model-id", "eleven_turbo_v2_5",
        "-o", out_path,
        text
    ], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  FAILED [{label}]: {result.stderr[-300:]}")
        failures.append((label, text, result.stderr[-300:]))
        # Use a 0.3s silence file as placeholder so the timing is preserved
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=channel_layout=mono:sample_rate=22050",
            "-t", "0.3", "-q:a", "9", out_path
        ], capture_output=True, text=True)
    mp3_files.append(out_path)

# Concat → AAC m4a
concat_file = os.path.join(temp_dir, "concat.txt")
with open(concat_file, "w") as f:
    for af in mp3_files:
        f.write(f"file '{af}'\n")

final_path = os.path.join(OUT_DIR, "corn_council_v1.m4a")
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
if failures:
    print(f"\n{len(failures)} line(s) failed (silence inserted):")
    for label, text, err in failures:
        print(f"  - {label}: {err[:200]}")

# svalley-podcast — Pipeline Reference

> **Read this first when making a new episode.** This is the canonical reference for
> the AI CEO podcast voice cloning pipeline. If you're an OpenClaw agent and you
> forgot this exists again, read this file top to bottom.

## Voice Cloning Pipeline (ElevenLabs + sag)

### Tools

- **TTS engine:** ElevenLabs API via `sag` CLI (ElevenLabs TTS)
- **Env / API key:** `~/.openclaw/agents/main/agent/elevenlabs.env` (chmod 600)
- **Model:** `eleven_turbo_v2_5` for fast multi-speaker dialogue
- **Concatenation:** ffmpeg → AAC m4a
- **Output dir:** `~/.openclaw/workspace/.cache/podcast/`

### Voice IDs (ElevenLabs clones)

| Label              | Voice ID                  | Status      | Notes |
|--------------------|---------------------------|-------------|-------|
| Steve Jobs         | `VqP3ylfAJnQDkfkqaSes`   | ✅ works    | Host. "Fake Steve" — pinned by Ray 2026-06-10. |
| Jensen Huang       | `l7zg34yrdZRade52A11W`   | ✅ works    | NVIDIA CEO. Leather jacket energy. |
| Mark Zuckerberg v2 | `OyWVL9LW2StlLFuOJIvc`   | ✅ works    | Use this one (v1 was blocked by ElevenLabs TOS). |
| Boz (A. Bosworth)  | `AO3MJs71nzPPbiQ4ynGt`   | ✅ works    | Meta CTO. NOT Jeff Bezos. |
| Jeff B (Jeremy)    | `kgDLS1JeFqVMIAW8JGRo`   | ✅ works    | Jeremy's clone. Used as "Jeff Bezos" stand-in. |
| Bill Gates         | `7uXYi4h2YXmavU1mNpgv`   | ✅ works    | Subbed for Elon in ep #002. |
| Elon Musk          | `NjHECNV1fBi9pkreu3ux`   | ❌ deleted  | 404 voice_not_found. Re-clone needed. |
| MZ v1 (old)        | `78wggkWNXpX7zCpzUp6Z`   | ❌ blocked  | ElevenLabs TOS impersonation block. |
| MZ fallback        | `UgBBYS2sOqTuMpoF3BR0`   | ✅ works    | Professional voice, not a clone. |

### Script Pattern

Both `render_podcast_example.py` (ep #001) and `render_corn_council.py` (ep #002)
follow the same pattern:

```python
LINES = [
    (voice_id, rate, text, label),
    ...
]
```

1. For each line: `sag speak -v <voice_id> -r <rate> --model-id eleven_turbo_v2_5 -o <mp3> <text>`
2. Concat all MP3s with ffmpeg → single AAC m4a
3. Send via `imsg send --chat-id <id> --file <m4a>` (MEDIA: directive is broken for iMessage groups)
4. Copy final m4a to `audio/` in this repo
5. Create episode HTML in `episodes/`
6. Update `index.html` with new episode card
7. Commit and push

### Rules (learned the hard way)

- **DO NOT** have speakers introduce themselves as "I'm AI <name>" — the AI framing
  belongs in the host's intro, not in self-intros. Ray called this out 2026-06-09.
- **DO** rewrite dialogue in the speaker's actual voice when swapping cloned voices.
  Wrong voice saying wrong personality lines = obvious mismatch.
- **DO** match voice IDs to the right personalities. Swapping without rewriting = bad.
- **DO NOT** use macOS `say`. Use `sag` (ElevenLabs). Corrected 2026-06-09.
- **DO** try fallback voices if a clone is blocked/deleted. Insert silence as
  placeholder if all options fail, then note it.

### Episode Log

| #   | Title                      | Date       | Voices                                         | Script                                |
|-----|----------------------------|------------|------------------------------------------------|---------------------------------------|
| 001 | Standing Desks            | 2026-06-04 | Mark, Boz                                      | (pre-pipeline, external)              |
| 002 | Corn Council              | 2026-06-16 | Steve, Jensen, Mark, Jeff B, Bill G            | `scripts/render_corn_council.py`      |

### Adding a New Episode

1. Copy `render_corn_council.py` as a template
2. Rewrite `LINES` with new dialogue (match personalities to voices!)
3. Run: `python3 scripts/render_<name>.py`
4. Copy output: `cp ~/.openclaw/workspace/.cache/podcast/<file> audio/00N-<slug>.m4a`
5. Create `episodes/00N-<slug>.html` (copy from existing episode for styling)
6. Add episode card to `index.html` (newest first)
7. `git add -A && git commit -m "ep 00N: <title>" && git push`

---

**Site:** podcast.svalley.org · **Repo:** rayhe/svalley-podcast
**Maintained by:** Jerbotclaw (OpenClaw agent for Jeremy Payne + Ray)

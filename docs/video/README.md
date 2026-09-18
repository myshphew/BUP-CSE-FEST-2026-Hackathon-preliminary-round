# Solution video

The current audit candidate video is `output/submission/1.0.1/gridwise-solution.mp4`: **2:38**, 1920x1080, 24 fps, H.264/AAC. All seven slides were visually inspected and the full audio/video stream decoded successfully. It is below the organizer's three-minute maximum.

It explains the problem, the LLM/guardrail/optimizer/replay boundary, actual official interpretation, cost-first/peak-second optimization, independent verification, Docker execution and the measured Terra/low profile. Screens use actual 1.0.1 container responses and audit reports; they are not a hosted 1.0.1 benchmark. Narration uses the installed Microsoft David synthetic voice. Review the [transcript](TRANSCRIPT.md); the team should understand every architectural choice.

The earlier 2:44 video is preserved at `output/submission/gridwise-solution.mp4` for the existing 1.0.0 release. Keep candidate and submitted versions clearly identified. A video in a draft release/private repository is not publicly accessible to judges; submit it through the permitted channel.

## Rebuild on this Windows machine

Optional media tools are separate from API dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install --target tmp/media-tools Pillow imageio-ffmpeg
.\.venv\Scripts\python.exe docs/video/build_video.py
```

Required inputs: `output/submission/1.0.1/sample-01-response.json`, `docs/audit-verification.json`, Windows Segoe UI fonts and the Microsoft David Desktop voice. The script makes no API calls and reads no credentials. It checks the three-minute ceiling before rendering. When changing measured results, update narration and evidence together, regenerate, visually inspect, decode and refresh checksums.

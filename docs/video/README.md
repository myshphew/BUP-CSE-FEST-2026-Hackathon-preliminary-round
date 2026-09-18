# Solution video

The local MP4 is `output/submission/gridwise-solution.mp4`: **2:44**, 1920×1080, 24 fps, H.264/AAC. It was visually checked, and a full audio/video decode succeeded. It is below the organizer's three-minute maximum.

Seven scenes explain the problem, architecture, a real official interpretation, optimization, verification, Docker execution, and performance. Screens use recorded local API evidence and actual test results. This is an architecture explainer with recorded results, not a public deployment screen capture. Narration uses the installed Microsoft David synthetic voice. Review the [transcript](TRANSCRIPT.md); the team may replace narration with its own recording.

The MP4, supporting evidence, image archive, manifest, and checksums are in the ignored `output/submission/` folder. Upload the MP4 to the organizer or an accessible video host. It has not been uploaded automatically.

## Rebuild on this Windows machine

Optional media tools are separate from the API requirements and Docker image:

```powershell
.\.venv\Scripts\python.exe -m pip install --target tmp/media-tools Pillow imageio-ffmpeg
.\.venv\Scripts\python.exe docs/video/build_video.py
```

Required inputs are `output/submission/sample-01-live-response.json`, `docs/docker-verification.json`, Windows Segoe UI fonts, and the Microsoft David Desktop voice. The script makes no API calls and reads no credentials. It checks the three-minute ceiling before rendering. Narration and slides are in `build_video.py`; the PowerShell helper only synthesizes supplied text. When changing measured results, update narration/evidence together, regenerate, and refresh the checksum.

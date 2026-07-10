# AirControlAI

AI-powered desktop controller for gesture, voice, assistant, and remote-control workflows.

## Milestones

| Milestone | Status |
| --- | --- |
| M1 - Project Setup | In progress |
| M2 - Camera & Hand Tracking | Not started |
| M3 - Gesture Engine | Not started |
| M4 - Mouse Control | Not started |
| M5 - Keyboard Control | Not started |
| M6 - AI Integration | Not started |
| M7 - Voice Commands | Not started |
| M8 - Remote Control | Not started |
| M9 - Professional GUI | Not started |
| M10 - Packaging & Documentation | Not started |

## Development Order

1. Camera
2. Hand tracking
3. Cursor movement
4. Click detection
5. Scroll
6. Keyboard gestures
7. Voice commands
8. AI commands
9. Remote laptop control
10. GUI
11. Packaging

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## Engineering Goals

- Cursor latency under 30 ms
- Stable hand tracking at 30+ FPS
- Graceful handling of lost hand tracking
- Configurable gesture sensitivity
- Cross-platform where practical, with Windows first

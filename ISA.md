---
task: Enhance AirControlAI gesture engine to be accurate and powerful
slug: aircontrolai-gesture-engine
effort: e3
phase: execute
progress: 0/36
mode: algorithm
started: 2026-07-07T00:00:00Z
updated: 2026-07-07T00:00:00Z
project: AirControlAI
---

## Problem

AirControlAI currently hardcodes gesture recognition inside `main.py`:
- Pointing is detected only by comparing fingertip Y-coordinates to PIP joints, which fails when the hand is rotated.
- Click is a bare threshold on thumb-index distance with no hysteresis or confidence.
- `gestures/gestures.json` exists but is empty and unused.
- There is no reusable engine for adding new gestures, no finger-state abstraction, and no state smoothing, so recognition flickers and accuracy drops as soon as the hand leaves the upright pose.

## Vision

The user experiences a stable, responsive gesture system: the cursor tracks smoothly, clicks fire reliably but not accidentally, and new gestures (open palm, fist, scroll, victory, thumbs up/down) can be added by editing a JSON file without touching Python. Recognition stays accurate even when the hand rotates or moves quickly because it reasons about finger states relative to the palm, not raw screen coordinates.

## Out of Scope

- No voice command integration in this change.
- No AI assistant integration in this change.
- No remote-control pairing or networking changes.
- No dashboard/GUI redesign beyond gesture status feedback in the OpenCV overlay.
- No new binary model files or dependencies beyond what is already in `requirements.txt`.
- No packaging, installer, or documentation website.

## Principles

1. **Extensibility over hardcoding.** Gestures are data-driven from JSON definitions, not scattered `if` trees.
2. **Orientation independence.** Finger state should be derived from palm geometry, not absolute image coordinates.
3. **Smooth state transitions.** Gesture outputs should be debounced so one noisy frame cannot flip the system state.
4. **Minimal coupling.** The engine exposes a small API; `main.py` asks it for the current gesture and acts on the result.
5. **Testability.** Landmark math and gesture matching must be unit-testable with synthetic or recorded data.

## Constraints

- The project must continue to run with the existing virtual environment (`requirements.txt`).
- Mouse fail-safe (`pyautogui.FAILSAFE`) must remain enabled.
- The existing One Euro cursor smoother must remain the cursor smoothing path.
- Hand tracking must keep MediaPipe legacy + Tasks compatibility already present in `core/hand_tracker.py`.

## Goal

Replace the hardcoded gesture checks in `main.py` with a `GestureEngine` that loads gesture definitions from `gestures/gestures.json`, recognizes finger-state patterns via palm-relative geometry, debounces state changes, and maps recognized gestures to actions through a clean API while preserving the existing cursor, click, and virtual-keyboard workflows.

## Criteria

- [ ] ISC-01: New module `core/gesture_engine.py` exists and exposes `GestureEngine` class.
- [ ] ISC-02: New module `core/finger_state.py` exists with `Finger` enum and `HandState` dataclass.
- [ ] ISC-03: Finger extended/folded detection uses palm-relative dot-product geometry, not absolute Y comparison.
- [ ] ISC-04: `HandState` computes finger states, palm center, palm radius, and palm plane normal from 21 MediaPipe landmarks.
- [ ] ISC-05: `gestures/gestures.json` defines at least 5 useful gestures: `point`, `pinch`, `open_palm`, `fist`, `scroll`.
- [ ] ISC-06: Each gesture definition contains `name`, `fingers`, `action`, `priority`, and optional `thresholds`.
- [ ] ISC-07: Gesture matching scores a confidence value and resolves ties by priority.
- [ ] ISC-08: `GestureEngine` returns a stable gesture with debouncing / cooldown so noisy frames do not flicker actions.
- [ ] ISC-09: `GestureEngine` maps the `point` gesture to continuous cursor coordinates from the index tip.
- [ ] ISC-10: `GestureEngine` maps the `pinch` gesture to a click action honoring a debounced cooldown.
- [ ] ISC-11: `GestureEngine` maps `scroll` gesture to a scroll action using vertical hand displacement.
- [ ] ISC-12: `GestureEngine` maps `open_palm` to an explicit neutral/idle state with no mouse action.
- [ ] ISC-13: `GestureEngine` maps `fist` to a reset that clears the smoother and releases any active state.
- [ ] ISC-14: `main.py` no longer contains hardcoded `index_tip.y < index_pip.y` checks.
- [ ] ISC-15: `main.py` calls `gesture_engine.update(landmarks)` each frame and dispatches returned actions.
- [ ] ISC-16: Existing mouse move + click + virtual-keyboard loop still works after refactor.
- [ ] ISC-17: Cursor cooler / virtual keyboard `k` toggle behavior is unchanged.
- [ ] ISC-18: Point gesture works when hand is rotated up to 90 degrees from vertical.
- [ ] ISC-19: Pinch click does not double-fire within the configured cooldown window.
- [ ] ISC-20: Adding a new gesture requires only editing `gestures/gestures.json` plus adding an action handler if needed.
- [ ] ISC-21: `requirements.txt` is unchanged (no new dependencies).
- [ ] ISC-22: Unit tests exist in `tests/test_finger_state.py` covering extended/folded logic with rotated hand fixtures.
- [ ] ISC-23: Unit tests exist in `tests/test_gesture_engine.py` covering all five defined gestures with synthetic landmarks.
- [ ] ISC-24: `python -m pytest tests/` runs successfully in the project virtual environment.
- [ ] ISC-25: `python main.py --dry-run` or a headless smoke test executes the main loop for 2 seconds without crashing.
- [ ] ISC-26: Logging output shows gesture transitions with human-readable names.
- [ ] ISC-27: `pyautogui.FAILSAFE` remains `True`.
- [ ] ISC-28: If MediaPipe returns no hands, the engine returns `NO_HAND` and `main.py` handles it gracefully.
- [ ] ISC-29: Gesture confidence below a configured threshold yields `UNCERTAIN` rather than a guessed gesture.
- [ ] ISC-30: Handedness (left/right) is normalized so left-handed users get the same gestures.
- [ ] ISC-31: OpenCV overlay displays current gesture name and confidence.
- [ ] ISC-32: `README.md` milestone table and development order are updated to reflect the completed gesture engine.
- [ ] ISC-33: Anti: No gesture action can execute from an uncertain or below-threshold match.
- [ ] ISC-34: Anti: Hardcoded gesture rules must not survive anywhere outside `gestures/gestures.json` and the engine.
- [ ] ISC-35: Anti: The engine must not import `pyautogui` or perform side-effects; actions are executed by `main.py`.
- [ ] ISC-36: Antecedent: A working webcam or test fixture is available for verification.

## Test Strategy

| ISC | Type | Check | Threshold | Tool |
|-----|------|-------|-------------|------|
| ISC-01 | file | `core/gesture_engine.py` exists | present | Glob |
| ISC-02 | file | `core/finger_state.py` exists | present | Glob |
| ISC-03 | code | landmark math uses palm-relative vectors | dot product sign | Read |
| ISC-04 | code | `HandState` properties present | 5 properties | Read |
| ISC-05 | data | `gestures/gestures.json` gestures >= 5 | ≥5 | Read |
| ISC-06 | data | schema fields present in each gesture | all 5 | Read |
| ISC-07 | unit | priority tie-break test | pass | pytest |
| ISC-08 | unit | debounce test with noisy frames | pass | pytest |
| ISC-09 | unit | `point` returns cursor point | pass | pytest |
| ISC-10 | unit | `pinch` returns click after cooldown | pass | pytest |
| ISC-11 | unit | `scroll` returns scroll delta | pass | pytest |
| ISC-12 | unit | `open_palm` maps to neutral | pass | pytest |
| ISC-13 | unit | `fist` maps to reset | pass | pytest |
| ISC-14 | grep | no `index_pip.y` in `main.py` | 0 matches | Grep |
| ISC-15 | grep | `gesture_engine.update` called | ≥1 match | Grep |
| ISC-16 | smoke | `python main.py` runs for 2s | no crash | Bash |
| ISC-17 | manual | `k` toggles keyboard | works | run |
| ISC-18 | unit | rotated hand fixture for point | pass | pytest |
| ISC-19 | unit | pinch cooldown test | pass | pytest |
| ISC-20 | code | new gesture JSON only + handler map | inspection | Read |
| ISC-21 | diff | `requirements.txt` unchanged | identical | git diff |
| ISC-22 | test | `test_finger_state.py` passes | pass | pytest |
| ISC-23 | test | `test_gesture_engine.py` passes | pass | pytest |
| ISC-24 | suite | full pytest suite | pass | pytest |
| ISC-25 | smoke | headless main loop | 2s no crash | Bash |
| ISC-26 | log | named transitions in log | match | Bash |
| ISC-27 | grep | `FAILSAFE = True` | present | Grep |
| ISC-28 | unit | empty landmarks -> NO_HAND | pass | pytest |
| ISC-29 | unit | low confidence -> UNCERTAIN | pass | pytest |
| ISC-30 | unit | left/right hand normalization | pass | pytest |
| ISC-31 | visual | overlay text in OpenCV frame | inspection | Read |
| ISC-32 | doc | README reflects updated milestones | updated | Read |
| ISC-33 | unit | uncertain action is None | pass | pytest |
| ISC-34 | grep | no `is_pointing` / `index_extended` in main | 0 matches | Grep |
| ISC-35 | grep | `pyautogui` import in `core/` | 0 matches | Grep |
| ISC-36 | manual | webcam or fixture available | available | Bash |

## Features

| name | description | satisfies | depends_on | parallelizable |
|------|-------------|-----------|------------|----------------|
| finger_state | Palm-relative finger-state computation | ISC-02, ISC-03, ISC-04, ISC-18, ISC-30 | none | yes |
| gesture_engine | Score-and-debounce gesture recognition core | ISC-01, ISC-07, ISC-08, ISC-28, ISC-29, ISC-33 | finger_state | yes |
| gesture_json | Configurable gesture definitions | ISC-05, ISC-06, ISC-20, ISC-34 | gesture_engine | no |
| main_refactor | Replace hardcoded checks with engine dispatch | ISC-14, ISC-15, ISC-16, ISC-17, ISC-31, ISC-35 | gesture_engine, gesture_json | no |
| action_handlers | Map gestures to mouse/keyboard/reset actions | ISC-09, ISC-10, ISC-11, ISC-12, ISC-13 | main_refactor | no |
| tests | Unit tests for finger state and engine | ISC-22, ISC-23, ISC-24, ISC-25 | finger_state, gesture_engine | yes |
| readme | Update documentation milestones | ISC-32 | main_refactor | no |

## Decisions

- 2026-07-07: Use E3 effort because the work is multi-file, architectural, and requires new engine code plus tests.
- 2026-07-07: MediaPipe legacy+Tasks compatibility is preserved; the engine consumes the normalized 21-landmark list regardless of source.
- 2026-07-07: Keep action execution in `main.py` so `core/` remains side-effect free.
- 2026-07-07: Palm-relative vector dot-product replaces the legacy Y-axis extended check to fix rotation sensitivity.
- 2026-07-07: Engine is stateless except for a small per-gesture confidence history / cooldown; no persistent side-effects.

### Risks

- Rotated-hand fixtures may not capture all real-world orientations; smoke test required.
- Left/right handedness normalization could flip finger roles if not carefully mapped.
- Debounce parameters are heuristic; may need tuning after real-world use.

## Changelog

- Conjectured: A palm-relative finger-state model will fix rotation-dependent pointing and enable new gestures.
- Refuted by: TBD / verification.
- Learned: TBD.
- Criterion now: ISC-03, ISC-18.

## Verification

- Pending execution phase evidence.

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
import os
from pathlib import Path

import cv2


@dataclass(slots=True)
class HandTrackerConfig:
    max_num_hands: int = 1
    min_detection_confidence: float = 0.7
    min_tracking_confidence: float = 0.7
    model_asset_path: str | None = None


class HandTracker:
    def __init__(self, config: HandTrackerConfig | None = None) -> None:
        self.config = config or HandTrackerConfig()
        self._load_error: Exception | None = None
        self._hands = None
        self._tasks_mode = False

        try:
            mp_hands = import_module("mediapipe.solutions.hands")
            self._hands = mp_hands.Hands(
                max_num_hands=self.config.max_num_hands,
                min_detection_confidence=self.config.min_detection_confidence,
                min_tracking_confidence=self.config.min_tracking_confidence,
            )
        except Exception as error:
            try:
                self._hands = self._create_tasks_hand_landmarker()
                self._tasks_mode = True
            except Exception as tasks_error:
                self._load_error = tasks_error if isinstance(error, ModuleNotFoundError) else error

    def _create_tasks_hand_landmarker(self):
        default_model_path = Path(__file__).resolve().parent.parent / "models" / "hand_landmarker.task"
        model_asset_path = (
            self.config.model_asset_path
            or os.getenv("AIRCONTROL_HAND_LANDMARKER_MODEL")
            or str(default_model_path)
        )
        if not model_asset_path:
            raise RuntimeError(
                "MediaPipe Tasks is installed, but no hand landmarker model was configured. "
                "Set AIRCONTROL_HAND_LANDMARKER_MODEL to a .task model file."
            )

        resolved_model_path = Path(model_asset_path).expanduser().resolve()
        if not resolved_model_path.is_file():
            raise FileNotFoundError(f"Hand landmarker model not found: {resolved_model_path}")

        import mediapipe as mp
        from mediapipe.tasks.python import BaseOptions
        from mediapipe.tasks.python import vision

        options = vision.HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(resolved_model_path)),
            running_mode=vision.RunningMode.IMAGE,
            num_hands=self.config.max_num_hands,
            min_hand_detection_confidence=self.config.min_detection_confidence,
            min_tracking_confidence=self.config.min_tracking_confidence,
        )
        return vision.HandLandmarker.create_from_options(options)

    def detect(self, frame):
        if self._hands is None:
            raise RuntimeError("MediaPipe hand tracker is not available.") from self._load_error

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if self._tasks_mode:
            import mediapipe as mp

            image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            return self._hands.detect(image)

        return self._hands.process(rgb_frame)

    def is_available(self) -> bool:
        return self._hands is not None

    @property
    def load_error(self) -> Exception | None:
        return self._load_error

    def close(self) -> None:
        if self._hands is not None:
            self._hands.close()

from __future__ import annotations

from dataclasses import dataclass

import cv2


@dataclass(slots=True)
class CameraConfig:
    device_index: int = 0
    width: int = 1280
    height: int = 720
    fps: int = 30


class Camera:
    def __init__(self, config: CameraConfig | None = None) -> None:
        self.config = config or CameraConfig()
        self._capture: cv2.VideoCapture | None = None

    def open(self) -> None:
        if self._capture is not None:
            return

        capture = cv2.VideoCapture(self.config.device_index)
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)
        capture.set(cv2.CAP_PROP_FPS, self.config.fps)
        self._capture = capture

    def read(self):
        if self._capture is None:
            self.open()

        if self._capture is None:
            return False, None

        return self._capture.read()

    def is_available(self) -> bool:
        self.open()
        return bool(self._capture and self._capture.isOpened())

    def release(self) -> None:
        if self._capture is not None:
            self._capture.release()
            self._capture = None

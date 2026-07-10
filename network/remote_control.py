from __future__ import annotations


class RemoteControl:
    def __init__(self) -> None:
        self._paired = False

    @property
    def is_paired(self) -> bool:
        return self._paired

    def pair(self, pairing_code: str) -> bool:
        self._paired = bool(pairing_code.strip())
        return self._paired

    def disconnect(self) -> None:
        self._paired = False

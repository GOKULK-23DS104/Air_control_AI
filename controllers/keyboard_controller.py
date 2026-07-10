from __future__ import annotations

from pynput.keyboard import Controller, Key


class KeyboardController:
    def __init__(self) -> None:
        self._keyboard = Controller()

    def press_key(self, key: str) -> None:
        self._keyboard.press(key)
        self._keyboard.release(key)

    def hotkey(self, *keys: str) -> None:
        parsed_keys = [getattr(Key, key, key) for key in keys]
        for key in parsed_keys:
            self._keyboard.press(key)
        for key in reversed(parsed_keys):
            self._keyboard.release(key)

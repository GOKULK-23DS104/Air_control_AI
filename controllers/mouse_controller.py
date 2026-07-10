from __future__ import annotations

import pyautogui


class MouseController:
    def __init__(self) -> None:
        pyautogui.FAILSAFE = True

    def move_to(self, x: int, y: int, duration: float = 0.0) -> None:
        pyautogui.moveTo(x, y, duration=duration)

    def click(self, button: str = "left") -> None:
        pyautogui.click(button=button)

    def scroll(self, amount: int) -> None:
        pyautogui.scroll(amount)

    def is_available(self) -> bool:
        return True

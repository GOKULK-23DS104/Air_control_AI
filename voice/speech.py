from __future__ import annotations

import speech_recognition as sr


class SpeechRecognizer:
    def __init__(self) -> None:
        self._recognizer = sr.Recognizer()

    def listen_once(self) -> str:
        with sr.Microphone() as source:
            audio = self._recognizer.listen(source)
        return self._recognizer.recognize_google(audio)

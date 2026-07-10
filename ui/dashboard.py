from __future__ import annotations

import customtkinter as ctk


class Dashboard(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("AirControlAI")
        self.geometry("900x600")

        title = ctk.CTkLabel(self, text="AirControlAI")
        title.pack(padx=24, pady=24)


def run_dashboard() -> None:
    app = Dashboard()
    app.mainloop()

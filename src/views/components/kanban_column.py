import customtkinter as ctk
from .task_card import TaskCard

class KanbanColumn(ctk.CTkFrame):
    def __init__(self, master, title, add_command, **kwargs):
        # Merge kwargs with our default column styling
        kwargs.setdefault("fg_color", "#161e31")
        kwargs.setdefault("corner_radius", 10)
        super().__init__(master, **kwargs)
        self.title = title

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(header, text=title.upper(), font=("Inter", 15, "bold"), text_color="white").pack(side="left")
        ctk.CTkButton(header, text="+", width=32, height=32, fg_color="#232d42", hover_color="#3478f6", 
                      font=("Inter", 16, "bold"), command=lambda: self.after(50, lambda: add_command(title))).pack(side="right")

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", width=230, height=500)
        self.scroll.pack(expand=True, fill="both", padx=5, pady=5)

    def add_task(self, task, refresh_callback, main_window):
        card = TaskCard(self.scroll, task, refresh_callback, main_window)
        card.pack(fill="x", padx=2, pady=5)
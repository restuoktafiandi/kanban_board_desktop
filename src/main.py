import customtkinter as ctk
from config.db import init_db
from views.main_window import MainWindow

if __name__ == "__main__":
    init_db()
    ctk.set_appearance_mode("dark")
    app = MainWindow()
    app.mainloop()
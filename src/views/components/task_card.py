import customtkinter as ctk
from controllers.task_controller import TaskController

class TaskCard(ctk.CTkFrame):
    def __init__(self, master, task, on_refresh, main_window, **kwargs):
        super().__init__(master, fg_color="#232d42", corner_radius=8, border_width=1, border_color="#323e59", cursor="hand2", **kwargs)
        
        self.task = task
        self.on_refresh = on_refresh
        self.main_window = main_window

        # Title
        ctk.CTkLabel(self, text=task.title, font=("Inter", 14, "bold"), text_color="#ffffff", wraplength=200).pack(padx=12, pady=(12, 5), anchor="w")
        # Tag
        ctk.CTkLabel(self, text=f"#{task.tags}", font=("Inter", 11, "bold"), text_color="#5dade2").pack(padx=12, pady=0, anchor="w")

        # Dates
        date_str = f"Created: {task.created_at.strftime('%b %d')}"
        if task.due_date:
            date_str += f" | Due: {task.due_date.strftime('%b %d')}"
            
        ctk.CTkLabel(self, text=date_str, font=("Inter", 10), text_color="#888888").pack(padx=12, pady=(5, 5), anchor="w")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.del_btn = ctk.CTkButton(btn_frame, text="Delete", width=50, height=24, fg_color="#c0392b", 
                                     hover_color="#e74c3c", font=("Inter", 11, "bold"), text_color="white", command=self.delete)
        self.del_btn.pack(side="right")

        # Drag and drop bindings
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)
        
        # Bind children as well so clicking inside the card also triggers drag
        for child in self.winfo_children():
            # Exclude the delete button from drag
            if child != btn_frame and child != self.del_btn:
                child.bind("<ButtonPress-1>", self.on_press)
                child.bind("<B1-Motion>", self.on_drag)
                child.bind("<ButtonRelease-1>", self.on_release)

    def on_press(self, event):
        self.main_window.dragged_task = self.task
        self.start_x = self.main_window.winfo_pointerx()
        self.start_y = self.main_window.winfo_pointery()
        self.is_dragging = False

    def on_drag(self, event):
        # Calculate distance
        curr_x = self.main_window.winfo_pointerx()
        curr_y = self.main_window.winfo_pointery()
        distance = ((curr_x - self.start_x)**2 + (curr_y - self.start_y)**2)**0.5
        
        if distance > 5:
            self.is_dragging = True
            
            # Create ghost widget for dragging if not exists
            if not self.main_window.ghost_widget:
                self.main_window.ghost_widget = ctk.CTkFrame(self.main_window, fg_color="#232d42", corner_radius=8, border_width=2, border_color="#3478f6", width=self.winfo_width(), height=self.winfo_height())
                ctk.CTkLabel(self.main_window.ghost_widget, text=self.task.title, font=("Inter", 14, "bold"), text_color="white").place(relx=0.5, rely=0.5, anchor="center")
            
            x = curr_x - self.main_window.winfo_rootx()
            y = curr_y - self.main_window.winfo_rooty()
            self.main_window.ghost_widget.place(x=x-50, y=y-20)

    def on_release(self, event):
        if self.main_window.ghost_widget:
            self.main_window.ghost_widget.destroy()
            self.main_window.ghost_widget = None

        if not self.main_window.dragged_task:
            return

        if not self.is_dragging:
            # It was a simple click, open detail modal
            self.main_window.dragged_task = None
            self.main_window.open_task_detail(self.task)
            return

        # Handle Drop
        x = self.main_window.winfo_pointerx()
        y = self.main_window.winfo_pointery()
        widget = self.main_window.winfo_containing(x, y)
        
        if widget:
            # Climb up to find the column status
            new_status = None
            for status, col in self.main_window.columns.items():
                if self.is_child_of(widget, col):
                    new_status = status
                    break
            
            if new_status and new_status != self.task.status:
                TaskController.update_status(self.task.id, new_status)
                self.on_refresh()
                
        self.main_window.dragged_task = None
        self.is_dragging = False

    def is_child_of(self, child, parent):
        if child == parent:
            return True
        p = child.master
        while p:
            if p == parent:
                return True
            p = p.master
        return False

    def delete(self):
        TaskController.delete_task(self.task.id)
        self.on_refresh()
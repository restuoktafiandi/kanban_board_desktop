import customtkinter as ctk
import tkinter.ttk as ttk
from datetime import datetime
from tkcalendar import DateEntry
from .components.kanban_column import KanbanColumn
from controllers.task_controller import TaskController

class TaskDialog(ctk.CTkToplevel):
    def __init__(self, master, status, on_submit, task=None):
        super().__init__(master)
        self.is_edit = task is not None
        self.title("Edit Task" if self.is_edit else f"New Task in {status}")
        self.geometry("450x480")
        self.resizable(False, False)
        self.status = status
        self.on_submit = on_submit
        self.task = task
        
        # Center dialog
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() // 2) - 225
        y = master.winfo_y() + (master.winfo_height() // 2) - 240
        self.geometry(f"+{x}+{y}")
        self.transient(master)
        self.grab_set()

        header_text = "Edit Task" if self.is_edit else f"Add Task - {status}"
        ctk.CTkLabel(self, text=header_text, font=("Inter", 16, "bold")).pack(pady=(15, 10))

        # Title
        self.title_entry = ctk.CTkEntry(self, placeholder_text="Task Title", width=350)
        self.title_entry.pack(pady=5)

        # Description
        self.desc_entry = ctk.CTkTextbox(self, width=350, height=100)
        self.desc_entry.pack(pady=5)
        if not self.is_edit:
            self.desc_entry.insert("1.0", "")
        
        # Tags
        tags_options = ["Bug", "Feature", "Enhancement", "Urgent", "UI/UX", "General"]
        self.tags_entry = ctk.CTkComboBox(self, values=tags_options, width=350)
        self.tags_entry.pack(pady=5)

        # Style DateEntry to match dark theme
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Dark.DateEntry', 
                        fieldbackground='#2b2b2b', background='#1e1e1e', 
                        foreground='white', bordercolor='#3a3a3a', 
                        lightcolor='#3a3a3a', darkcolor='#3a3a3a',
                        arrowcolor='white')

        # Due Date
        date_frame = ctk.CTkFrame(self, fg_color="transparent")
        date_frame.pack(pady=5)
        ctk.CTkLabel(date_frame, text="Due Date: ", font=("Inter", 12)).pack(side="left", padx=5)
        
        self.date_entry = DateEntry(date_frame, width=20, style='Dark.DateEntry',
                                    headersbackground='#1e1e1e', headersforeground='white',
                                    selectbackground='#1f538d', selectforeground='white',
                                    normalbackground='#2b2b2b', normalforeground='white', 
                                    bottombackground='#1e1e1e', borderwidth=0, date_pattern='y-mm-dd')
        self.date_entry.pack(side="left", padx=5)

        if self.is_edit:
            self.title_entry.insert(0, task.title)
            if task.description:
                self.desc_entry.insert("1.0", task.description)
            self.tags_entry.set(task.tags)
            if task.due_date:
                self.date_entry.set_date(task.due_date)
        else:
            self.tags_entry.set("General")

        submit_text = "Save Changes" if self.is_edit else "Create Task"
        submit_btn = ctk.CTkButton(self, text=submit_text, width=350, command=self.submit)
        submit_btn.pack(pady=20)

    def submit(self):
        title = self.title_entry.get().strip()
        description = self.desc_entry.get("1.0", "end-1c").strip()
        tags = self.tags_entry.get().strip()
        date_str = self.date_entry.get()

        if not title:
            return

        due_date = None
        if date_str:
            try:
                due_date = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                pass

        self.on_submit(title, description, tags, self.status, due_date)
        self.destroy()

class TaskDetailModal(ctk.CTkToplevel):
    def __init__(self, master, task, on_edit_click):
        super().__init__(master)
        self.title("Task Detail")
        self.geometry("450x400")
        self.resizable(False, False)
        
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() // 2) - 225
        y = master.winfo_y() + (master.winfo_height() // 2) - 200
        self.geometry(f"+{x}+{y}")
        self.transient(master)
        self.grab_set()

        ctk.CTkLabel(self, text=task.title, font=("Inter", 20, "bold"), wraplength=400).pack(pady=(20, 5))
        ctk.CTkLabel(self, text=f"Status: {task.status}  |  Tags: #{task.tags}", font=("Inter", 12), text_color="#5dade2").pack(pady=0)
        
        dates_frame = ctk.CTkFrame(self, fg_color="transparent")
        dates_frame.pack(pady=10)
        created_str = f"Created: {task.created_at.strftime('%Y-%m-%d')}"
        due_str = f"Due: {task.due_date.strftime('%Y-%m-%d')}" if task.due_date else "Due: None"
        ctk.CTkLabel(dates_frame, text=created_str, font=("Inter", 12), text_color="#aaaaaa").pack(side="left", padx=10)
        ctk.CTkLabel(dates_frame, text=due_str, font=("Inter", 12), text_color="#e74c3c" if task.due_date else "#aaaaaa").pack(side="left", padx=10)

        # Description Box (Read Only)
        desc_box = ctk.CTkTextbox(self, width=400, height=120)
        desc_box.pack(pady=10)
        desc_box.insert("1.0", task.description if task.description else "No description provided.")
        desc_box.configure(state="disabled")

        edit_btn = ctk.CTkButton(self, text="Edit Task", width=400, command=lambda: [self.destroy(), on_edit_click()])
        edit_btn.pack(pady=20)

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Kanban Board | by ❤️ Restu Oktafiandi")
        self.geometry("1200x700")
        self.configure(fg_color="#0e1526")
        
        self.dragged_task = None
        self.ghost_widget = None

        # Top Section
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=25, pady=(25, 10))
        
        ctk.CTkLabel(top_frame, text="MY DAILY KANBAN", font=("Inter", 26, "bold"), text_color="white").pack(side="left")
        
        # Search Bar
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_ui())
        self.search_entry = ctk.CTkEntry(top_frame, placeholder_text="Search tasks...", textvariable=self.search_var, 
                                         width=280, height=36, corner_radius=18, border_color="#323e59", fg_color="#161e31")
        self.search_entry.pack(side="right", padx=10)
        
        # Unfocus search entry on Enter or Escape
        self.search_entry.bind("<Return>", lambda e: self.focus_set())
        self.search_entry.bind("<Escape>", lambda e: [self.search_var.set(""), self.focus_set()])
        
        # Unfocus if clicking outside (on top frame)
        top_frame.bind("<Button-1>", lambda e: self.focus_set())

        # Status Filters (Pill Buttons)
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", padx=25, pady=(0, 15))
        
        self.statuses = ["Backlog", "To Do", "In Progress", "Review", "Done"]
        self.status_vars = {}
        self.status_btns = {}
        
        ctk.CTkLabel(filter_frame, text="Filters:", font=("Inter", 14, "bold"), text_color="#aaaaaa").pack(side="left", padx=(0, 15))
        for status in self.statuses:
            var = ctk.BooleanVar(value=True)
            self.status_vars[status] = var
            btn = ctk.CTkButton(filter_frame, text=status, corner_radius=15, height=30,
                                fg_color="#3478f6", text_color="white", hover_color="#2b62c8",
                                command=lambda s=status: self.toggle_filter(s))
            btn.pack(side="left", padx=5)
            self.status_btns[status] = btn

        self.main_scroll = ctk.CTkScrollableFrame(self, orientation="horizontal", fg_color="transparent")
        self.main_scroll.pack(expand=True, fill="both", padx=15, pady=10)

        self.columns = {}
        for status in self.statuses:
            col = KanbanColumn(self.main_scroll, title=status, add_command=self.add_task, width=300)
            self.columns[status] = col

        self.toggle_columns()

        self.bind_all("<MouseWheel>", self.on_mousewheel)
        self.bind_all("<Button-4>", self.on_mousewheel)
        self.bind_all("<Button-5>", self.on_mousewheel)

        # Dynamic scrollbar hide/show
        self.main_scroll._parent_canvas.bind("<Configure>", self.check_scrollbar)
        self.main_scroll._parent_frame.bind("<Configure>", self.check_scrollbar)

    def check_scrollbar(self, event=None):
        try:
            canvas = self.main_scroll._parent_canvas
            bbox = canvas.bbox("all")
            if bbox:
                content_width = bbox[2] - bbox[0]
                if content_width <= canvas.winfo_width():
                    self.main_scroll._scrollbar.grid_remove()
                else:
                    self.main_scroll._scrollbar.grid()
        except Exception:
            pass

    def toggle_filter(self, status):
        var = self.status_vars[status]
        var.set(not var.get())
        btn = self.status_btns[status]
        
        if var.get():
            btn.configure(fg_color="#3478f6", hover_color="#2b62c8")
        else:
            btn.configure(fg_color="#161e31", hover_color="#232d42")
            
        self.toggle_columns()

    def toggle_columns(self):
        for status in self.statuses:
            self.columns[status].pack_forget()
            
        for status in self.statuses:
            if self.status_vars[status].get():
                self.columns[status].pack(side="left", fill="both", padx=10)
                
        self.refresh_ui()
        self.after(50, self.check_scrollbar) # Check after repack

    def is_child_of(self, child, parent):
        if child == parent:
            return True
        p = child.master
        while p:
            if p == parent:
                return True
            p = p.master
        return False

    def on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            direction = -1
        elif event.num == 5 or event.delta < 0:
            direction = 1
        else:
            return

        x, y = self.winfo_pointerxy()
        widget_under_mouse = self.winfo_containing(x, y)
        
        is_inside_col = False
        if widget_under_mouse:
            for col in self.columns.values():
                if self.is_child_of(widget_under_mouse, col.scroll._parent_canvas) or self.is_child_of(widget_under_mouse, col.scroll._parent_frame):
                    is_inside_col = True
                    break
        
        if not is_inside_col:
            try:
                self.main_scroll._parent_canvas.xview_scroll(direction, "units")
            except AttributeError:
                self.main_scroll._parent_canvas.yview_scroll(direction, "units")

    def add_task(self, status):
        def on_submit(title, description, tags, status, due_date):
            TaskController.create_task(title, description, tags, status, due_date)
            self.refresh_ui()
        
        TaskDialog(self, status, on_submit)

    def open_task_detail(self, task):
        TaskDetailModal(self, task, on_edit_click=lambda: self.edit_task(task))

    def edit_task(self, task):
        def on_submit(title, description, tags, status, due_date):
            TaskController.update_task(task.id, title, description, tags, due_date)
            self.refresh_ui()
            
        TaskDialog(self, task.status, on_submit, task=task)

    def refresh_ui(self):
        search_query = self.search_var.get().lower()
        
        for col in self.columns.values():
            for child in col.scroll.winfo_children():
                child.destroy()
        
        for status in self.statuses:
            if not self.status_vars[status].get():
                continue
                
            tasks = TaskController.get_tasks_by_status(status)
            for task in tasks:
                if search_query and search_query not in task.title.lower() and search_query not in (task.tags or "").lower():
                    continue
                self.columns[status].add_task(task, self.refresh_ui, self)
        
        self.after(50, self.check_scrollbar)
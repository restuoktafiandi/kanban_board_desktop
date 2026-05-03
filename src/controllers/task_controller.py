from config.db import SessionLocal
from models.task import Task

class TaskController:
    @staticmethod
    def create_task(title, description, tags, status, due_date=None):
        db = SessionLocal()
        new_task = Task(title=title, description=description, tags=tags, status=status, due_date=due_date)
        db.add(new_task)
        db.commit()
        db.close()

    @staticmethod
    def get_tasks_by_status(status):
        db = SessionLocal()
        tasks = db.query(Task).filter(Task.status == status).all()
        db.close()
        return tasks

    @staticmethod
    def update_status(task_id, new_status):
        db = SessionLocal()
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = new_status
            db.commit()
        db.close()

    @staticmethod
    def update_task(task_id, title, description, tags, due_date=None):
        db = SessionLocal()
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.title = title
            task.description = description
            task.tags = tags
            task.due_date = due_date
            db.commit()
        db.close()

    @staticmethod
    def delete_task(task_id):
        db = SessionLocal()
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            db.delete(task)
            db.commit()
        db.close()
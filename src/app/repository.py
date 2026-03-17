from sqlalchemy.orm import Session
from src.app.database import AnalysisTask

class TaskRepository:
    def create_task(self, db: Session, target_name: str) -> AnalysisTask:
        new_task = AnalysisTask(target_name=target_name, status="PENDING")
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return new_task
    
    def update_task(self, db: Session, task_id: str, status: str, result_text: str = None, error: str = None):
        task = db.query(AnalysisTask).filter(AnalysisTask.task_id == task_id).first()
        if task:
            task.status = status
            if result_text:
                task.result_text = result_text
            if error:
                task.error_message = error
            db.commit()
            db.refresh(task)
        return task

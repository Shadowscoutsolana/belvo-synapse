import json
from typing import Optional, Any, Dict
from sqlalchemy.orm import Session
from app.models.users import AuditLog

class AuditService:
    @staticmethod
    def log_action(
        db: Session,
        user_id: Optional[int],
        table_name: str,
        record_id: Optional[int],
        action: str,
        before: Optional[Dict[str, Any]] = None,
        after: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        log_entry = AuditLog(
            user_id=user_id,
            table_name=table_name,
            record_id=record_id,
            action=action,
            before_json=before,
            after_json=after
        )
        db.add(log_entry)
        db.commit()
        return log_entry

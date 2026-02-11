"""
Database Services
Handles all database operations and queries
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from core.logging.logger import db_logger


class DatabaseService:
    """
    Base database service class
    Extend this for specific database operations
    """
    
    def __init__(self, db: Session):
        """
        Initialize database service
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    async def create(self, model: Any, data: Dict) -> Optional[Any]:
        """
        Create a new record
        
        Args:
            model: SQLAlchemy model class
            data: Data to create record with
            
        Returns:
            Created record or None
        """
        try:
            instance = model(**data)
            self.db.add(instance)
            self.db.commit()
            self.db.refresh(instance)
            
            db_logger.info(
                f"Created new {model.__name__} record",
                method="CREATE",
                extra_info={"id": getattr(instance, 'id', None)}
            )
            
            return instance
            
        except Exception as e:
            self.db.rollback()
            db_logger.error(
                f"Error creating {model.__name__}: {str(e)}",
                method="CREATE",
                extra_info={"data": data}
            )
            return None
    
    async def get_by_id(self, model: Any, record_id: int) -> Optional[Any]:
        """
        Get record by ID
        
        Args:
            model: SQLAlchemy model class
            record_id: Record ID
            
        Returns:
            Record or None
        """
        try:
            record = self.db.query(model).filter(model.id == record_id).first()
            
            if record:
                db_logger.info(
                    f"Retrieved {model.__name__} record",
                    method="GET",
                    extra_info={"id": record_id}
                )
            
            return record
            
        except Exception as e:
            db_logger.error(
                f"Error getting {model.__name__} by ID: {str(e)}",
                method="GET",
                extra_info={"id": record_id}
            )
            return None
    
    async def get_all(self, model: Any, skip: int = 0, limit: int = 100) -> List[Any]:
        """
        Get all records with pagination
        
        Args:
            model: SQLAlchemy model class
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of records
        """
        try:
            records = self.db.query(model).offset(skip).limit(limit).all()
            
            db_logger.info(
                f"Retrieved {len(records)} {model.__name__} records",
                method="GET_ALL",
                extra_info={"skip": skip, "limit": limit}
            )
            
            return records
            
        except Exception as e:
            db_logger.error(
                f"Error getting all {model.__name__}: {str(e)}",
                method="GET_ALL"
            )
            return []
    
    async def update(self, model: Any, record_id: int, data: Dict) -> Optional[Any]:
        """
        Update a record
        
        Args:
            model: SQLAlchemy model class
            record_id: Record ID to update
            data: Data to update
            
        Returns:
            Updated record or None
        """
        try:
            record = self.db.query(model).filter(model.id == record_id).first()
            
            if not record:
                db_logger.warning(
                    f"{model.__name__} record not found",
                    method="UPDATE",
                    extra_info={"id": record_id}
                )
                return None
            
            for key, value in data.items():
                if hasattr(record, key):
                    setattr(record, key, value)
            
            self.db.commit()
            self.db.refresh(record)
            
            db_logger.info(
                f"Updated {model.__name__} record",
                method="UPDATE",
                extra_info={"id": record_id}
            )
            
            return record
            
        except Exception as e:
            self.db.rollback()
            db_logger.error(
                f"Error updating {model.__name__}: {str(e)}",
                method="UPDATE",
                extra_info={"id": record_id, "data": data}
            )
            return None
    
    async def delete(self, model: Any, record_id: int) -> bool:
        """
        Delete a record
        
        Args:
            model: SQLAlchemy model class
            record_id: Record ID to delete
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            record = self.db.query(model).filter(model.id == record_id).first()
            
            if not record:
                db_logger.warning(
                    f"{model.__name__} record not found",
                    method="DELETE",
                    extra_info={"id": record_id}
                )
                return False
            
            self.db.delete(record)
            self.db.commit()
            
            db_logger.info(
                f"Deleted {model.__name__} record",
                method="DELETE",
                extra_info={"id": record_id}
            )
            
            return True
            
        except Exception as e:
            self.db.rollback()
            db_logger.error(
                f"Error deleting {model.__name__}: {str(e)}",
                method="DELETE",
                extra_info={"id": record_id}
            )
            return False


class TransactionManager:
    """Manage database transactions"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def execute_transaction(self, operations: List[callable]) -> bool:
        """
        Execute multiple operations in a single transaction
        
        Args:
            operations: List of operations to execute
            
        Returns:
            True if successful, False otherwise
        """
        try:
            for operation in operations:
                operation()
            
            self.db.commit()
            db_logger.info(
                f"Transaction completed successfully",
                method="TRANSACTION",
                extra_info={"operations_count": len(operations)}
            )
            return True
            
        except Exception as e:
            self.db.rollback()
            db_logger.error(
                f"Transaction failed: {str(e)}",
                method="TRANSACTION"
            )
            return False

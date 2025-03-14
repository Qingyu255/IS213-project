from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
from uuid import UUID

class Base(DeclarativeBase):
    def to_dict(self):
        """Convert model instance to dictionary."""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, (datetime, UUID)):
                value = str(value)
            result[column.name] = value
        
        # Handle relationships if they exist
        for relationship in self.__mapper__.relationships:
            related_obj = getattr(self, relationship.key)
            if related_obj is not None:
                if hasattr(related_obj, '__iter__'):
                    result[relationship.key] = [obj.to_dict() if hasattr(obj, 'to_dict') else str(obj) for obj in related_obj]
                else:
                    result[relationship.key] = related_obj.to_dict() if hasattr(related_obj, 'to_dict') else str(related_obj)
        
        return result

Base = declarative_base() 
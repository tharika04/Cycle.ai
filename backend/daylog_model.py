from sqlalchemy import Column, Integer, String, Date, ForeignKey

from backend.database import Base


class DayTag(Base):
    __tablename__ = "day_tags"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    date = Column(Date, nullable=False, index=True)
    category = Column(String, nullable=False)
    tag = Column(String, nullable=False)
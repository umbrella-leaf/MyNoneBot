from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, String, Column, Text, DATETIME

Base = declarative_base()


class ReportMessageInfo(Base):
    __tablename__ = "report_message_info"

    id = Column(Integer, primary_key=True)
    nickname = Column(String(255))
    avatar_url = Column(String(255))
    message = Column(Text)
    appendix = Column(Text)
    send_time = Column(DATETIME)
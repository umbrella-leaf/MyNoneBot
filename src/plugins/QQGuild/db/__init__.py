import pymysql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .model import ReportMessageInfo, Base


class MySQLClient:
    def __init__(self, user: str,
                 password: str,
                 host: str,
                 dbname: str,
                 echo: bool = False,
                 pool_size: int = 8,
                 pool_recycle: int = 1800):
        pymysql.install_as_MySQLdb()
        url = f"mysql://{user}:{password}@{host}/{dbname}?charset=utf8"
        self.engine = create_engine(url, echo=echo,
                                    pool_size=pool_size,
                                    pool_recycle=pool_recycle)
        Base.metadata.create_all(self.engine)
        self.DbSession = sessionmaker(bind=self.engine)

    def addInfo(self,
                nickname: str,
                avatar_url: str,
                message: str,
                appendix: str,
                send_time: str):
        session = self.DbSession()
        info = ReportMessageInfo(nickname=nickname,
                                 avatar_url=avatar_url,
                                 message=message,
                                 appendix=appendix,
                                 send_time=send_time)
        session.add(info)
        session.commit()
        session.close()

    def __del__(self):
        self.engine.dispose()

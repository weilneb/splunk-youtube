from sqlalchemy import Column, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class YoutubeChannel(Base):
    __tablename__ = "channels"

    channel_id = Column(String, primary_key=True)
    playlist_id = Column(String, nullable=False)
    next_token = Column(String)
    next_scheduled_at = Column(DateTime, default=func.now())

    # TODO: timestamp_of_last_video_downloaded

    def __repr__(self):
        return f"<YoutubeChannel(channel_id='{self.channel_id}', playlist_id='{self.playlist_id}', next_token='{self.next_token}')>"


def get_db_engine(path_to_db="db.sqlite"):
    return create_engine(f"sqlite:///{path_to_db}")
    # return create_engine(f"sqlite:///{path_to_db}", echo=True)


# def get_session(engine=None):
#     if engine is None:
#         engine = get_db_engine()
#     return sessionmaker(bind=engine)()


def init_db_tables(db_engine):
    Base.metadata.create_all(db_engine)

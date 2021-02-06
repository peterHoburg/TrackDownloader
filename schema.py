from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Downloads(Base):
    __tablename__ = 'downloads'
    download_id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    track_name = Column(String)
    artist = Column(String)
    url = Column(String)
    downloaded = Column(Boolean)


class DatabaseHandler:
    def __init__(self):
        self.engine = create_engine('sqlite:///Files/data.sqlite')
        self.session = sessionmaker(bind=self.engine)()

    def _create_database(self):
        Base.metadata.create_all(bind=self.engine)

    def query(self, sql_statement):
        return [x for x in self.engine.execute(sql_statement)]

    def commit(self, sql_statement):
        try:
            self.engine.execute(sql_statement)
            self.session.commit()
            return True
        except Exception:
            return False

    def get_all_tracks(self):
        return [x.track_name for x in self.query('SELECT * FROM downloads WHERE downloaded IS NOT NULL')]

    def insert(self, data):
        self.session.add(data)
        self.session.commit()


if __name__ == '__main__':
    database = DatabaseHandler()


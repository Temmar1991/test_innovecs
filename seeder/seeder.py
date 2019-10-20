from sqlalchemy import create_engine, Column, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import Config
import schedule
import time
import datetime
import os

conf = Config()
database_string = f'mysql://{os.environ.get("DATABASE_USER")}:{os.environ.get("DATABASE_PASS")}@{os.environ.get("HOST")}:3306/{os.environ.get("DATABASE")}'
db = create_engine(database_string)
base = declarative_base()


def check_socket(host, port):
    import socket
    from contextlib import closing
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        if sock.connect_ex((host, port)) == 0:
            print("Mysql is running")
            return True
        else:
            print("Mysql is not running...Waiting...")
            return False


def connect():
    try:
        session = sessionmaker(bind=db)
        ses = session()
        base.metadata.create_all(db)
        return ses
    except Exception as e:
        print(e)


class Ticks(base):
    __tablename__ = 'ticks'

    id_entry = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False)

    def __init__(self, createad_at):
        self.created_at = createad_at


def scheduler():
    schedule.every(1).seconds.do(insert_to_table)
    while True:
        schedule.run_pending()
        time.sleep(1)


def insert_to_table():
    now = datetime.datetime.utcnow()
    entry = Ticks(createad_at=now.strftime('%Y-%m-%d %H:%M:%S'))
    session = connect()
    session.add(entry)
    session.commit()
    session.close()


if __name__ == '__main__':
    while True:
        time.sleep(5)
        while check_socket("localhost", 3306):
            time.sleep(3)
            scheduler()




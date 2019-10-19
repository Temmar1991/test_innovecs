import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    DATABASE = os.environ.get('DATABASE')
    DATABASE_USER = os.environ.get('DATABASE_USER')
    DATABASE_PASS = os.environ.get('DATABASE_PASS')
    HOST = os.environ.get('HOST')




import os

class Config:
    SECRET_KEY = 'supersecretkey'  # Change this to a strong, unique key
    SQLALCHEMY_DATABASE_URI = 'sqlite:///blog.db'  # SQLite database
    SQLALCHEMY_TRACK_MODIFICATIONS = False

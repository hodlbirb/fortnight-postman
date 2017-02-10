import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base

# init db
engine = create_engine('sqlite:///email.db')
Base.metadata.bind = engine
SessionFactory = sessionmaker(bind=engine,autoflush=True,autocommit=False)
Session = scoped_session(SessionFactory)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from models import city,image

# sqlite://<nohostname>/<path>
# where <path> is relative:
# data stored in local directory 
engine = create_engine("sqlite:///zolitron.db")

Base = declarative_base()

#create tables 
Base.metadata.create_all(engine)


#session init
Session = sessionmaker(bind=engine,autoflush=False)
session = Session()


def get_db():
    ##init db
    db = Session()
    try:    
    #do stuff (queries)
        yield db
    finally:
        db.close()
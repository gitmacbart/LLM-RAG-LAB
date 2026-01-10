from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    quantity = Column(Integer, default=0)
    category = Column(String)

# Create engine
engine = create_engine('sqlite:///inventory.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
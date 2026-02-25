from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

Base = declarative_base()

# 导入User模型，确保它被包含在Base.metadata中
from auth import User

class TrafficData(Base):
    __tablename__ = "traffic_data"
    
    id = Column(Integer, primary_key=True, index=True)
    intersection_id = Column(String, index=True)
    lane_id = Column(String)
    vehicle_count = Column(Integer)
    average_speed = Column(Float)
    queue_length = Column(Integer)
    status = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class TrafficLight(Base):
    __tablename__ = "traffic_lights"
    
    id = Column(Integer, primary_key=True, index=True)
    intersection_id = Column(String, index=True)
    phase_id = Column(String)
    state = Column(String)  # green, yellow, red
    remaining_time = Column(Integer)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class ControlLog(Base):
    __tablename__ = "control_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    operation = Column(String)
    details = Column(String)
    success = Column(Boolean, default=True)

# 创建内存数据库用于演示
SQLALCHEMY_DATABASE_URL = "sqlite:///./traffic_control.db"
# 在生产环境中，您可能想使用 PostgreSQL 或 MySQL：
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
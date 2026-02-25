from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import datetime
import random
import time
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import jwt
from pydantic import BaseModel
from typing import Optional
import hashlib

app = FastAPI(title='智能交通灯控制系统API', version='1.0.0')

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库配置 (使用SQLite)
DATABASE_URL = "sqlite:///./traffic_users.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# JWT配置
SECRET_KEY = "traffic_light_secret_key_2026"
ALGORITHM = "HS256"

# 安全方案
security = HTTPBearer()

# 数据模型
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

class TrafficData(Base):
    __tablename__ = "traffic_data"
    
    id = Column(Integer, primary_key=True, index=True)
    intersection_id = Column(String, index=True)
    timestamp = Column(String)
    vehicle_count = Column(Integer)
    average_speed = Column(Integer)
    congestion_level = Column(String)
    light_status = Column(String)  # 新增信号灯状态

# Pydantic模型
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TrafficUpdate(BaseModel):
    intersection_id: str
    vehicle_count: int
    average_speed: int
    congestion_level: str
    light_status: str  # 新增信号灯状态字段

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 全局变量存储最新的交通数据（用于实时模拟）
latest_traffic_data = {}
traffic_history = []

# 信号灯控制状态
light_control_state = {
    "current_phase": "north_south",  # 当前相位：north_south 或 east_west
    "phase_start_time": time.time(),  # 相位开始时间
    "yellow_warning_given": False     # 是否已给出黄灯警告
}

def get_time_based_vehicle_count():
    """根据时间段返回合理的车流量"""
    current_hour = datetime.datetime.now().hour
    
    # 定义不同时间段的基础车流量范围
    if 7 <= current_hour <= 9:  # 早高峰 7:00-9:00
        base_min, base_max = 40, 80
    elif 17 <= current_hour <= 19:  # 晚高峰 17:00-19:00
        base_min, base_max = 45, 85
    elif 10 <= current_hour <= 16:  # 白天平峰 10:00-16:00
        base_min, base_max = 20, 50
    elif 20 <= current_hour <= 22:  # 晚间 20:00-22:00
        base_min, base_max = 15, 35
    else:  # 夜间低峰 23:00-6:00
        base_min, base_max = 5, 20
    
    # 添加随机波动（±10%）
    fluctuation = random.uniform(0.9, 1.1)
    vehicle_count = int(random.randint(base_min, base_max) * fluctuation)
    return max(1, min(100, vehicle_count))  # 限制在合理范围内

def get_signal_light_status_and_time():
    """获取信号灯状态和剩余时间，包含黄灯逻辑"""
    global light_control_state
    
    current_time = time.time()
    elapsed_time = current_time - light_control_state["phase_start_time"]
    
    # 信号灯周期配置（秒）
    GREEN_TIME = 30  # 绿灯时间
    YELLOW_TIME = 5   # 黄灯时间
    RED_TIME = 30    # 红灯时间（另一方向的绿灯时间）
    TOTAL_CYCLE = GREEN_TIME + YELLOW_TIME + RED_TIME + YELLOW_TIME  # 完整周期
    
    # 计算当前在周期中的位置
    cycle_position = elapsed_time % TOTAL_CYCLE
    
    # 确定当前相位和状态
    if cycle_position < GREEN_TIME:
        # 北南向绿灯
        light_control_state["current_phase"] = "north_south"
        light_control_state["yellow_warning_given"] = False
        status = "绿灯"
        remaining_time = int(GREEN_TIME - cycle_position)
    elif cycle_position < GREEN_TIME + YELLOW_TIME:
        # 北南向黄灯
        light_control_state["current_phase"] = "north_south"
        if not light_control_state["yellow_warning_given"]:
            light_control_state["yellow_warning_given"] = True
        status = "黄灯"
        remaining_time = int(GREEN_TIME + YELLOW_TIME - cycle_position)
    elif cycle_position < GREEN_TIME + YELLOW_TIME + RED_TIME:
        # 北南向红灯，东西向绿灯
        light_control_state["current_phase"] = "east_west"
        light_control_state["yellow_warning_given"] = False
        status = "红灯"
        remaining_time = int(GREEN_TIME + YELLOW_TIME + RED_TIME - cycle_position)
    else:
        # 东西向黄灯
        light_control_state["current_phase"] = "east_west"
        status = "黄灯"
        remaining_time = int(TOTAL_CYCLE - cycle_position)
    
    return status, remaining_time, light_control_state["current_phase"]

def update_traffic_data(intersection_id: str, data: dict):
    """更新交通数据 - 改进版本，包含黄灯和时间段特性"""
    global latest_traffic_data, traffic_history
    
    # 获取基于时间段的车流量
    vehicle_count = get_time_based_vehicle_count()
    
    # 根据车流量计算拥堵等级
    if vehicle_count > 70:
        congestion_level = "拥堵"
    elif vehicle_count > 40:
        congestion_level = "缓行"
    else:
        congestion_level = "畅通"
    
    # 根据拥堵情况和时间段计算平均速度
    current_hour = datetime.datetime.now().hour
    if congestion_level == "拥堵":
        if 7 <= current_hour <= 9 or 17 <= current_hour <= 19:  # 高峰期更拥堵
            avg_speed = random.randint(8, 18)
        else:
            avg_speed = random.randint(12, 25)
    elif congestion_level == "缓行":
        if 7 <= current_hour <= 9 or 17 <= current_hour <= 19:
            avg_speed = random.randint(15, 28)
        else:
            avg_speed = random.randint(20, 35)
    else:  # 畅通
        if 7 <= current_hour <= 9 or 17 <= current_hour <= 19:
            avg_speed = random.randint(25, 40)
        elif 10 <= current_hour <= 16:
            avg_speed = random.randint(35, 55)
        else:
            avg_speed = random.randint(45, 65)
    
    # 获取信号灯状态和剩余时间（使用改进后的逻辑）
    light_status, remaining_time, current_phase = get_signal_light_status_and_time()
    
    # 构建返回数据
    traffic_data = {
        'timestamp': datetime.datetime.now().isoformat(),
        'vehicle_count': vehicle_count,
        'average_speed': avg_speed,
        'congestion_level': congestion_level,
        'light_status': light_status,
        'remaining_time': remaining_time,
        'current_phase': current_phase
    }
    
    latest_traffic_data[intersection_id] = traffic_data
    
    # 添加到历史记录
    history_entry = {
        'timestamp': datetime.datetime.now().isoformat(),
        'intersection_id': intersection_id,
        'vehicle_count': vehicle_count,
        'average_speed': avg_speed,
        'congestion_level': congestion_level,
        'light_status': light_status,
        'phase': current_phase
    }
    
    traffic_history.append(history_entry)
    
    # 保留最近的100条记录
    if len(traffic_history) > 100:
        traffic_history.pop(0)
    
    return traffic_data

# 依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def get_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, str(user.hashed_password)):
        return False
    return user

def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        username = str(username)  # 显式类型转换
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# 初始化默认用户
def init_default_user():
    db = SessionLocal()
    try:
        # 检查是否已存在用户
        existing_user = db.query(User).first()
        if not existing_user:
            # 创建默认管理员用户
            default_user = User(
                username="admin",
                email="admin@traffic.com",
                hashed_password=get_password_hash("admin123"),
                is_admin=True,
                is_active=True
            )
            db.add(default_user)
            db.commit()
            print("默认用户已创建: admin/admin123")
    finally:
        db.close()

# API路由
@app.get("/")
async def root():
    return {"message": "智能交通灯控制系统API", "version": "1.0.0"}

@app.post("/api/auth/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token, 
        "refresh_token": "",  # 前端可以忽略空的refresh_token
        "token_type": "bearer",
        "message": "登录成功"
    }

@app.get("/api/system/status")
async def get_system_status(current_user: User = Depends(get_current_user)):
    return {
        "status": "running",
        "timestamp": datetime.datetime.now().isoformat(),
        "version": "1.0.0",
        "sensor_status": {
            "sensors": "在线",
            "cameras": "在线",
            "radar": "在线",
            "communication": "在线"
        }
    }

@app.get("/api/traffic/data")
async def get_traffic_data(current_user: User = Depends(get_current_user)):
    """获取实时交通数据"""
    # 每次请求都动态生成数据
    intersections = ["路口A", "路口B", "路口C", "路口D"]
    result = []
    for intersection in intersections:
        update_traffic_data(intersection, {})
        data = latest_traffic_data[intersection]
        # 信号灯周期：绿灯30s→黄灯5s→红灯30s→黄灯5s，总周期70s
        now = int(time.time())
        cycle = now % 70
        # 相位控制：北南为一组，东西为一组
        if cycle < 30:
            ns_status = "绿灯"
            ns_countdown = 30 - cycle
            ew_status = "红灯"
            ew_countdown = 65 - cycle if cycle < 65 else 0
        elif cycle < 35:
            ns_status = "黄灯"
            ns_countdown = 35 - cycle
            ew_status = "红灯"
            ew_countdown = 65 - cycle if cycle < 65 else 0
        elif cycle < 65:
            ns_status = "红灯"
            ns_countdown = 65 - cycle
            ew_status = "绿灯"
            ew_countdown = 65 - cycle
        else:
            ns_status = "红灯"
            ns_countdown = 70 - cycle
            ew_status = "黄灯"
            ew_countdown = 70 - cycle

        lights = {
            "north": {"status": ns_status, "countdown": ns_countdown},
            "south": {"status": ns_status, "countdown": ns_countdown},
            "east": {"status": ew_status, "countdown": ew_countdown},
            "west": {"status": ew_status, "countdown": ew_countdown}
        }
        result.append({
            "intersection_id": intersection,
            "timestamp": data['timestamp'],
            "vehicle_count": data['vehicle_count'],
            "average_speed": data['average_speed'],
            "congestion_level": data['congestion_level'],
            "lights": lights,
            "phase": data.get('phase', '')
        })
    return {"data": result}

@app.post("/api/traffic/update")
async def update_traffic_data_api(
    traffic_data: TrafficUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新交通数据（用于模拟数据注入）"""
    # 保存交通数据到数据库
    db_traffic = TrafficData(
        intersection_id=traffic_data.intersection_id,
        timestamp=datetime.datetime.now().isoformat(),
        vehicle_count=traffic_data.vehicle_count,
        average_speed=traffic_data.average_speed,
        congestion_level=traffic_data.congestion_level,
        light_status=traffic_data.light_status
    )
    db.add(db_traffic)
    db.commit()
    db.refresh(db_traffic)
    
    # 更新实时数据
    update_traffic_data(traffic_data.intersection_id, {
        'vehicle_count': traffic_data.vehicle_count
    })
    
    return {"message": "交通数据更新成功", "data": traffic_data}

@app.get("/api/traffic/simulate")
async def simulate_traffic_data(current_user: User = Depends(get_current_user)):
    """模拟交通数据变化（用于前端轮询）"""
    # 随机选择一个路口进行数据更新
    intersections = list(latest_traffic_data.keys())
    if intersections:
        intersection_id = random.choice(intersections)
        # 随机调整车流量（±10车辆）
        current_count = latest_traffic_data[intersection_id]['vehicle_count']
        new_count = max(10, min(100, current_count + random.randint(-10, 10)))
        
        update_traffic_data(intersection_id, {
            'vehicle_count': new_count
        })
    
    # 返回当前所有数据
    return await get_traffic_data(current_user)

@app.get("/api/user/profile")
async def get_user_profile(current_user: User = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "email": current_user.email,
        "is_admin": current_user.is_admin,
        "is_active": current_user.is_active
    }

if __name__ == "__main__":
    init_default_user()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
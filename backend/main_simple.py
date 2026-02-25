from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import datetime

app = FastAPI(title='智能交通灯控制系统API', version='1.0.0')

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get('/')
async def root():
    return {'message': '智能交通灯控制系统后端服务', 'status': 'running'}

@app.get('/api/traffic/status')
async def get_traffic_status():
    '''获取交通状态（简化版本）'''
    return {
        'intersection_id': 'intersection_001',
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'lanes': [
            {
                'id': 'lane_north_1',
                'direction': 'north',
                'vehicle_count': 15,
                'average_speed': 25.5,
                'queue_length': 3,
                'status': 'normal'
            },
            {
                'id': 'lane_south_1',
                'direction': 'south',
                'vehicle_count': 8,
                'average_speed': 30.2,
                'queue_length': 1,
                'status': 'light'
            }
        ]
    }

@app.get('/api/traffic/light/{intersection_id}')
async def get_traffic_light_status(intersection_id: str):
    '''获取信号灯状态（简化版本）'''
    return {
        'intersection_id': intersection_id,
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'phases': [
            {
                'id': 'phase_1',
                'state': 'green',
                'remaining_time': 25,
                'lane_ids': ['lane_north_1', 'lane_south_1']
            },
            {
                'id': 'phase_2',
                'state': 'red',
                'remaining_time': 0,
                'lane_ids': ['lane_east_1', 'lane_west_1']
            }
        ]
    }

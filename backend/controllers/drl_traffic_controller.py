import numpy as np
try:
    import tensorflow as tf
    # 尝试多种方式导入keras
    try:
        # TensorFlow 2.x 的推荐导入方式
        import tensorflow.keras as keras
    except ImportError:
        try:
            # 备用导入方式
            from tensorflow import keras
        except ImportError:
            try:
                # 独立的 Keras 包
                import keras
            except ImportError:
                raise ImportError("Cannot import Keras. Please install TensorFlow: pip install tensorflow")
    TENSORFLOW_AVAILABLE = True
except ImportError as e:
    print(f"Warning: TensorFlow not available: {e}")
    print("Please install TensorFlow: pip install tensorflow")
    TENSORFLOW_AVAILABLE = False
    # 创建假的模块以避免导入错误
    class FakeModule:
        def __getattr__(self, name):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'. TensorFlow is not installed.")
    tf = FakeModule()
    keras = FakeModule()

import random
import time
import logging
from collections import deque
from typing import Dict, List, Tuple, Optional, Union, Any
import json
import os

logger = logging.getLogger(__name__)

def check_tensorflow_availability() -> bool:
    """
    检查 TensorFlow 是否可用
    
    Returns:
        bool: TensorFlow 是否可用
    """
    if TENSORFLOW_AVAILABLE:
        try:
            # 测试基本功能
            _ = tf.constant([1.0])
            return True
        except Exception as e:
            logger.error(f"TensorFlow available but not functional: {e}")
            return False
    return False

def install_tensorflow_instructions() -> str:
    """
    返回安装 TensorFlow 的指令
    
    Returns:
        str: 安装指令
    """
    return (
        "Please install TensorFlow using one of these methods:\n"
        "1. pip install tensorflow\n"
        "2. Run the installation script: python install_deps.py\n"
        "3. For GPU support: pip install tensorflow[and-cuda]"
    )

class DRLTrafficController:
    """
    基于深度强化学习的交通信号控制器
    使用Deep Q-Network (DQN)算法进行交通信号优化控制
    """
    
    def __init__(self, intersection_id: str, model_path: Optional[str] = None):
        if not TENSORFLOW_AVAILABLE:
            raise RuntimeError(
                "TensorFlow is required for DRLTrafficController. "
                "Please install it with: pip install tensorflow\n"
                "Or run the install script: python install_deps.py"
            )
        
        self.intersection_id = intersection_id
        self.model_path = model_path or os.path.join(os.path.dirname(__file__), 'models')
        os.makedirs(self.model_path, exist_ok=True)
        
        # DQN超参数
        self.learning_rate = 0.001
        self.gamma = 0.95  # 折扣因子
        self.epsilon = 1.0  # 探索率
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.batch_size = 32
        self.memory_size = 10000
        
        # 经验回放缓冲区
        self.memory = deque(maxlen=self.memory_size)
        
        # 交通控制参数
        self.min_green_time = 15  # 最小绿灯时间（秒）
        self.max_green_time = 120  # 最大绿灯时间（秒）
        self.yellow_time = 3  # 黄灯时间（秒）
        self.all_red_time = 2  # 全红时间（秒）
        
        # 相位定义
        self.phases = {
            0: {'name': 'North-South Straight', 'directions': ['north_straight', 'south_straight']},
            1: {'name': 'East-West Straight', 'directions': ['east_straight', 'west_straight']},
            2: {'name': 'North-South Left', 'directions': ['north_left', 'south_left']},
            3: {'name': 'East-West Left', 'directions': ['east_left', 'west_left']}
        }
        
        # 当前状态
        self.current_phase = 0
        self.phase_timer = 0
        self.phase_start_time = time.time()
        self.total_wait_time = 0
        self.vehicle_count_history = []
        
        # 神经网络模型
        self.q_network: Optional[Any] = None
        self.target_network: Optional[Any] = None
        self._build_model()
        
        # 加载预训练模型（如果存在）
        self._load_model()
        
        logger.info(f"DRLTrafficController initialized for intersection {intersection_id}")
    
    def _build_model(self):
        """构建深度Q网络"""
        try:
            # 输入层：状态特征 [车流量, 等待时间, 当前相位, 时间信息]
            input_layer = keras.layers.Input(shape=(self._get_state_size(),))
            
            # 隐藏层
            x = keras.layers.Dense(128, activation='relu')(input_layer)  # type: ignore
            x = keras.layers.BatchNormalization()(x)  # type: ignore
            x = keras.layers.Dropout(0.2)(x)  # type: ignore
            
            x = keras.layers.Dense(64, activation='relu')(x)  # type: ignore
            x = keras.layers.BatchNormalization()(x)  # type: ignore
            x = keras.layers.Dropout(0.2)(x)  # type: ignore
            
            x = keras.layers.Dense(32, activation='relu')(x)  # type: ignore
            
            # 输出层：每个动作的Q值
            output_layer = keras.layers.Dense(len(self.phases), activation='linear')(x)  # type: ignore
            
            self.q_network = keras.Model(inputs=input_layer, outputs=output_layer)
            self.target_network = keras.Model(inputs=input_layer, outputs=output_layer)
            
            # 编译模型
            if self.q_network is not None:
                optimizer = keras.optimizers.Adam(learning_rate=self.learning_rate)
                self.q_network.compile(optimizer=optimizer, loss='mse')
            
            # 同步目标网络
            if self.q_network is not None and self.target_network is not None:
                self.target_network.set_weights(self.q_network.get_weights())
            
            logger.info("DQN model built successfully")
            
        except Exception as e:
            logger.error(f"Failed to build DQN model: {e}")
            raise
    
    def _get_state_size(self) -> int:
        """返回状态向量的维度"""
        # [各方向车流量, 各方向平均等待时间, 当前相位, 时间信息]
        return len(self.phases) * 2 + 2
    
    def _get_state(self, traffic_data: Dict) -> np.ndarray:
        """将交通数据转换为状态向量"""
        state = []
        
        # 各方向车流量
        directions = ['north', 'south', 'east', 'west']
        for direction in directions:
            straight_flow = traffic_data.get(f'{direction}_straight', 0)
            left_flow = traffic_data.get(f'{direction}_left', 0)
            state.extend([straight_flow, left_flow])
        
        # 各方向平均等待时间
        for direction in directions:
            straight_wait = traffic_data.get(f'{direction}_straight_wait', 0)
            left_wait = traffic_data.get(f'{direction}_left_wait', 0)
            state.extend([straight_wait, left_wait])
        
        # 当前相位
        phase_one_hot = [0] * len(self.phases)
        phase_one_hot[self.current_phase] = 1
        state.extend(phase_one_hot)
        
        # 时间信息（归一化到[0,1]）
        time_normalized = (time.time() % 3600) / 3600  # 小时内的相对时间
        state.append(time_normalized)
        
        return np.array(state, dtype=np.float32)
    
    def _choose_action(self, state: np.ndarray) -> int:
        """根据ε-greedy策略选择动作"""
        if random.random() <= self.epsilon:
            # 探索：随机选择动作
            return random.randint(0, len(self.phases) - 1)
        else:
            # 利用：选择Q值最大的动作
            if self.q_network is not None:
                q_values = self.q_network.predict(state.reshape(1, -1), verbose='0')
                return int(np.argmax(q_values[0]))
            else:
                return 0
    
    def _remember(self, state: np.ndarray, action: int, reward: float, 
                  next_state: np.ndarray, done: bool):
        """存储经验到回放缓冲区"""
        self.memory.append((state, action, reward, next_state, done))
    
    def _replay(self):
        """从经验回放中学习"""
        if len(self.memory) < self.batch_size or self.q_network is None or self.target_network is not None:
            return
        
        # 随机采样一批经验
        batch = random.sample(self.memory, self.batch_size)
        states = np.array([e[0] for e in batch])
        actions = np.array([e[1] for e in batch])
        rewards = np.array([e[2] for e in batch])
        next_states = np.array([e[3] for e in batch])
        dones = np.array([e[4] for e in batch])
        
        # 计算目标Q值
        if self.q_network is not None and self.target_network is not None:
            current_q_values = self.q_network.predict(states, verbose='0')
            next_q_values = self.target_network.predict(next_states, verbose='0')
        else:
            return
        
        # 更新Q值
        for i in range(self.batch_size):
            if dones[i]:
                current_q_values[i][actions[i]] = rewards[i]
            else:
                current_q_values[i][actions[i]] = rewards[i] + self.gamma * np.max(next_q_values[i])
        
        # 训练网络
        if self.q_network is not None:
            self.q_network.fit(states, current_q_values, epochs=1, verbose='0')
        
        # 降低探索率
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def _update_target_network(self):
        """更新目标网络权重"""
        if self.q_network is not None and self.target_network is not None:
            self.target_network.set_weights(self.q_network.get_weights())
    
    def calculate_reward(self, traffic_data: Dict) -> float:
        """计算奖励函数"""
        # 奖励基于减少的等待时间和提高的通行效率
        total_waiting_time = sum([
            traffic_data.get('north_straight_wait', 0),
            traffic_data.get('south_straight_wait', 0),
            traffic_data.get('east_straight_wait', 0),
            traffic_data.get('west_straight_wait', 0),
            traffic_data.get('north_left_wait', 0),
            traffic_data.get('south_left_wait', 0),
            traffic_data.get('east_left_wait', 0),
            traffic_data.get('west_left_wait', 0)
        ])
        
        # 负奖励（等待时间越少越好）
        reward = -total_waiting_time * 0.1
        
        # 正奖励（车辆通过数量）
        vehicles_passed = sum([
            traffic_data.get('north_straight_passed', 0),
            traffic_data.get('south_straight_passed', 0),
            traffic_data.get('east_straight_passed', 0),
            traffic_data.get('west_straight_passed', 0),
            traffic_data.get('north_left_passed', 0),
            traffic_data.get('south_left_passed', 0),
            traffic_data.get('east_left_passed', 0),
            traffic_data.get('west_left_passed', 0)
        ])
        reward += vehicles_passed * 0.5
        
        return reward
    
    def get_next_phase(self, traffic_data: Dict) -> Tuple[int, int]:
        """
        根据当前交通状况决定下一个相位和持续时间
        
        Args:
            traffic_data: 包含各方向车流量和等待时间的字典
            
        Returns:
            tuple: (next_phase, duration_seconds)
        """
        try:
            # 获取当前状态
            current_state = self._get_state(traffic_data)
            
            # 选择动作
            action = self._choose_action(current_state)
            
            # 执行动作并获得奖励
            reward = self.calculate_reward(traffic_data)
            
            # 获取下一个状态（模拟）
            next_state = self._simulate_next_state(current_state, action, traffic_data)
            
            # 存储经验
            done = False  # 交通控制是连续过程
            self._remember(current_state, action, reward, next_state, done)
            
            # 学习
            self._replay()
            
            # 决定相位持续时间
            duration = self._calculate_phase_duration(action, traffic_data)
            
            logger.debug(f"DRL Controller - Phase: {action}, Duration: {duration}s, Reward: {reward:.2f}")
            
            return action, duration
            
        except Exception as e:
            logger.error(f"Error in DRL controller decision: {e}")
            # 回退到默认策略
            return self.current_phase, self.min_green_time
    
    def _simulate_next_state(self, current_state: np.ndarray, action: int, 
                           traffic_data: Dict) -> np.ndarray:
        """模拟执行动作后的下一个状态"""
        # 简化的状态转移模拟
        next_state = current_state.copy()
        
        # 更新相位信息
        phase_start_idx = len(self.phases) * 2  # 相位信息在状态向量中的起始位置
        next_state[phase_start_idx:phase_start_idx + len(self.phases)] = 0
        next_state[phase_start_idx + action] = 1
        
        # 模拟车流量变化（简化）
        flow_change_factor = 0.9  # 假设相位切换后车流减少
        for i in range(len(self.phases) * 2):
            next_state[i] *= flow_change_factor
            
        return next_state
    
    def _calculate_phase_duration(self, phase: int, traffic_data: Dict) -> int:
        """根据交通状况计算相位持续时间"""
        # 基于该相位方向的车流量决定持续时间
        phase_directions = self.phases[phase]['directions']
        total_flow = 0
        
        for direction in phase_directions:
            flow_key = f"{direction.replace('_straight', '').replace('_left', '')}_{direction.split('_')[1] if '_' in direction else 'straight'}"
            total_flow += traffic_data.get(flow_key, 0)
        
        # 动态调整持续时间
        base_duration = self.min_green_time
        flow_factor = min(total_flow / 20.0, 2.0)  # 最多延长2倍
        duration = int(base_duration * (1 + flow_factor))
        duration = max(self.min_green_time, min(duration, self.max_green_time))
        
        return duration
    
    def update_stats(self, traffic_data: Dict):
        """更新统计信息"""
        # 记录历史数据用于分析
        timestamp = time.time()
        stats = {
            'timestamp': timestamp,
            'current_phase': self.current_phase,
            'vehicle_counts': {
                'north_straight': traffic_data.get('north_straight', 0),
                'south_straight': traffic_data.get('south_straight', 0),
                'east_straight': traffic_data.get('east_straight', 0),
                'west_straight': traffic_data.get('west_straight', 0),
                'north_left': traffic_data.get('north_left', 0),
                'south_left': traffic_data.get('south_left', 0),
                'east_left': traffic_data.get('east_left', 0),
                'west_left': traffic_data.get('west_left', 0)
            },
            'waiting_times': {
                'north_straight_wait': traffic_data.get('north_straight_wait', 0),
                'south_straight_wait': traffic_data.get('south_straight_wait', 0),
                'east_straight_wait': traffic_data.get('east_straight_wait', 0),
                'west_straight_wait': traffic_data.get('west_straight_wait', 0),
                'north_left_wait': traffic_data.get('north_left_wait', 0),
                'south_left_wait': traffic_data.get('south_left_wait', 0),
                'east_left_wait': traffic_data.get('east_left_wait', 0),
                'west_left_wait': traffic_data.get('west_left_wait', 0)
            }
        }
        
        self.vehicle_count_history.append(stats)
        
        # 保持最近100条记录
        if len(self.vehicle_count_history) > 100:
            self.vehicle_count_history.pop(0)
    
    def save_model(self, filepath: Optional[str] = None):
        """保存训练好的模型"""
        try:
            if filepath is None:
                filepath = os.path.join(self.model_path, f'drl_model_{self.intersection_id}.h5')
            
            if self.q_network is not None:
                self.q_network.save(filepath)
                logger.info(f"Model saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    def _load_model(self, filepath: Optional[str] = None):
        """加载预训练模型"""
        try:
            if filepath is None:
                filepath = os.path.join(self.model_path, f'drl_model_{self.intersection_id}.h5')
            
            if os.path.exists(filepath) and self.q_network is not None:
                self.q_network = keras.models.load_model(filepath)
                self.target_network = keras.models.clone_model(self.q_network)
                if self.q_network is not None and self.target_network is not None:
                    self.target_network.set_weights(self.q_network.get_weights())
                logger.info(f"Model loaded from {filepath}")
            else:
                logger.info("No pre-trained model found, using newly initialized model")
                
        except Exception as e:
            logger.warning(f"Failed to load model: {e}, using default initialization")
    
    def get_performance_metrics(self) -> Dict:
        """获取控制器性能指标"""
        if not self.vehicle_count_history:
            return {}
        
        recent_data = self.vehicle_count_history[-20:]  # 最近20个时间点
        
        # 计算平均等待时间
        avg_waiting_time = np.mean([
            sum(item['waiting_times'].values()) for item in recent_data
        ])
        
        # 计算总车流量
        total_vehicles = sum([
            sum(item['vehicle_counts'].values()) for item in recent_data
        ])
        
        return {
            'average_waiting_time': float(avg_waiting_time),
            'total_vehicles_processed': total_vehicles,
            'exploration_rate': self.epsilon,
            'memory_size': len(self.memory)
        }

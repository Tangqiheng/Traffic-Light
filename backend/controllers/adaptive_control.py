import numpy as np
import random
import time
from collections import defaultdict
import logging
from typing import Dict, List, Tuple
import json
import os

logger = logging.getLogger(__name__)

class AdaptiveTrafficController:
    def __init__(self, intersection_id: str, model_path: str = None):
        self.intersection_id = intersection_id
        self.model_path = model_path or os.path.join(os.path.dirname(__file__), 'models')
        os.makedirs(self.model_path, exist_ok=True)
        
        # Q-Learning参数
        self.alpha = 0.1  # 学习率
        self.gamma = 0.9  # 折扣因子
        self.epsilon = 0.1  # 探索率
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        
        # 交通灯控制参数
        self.min_green_time = 10  # 最小绿灯时间（秒）
        self.max_green_time = 120  # 最大绿灯时间（秒）
        self.yellow_time = 3  # 黄灯时间（秒）
        self.all_red_time = 2  # 全红时间（秒）
        
        # 相位定义（十字路口）
        self.phases = {
            0: {'name': 'North-South', 'directions': ['north', 'south']},
            1: {'name': 'East-West', 'directions': ['east', 'west']},
            2: {'name': 'North-Left', 'directions': ['north_left']},
            3: {'name': 'East-Left', 'directions': ['east_left']},
            4: {'name': 'South-Left', 'directions': ['south_left']},
            5: {'name': 'West-Left', 'directions': ['west_left']}
        }
        
        # 当前状态
        self.current_phase = 0
        self.phase_timer = 0
        self.phase_start_time = time.time()
        
        # Q表
        self.q_table = defaultdict(lambda: defaultdict(float))
        
        # 状态和动作空间
        self.state_space = self._define_state_space()
        self.action_space = self._define_action_space()
        
        # 历史数据
        self.control_history = []
        
        # 加载模型
        self._load_model()
    
    def _define_state_space(self) -> List[str]:
        """定义状态空间"""
        # 状态基于各方向的拥堵等级和当前相位
        congestion_levels = ['low', 'medium', 'high']
        phases = list(self.phases.keys())
        
        states = []
        for n_cong in congestion_levels:
            for s_cong in congestion_levels:
                for e_cong in congestion_levels:
                    for w_cong in congestion_levels:
                        for phase in phases:
                            state = f"{n_cong}_{s_cong}_{e_cong}_{w_cong}_{phase}"
                            states.append(state)
        return states
    
    def _define_action_space(self) -> List[str]:
        """定义动作空间"""
        # 动作：改变绿灯时间或切换相位
        actions = []
        
        # 绿灯时间调整动作
        for time_change in [-10, -5, 0, 5, 10]:  # 时间变化（秒）
            actions.append(f"extend_{time_change}")
        
        # 相位切换动作
        for phase in self.phases.keys():
            actions.append(f"switch_to_{phase}")
        
        # 特殊动作
        actions.extend(['emergency_stop', 'night_mode'])
        
        return actions
    
    def _load_model(self):
        """加载Q表"""
        try:
            model_file = os.path.join(self.model_path, f'q_table_{self.intersection_id}.json')
            if os.path.exists(model_file):
                with open(model_file, 'r') as f:
                    self.q_table = defaultdict(lambda: defaultdict(float), json.load(f))
                logger.info("加载Q-Learning模型成功")
            else:
                logger.info("未找到现有模型，将从零开始学习")
        except Exception as e:
            logger.error(f"加载模型失败: {e}")
    
    def _save_model(self):
        """保存Q表"""
        try:
            model_file = os.path.join(self.model_path, f'q_table_{self.intersection_id}.json')
            # 转换为普通字典以便JSON序列化
            q_table_dict = {state: dict(actions) for state, actions in self.q_table.items()}
            
            with open(model_file, 'w') as f:
                json.dump(q_table_dict, f, indent=2)
            
            logger.info("Q-Learning模型保存成功")
        except Exception as e:
            logger.error(f"保存模型失败: {e}")
    
    def get_current_state(self, traffic_data: Dict) -> str:
        """根据交通数据获取当前状态"""
        try:
            lanes = traffic_data.get('lanes', {})
            
            # 计算各方向的拥堵等级
            direction_congestion = {}
            for direction in ['north', 'south', 'east', 'west']:
                dir_lanes = [lane for lane in lanes.values() if lane.get('direction') == direction]
                if dir_lanes:
                    avg_congestion = np.mean([lane.get('congestion_level', 0.5) for lane in dir_lanes])
                    
                    if avg_congestion < 0.3:
                        congestion_level = 'low'
                    elif avg_congestion < 0.7:
                        congestion_level = 'medium'
                    else:
                        congestion_level = 'high'
                else:
                    congestion_level = 'low'
                
                direction_congestion[direction] = congestion_level
            
            # 构建状态字符串
            state = f"{direction_congestion['north']}_{direction_congestion['south']}_" \
                   f"{direction_congestion['east']}_{direction_congestion['west']}_" \
                   f"{self.current_phase}"
            
            return state
            
        except Exception as e:
            logger.error(f"获取当前状态失败: {e}")
            return f"low_low_low_low_{self.current_phase}"
    
    def choose_action(self, state: str) -> str:
        """选择动作（ε-贪婪策略）"""
        if random.random() < self.epsilon:
            # 探索：随机选择动作
            action = random.choice(self.action_space)
        else:
            # 利用：选择Q值最大的动作
            state_actions = self.q_table[state]
            if state_actions:
                action = max(state_actions, key=state_actions.get)
            else:
                action = random.choice(self.action_space)
        
        return action
    
    def execute_action(self, action: str) -> Dict:
        """执行动作"""
        try:
            if action.startswith('extend_'):
                # 调整绿灯时间
                time_change = int(action.split('_')[1])
                new_green_time = max(self.min_green_time, 
                                   min(self.max_green_time, 
                                       self._get_current_green_time() + time_change))
                
                result = {
                    'action_type': 'time_adjustment',
                    'time_change': time_change,
                    'new_green_time': new_green_time,
                    'current_phase': self.current_phase
                }
                
            elif action.startswith('switch_to_'):
                # 切换相位
                new_phase = int(action.split('_')[2])
                if new_phase != self.current_phase:
                    self._switch_phase(new_phase)
                    result = {
                        'action_type': 'phase_switch',
                        'old_phase': self.current_phase,
                        'new_phase': new_phase,
                        'switch_time': time.time()
                    }
                    self.current_phase = new_phase
                else:
                    result = {
                        'action_type': 'no_change',
                        'reason': 'already_in_phase'
                    }
                    
            elif action == 'emergency_stop':
                # 紧急停车（所有方向红灯）
                result = {
                    'action_type': 'emergency',
                    'emergency_type': 'all_red'
                }
                
            elif action == 'night_mode':
                # 夜间模式（黄闪）
                result = {
                    'action_type': 'night_mode',
                    'flash_interval': 1.0
                }
            else:
                result = {
                    'action_type': 'unknown',
                    'action': action
                }
            
            # 记录控制历史
            self.control_history.append({
                'timestamp': time.time(),
                'action': action,
                'result': result
            })
            
            return result
            
        except Exception as e:
            logger.error(f"执行动作失败: {e}")
            return {'action_type': 'error', 'error': str(e)}
    
    def _get_current_green_time(self) -> int:
        """获取当前绿灯剩余时间"""
        elapsed = time.time() - self.phase_start_time
        remaining = max(0, self.phase_timer - elapsed)
        return int(remaining)
    
    def _switch_phase(self, new_phase: int):
        """切换到新相位"""
        # 这里应该包含黄灯和全红过渡逻辑
        logger.info(f"切换相位: {self.current_phase} -> {new_phase}")
        self.phase_start_time = time.time()
        self.phase_timer = self.min_green_time  # 重置定时器
    
    def calculate_reward(self, old_state: str, action: str, new_state: str, 
                        traffic_data: Dict) -> float:
        """计算奖励函数"""
        try:
            # 解析状态
            old_congestion = self._parse_state_congestion(old_state)
            new_congestion = self._parse_state_congestion(new_state)
            
            # 奖励基于拥堵减少和等待时间减少
            congestion_improvement = old_congestion - new_congestion
            
            # 获取交通统计数据
            overall_status = traffic_data.get('overall_status', {})
            total_vehicles = overall_status.get('total_vehicles', 0)
            avg_speed = overall_status.get('average_speed', 30)
            
            # 奖励计算
            reward = 0
            
            # 拥堵改善奖励
            reward += congestion_improvement * 10
            
            # 速度奖励（鼓励更高平均速度）
            if avg_speed > 40:
                reward += 5
            elif avg_speed < 20:
                reward -= 5
            
            # 车辆通行奖励
            if total_vehicles < 10:
                reward += 2  # 畅通奖励
            elif total_vehicles > 30:
                reward -= 10  # 拥堵惩罚
            
            # 动作惩罚（避免频繁切换）
            if action.startswith('switch_to_'):
                reward -= 2  # 切换相位有一定惩罚
            
            # 紧急动作惩罚
            if action in ['emergency_stop']:
                reward -= 20
            
            return reward
            
        except Exception as e:
            logger.error(f"计算奖励失败: {e}")
            return 0.0
    
    def _parse_state_congestion(self, state: str) -> float:
        """解析状态中的拥堵等级"""
        parts = state.split('_')
        if len(parts) < 5:
            return 0.5
        
        congestion_map = {'low': 0.2, 'medium': 0.5, 'high': 0.8}
        direction_congestion = [congestion_map.get(parts[i], 0.5) for i in range(4)]
        
        return np.mean(direction_congestion)
    
    def update_q_table(self, old_state: str, action: str, reward: float, new_state: str):
        """更新Q表"""
        try:
            # Q-Learning更新公式
            old_q = self.q_table[old_state][action]
            
            # 获取新状态的最大Q值
            new_state_actions = self.q_table[new_state]
            max_new_q = max(new_state_actions.values()) if new_state_actions else 0
            
            # 更新Q值
            new_q = old_q + self.alpha * (reward + self.gamma * max_new_q - old_q)
            self.q_table[old_state][action] = new_q
            
            # 衰减探索率
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
            
        except Exception as e:
            logger.error(f"更新Q表失败: {e}")
    
    def control_step(self, traffic_data: Dict) -> Dict:
        """执行一个控制步骤"""
        try:
            # 获取当前状态
            current_state = self.get_current_state(traffic_data)
            
            # 选择动作
            action = self.choose_action(current_state)
            
            # 执行动作
            action_result = self.execute_action(action)
            
            # 等待一小段时间模拟交通变化
            time.sleep(0.1)
            
            # 获取新状态（这里简化，实际应该等待传感器数据更新）
            new_state = self.get_current_state(traffic_data)
            
            # 计算奖励
            reward = self.calculate_reward(current_state, action, new_state, traffic_data)
            
            # 更新Q表
            self.update_q_table(current_state, action, reward, new_state)
            
            # 定期保存模型
            if len(self.control_history) % 100 == 0:
                self._save_model()
            
            return {
                'state': current_state,
                'action': action,
                'reward': reward,
                'new_state': new_state,
                'action_result': action_result,
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"控制步骤执行失败: {e}")
            return {'error': str(e)}
    
    def get_control_status(self) -> Dict:
        """获取控制状态"""
        return {
            'current_phase': self.current_phase,
            'phase_name': self.phases[self.current_phase]['name'],
            'remaining_time': self._get_current_green_time(),
            'total_actions': len(self.control_history),
            'epsilon': self.epsilon,
            'q_table_size': len(self.q_table)
        }
    
    def reset_controller(self):
        """重置控制器"""
        self.current_phase = 0
        self.phase_timer = self.min_green_time
        self.phase_start_time = time.time()
        self.control_history.clear()
        logger.info("交通灯控制器已重置")

# 基于规则的交通灯控制器（作为备选）
class RuleBasedTrafficController:
    def __init__(self, intersection_id: str):
        self.intersection_id = intersection_id
        
        # 固定配时方案
        self.phase_timings = {
            0: 30,  # North-South
            1: 25,  # East-West
            2: 15,  # North-Left
            3: 15,  # East-Left
            4: 15,  # South-Left
            5: 15   # West-Left
        }
        
        self.current_phase = 0
        self.phase_start_time = time.time()
        self.yellow_time = 3
        self.all_red_time = 2
    
    def control_step(self, traffic_data: Dict) -> Dict:
        """基于规则的控制步骤"""
        current_time = time.time()
        elapsed = current_time - self.phase_start_time
        
        # 检查是否需要切换相位
        current_timing = self.phase_timings[self.current_phase]
        
        if elapsed >= current_timing:
            # 切换到下一个相位
            old_phase = self.current_phase
            self.current_phase = (self.current_phase + 1) % len(self.phase_timings)
            self.phase_start_time = current_time
            
            return {
                'action': f'switch_to_{self.current_phase}',
                'old_phase': old_phase,
                'new_phase': self.current_phase,
                'reason': 'timing_cycle'
            }
        
        return {
            'action': 'maintain_current',
            'current_phase': self.current_phase,
            'remaining_time': current_timing - elapsed
        }
    
    def get_control_status(self) -> Dict:
        """获取控制状态"""
        elapsed = time.time() - self.phase_start_time
        remaining = max(0, self.phase_timings[self.current_phase] - elapsed)
        
        return {
            'current_phase': self.current_phase,
            'remaining_time': remaining,
            'control_type': 'rule_based'
        }

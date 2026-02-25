import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os
import time
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class TrafficStateClassifier:
    def __init__(self, model_path: str = None):
        self.model_path = model_path or os.path.join(os.path.dirname(__file__), 'models')
        os.makedirs(self.model_path, exist_ok=True)
        
        self.scaler = StandardScaler()
        self.classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        # 交通状态类别
        self.classes = ['free', 'normal', 'congested', 'heavy_congested']
        self.class_labels = {cls: i for i, cls in enumerate(self.classes)}
        
        # 特征名称
        self.feature_names = [
            'queue_length', 'average_speed', 'occupancy_rate', 'traffic_density',
            'flow_rate', 'speed_variance', 'direction_balance'
        ]
        
        # 加载或训练模型
        self._load_or_train_model()
    
    def _load_or_train_model(self):
        """加载现有模型或训练新模型"""
        model_file = os.path.join(self.model_path, 'traffic_classifier.pkl')
        scaler_file = os.path.join(self.model_path, 'scaler.pkl')
        
        if os.path.exists(model_file) and os.path.exists(scaler_file):
            try:
                self.classifier = joblib.load(model_file)
                self.scaler = joblib.load(scaler_file)
                logger.info("加载现有交通状态分类模型")
            except Exception as e:
                logger.warning(f"加载模型失败: {e}，将重新训练")
                self._train_default_model()
        else:
            logger.info("未找到现有模型，开始训练默认模型")
            self._train_default_model()
    
    def _train_default_model(self):
        """训练默认模型"""
        # 生成合成训练数据
        X, y = self._generate_training_data()
        
        # 数据预处理
        X_scaled = self.scaler.fit_transform(X)
        
        # 训练模型
        self.classifier.fit(X_scaled, y)
        
        # 保存模型
        self._save_model()
        
        logger.info("默认交通状态分类模型训练完成")
    
    def _generate_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """生成合成训练数据"""
        n_samples = 10000
        
        data = []
        labels = []
        
        for _ in range(n_samples):
            # 生成不同交通状态的特征
            state = np.random.choice(self.classes, p=[0.4, 0.4, 0.15, 0.05])
            
            if state == 'free':
                queue_length = np.random.uniform(0, 3)
                avg_speed = np.random.uniform(35, 60)
                occupancy = np.random.uniform(0, 0.1)
                density = np.random.uniform(0, 0.1)
            elif state == 'normal':
                queue_length = np.random.uniform(2, 8)
                avg_speed = np.random.uniform(25, 45)
                occupancy = np.random.uniform(0.05, 0.25)
                density = np.random.uniform(0.05, 0.25)
            elif state == 'congested':
                queue_length = np.random.uniform(6, 15)
                avg_speed = np.random.uniform(10, 25)
                occupancy = np.random.uniform(0.2, 0.5)
                density = np.random.uniform(0.2, 0.5)
            else:  # heavy_congested
                queue_length = np.random.uniform(12, 25)
                avg_speed = np.random.uniform(0, 15)
                occupancy = np.random.uniform(0.4, 0.8)
                density = np.random.uniform(0.4, 0.8)
            
            # 添加其他特征
            flow_rate = np.random.uniform(0, 50)  # 车流量
            speed_variance = np.random.uniform(0, 20)  # 速度方差
            direction_balance = np.random.uniform(0.3, 1.0)  # 方向平衡度
            
            features = [
                queue_length, avg_speed, occupancy, density,
                flow_rate, speed_variance, direction_balance
            ]
            
            data.append(features)
            labels.append(self.class_labels[state])
        
        return np.array(data), np.array(labels)
    
    def _save_model(self):
        """保存模型"""
        try:
            model_file = os.path.join(self.model_path, 'traffic_classifier.pkl')
            scaler_file = os.path.join(self.model_path, 'scaler.pkl')
            
            joblib.dump(self.classifier, model_file)
            joblib.dump(self.scaler, scaler_file)
            
            logger.info("模型保存成功")
        except Exception as e:
            logger.error(f"模型保存失败: {e}")
    
    def classify_traffic_state(self, features: Dict) -> Dict:
        """分类交通状态"""
        try:
            # 提取特征
            feature_vector = self._extract_features(features)
            
            # 标准化特征
            feature_scaled = self.scaler.transform([feature_vector])
            
            # 预测
            prediction = self.classifier.predict(feature_scaled)[0]
            probabilities = self.classifier.predict_proba(feature_scaled)[0]
            
            # 获取预测类别
            predicted_class = self.classes[prediction]
            confidence = probabilities[prediction]
            
            # 计算拥堵等级
            congestion_level = self._calculate_congestion_level(predicted_class, features)
            
            return {
                'traffic_state': predicted_class,
                'confidence': float(confidence),
                'congestion_level': congestion_level,
                'probabilities': {
                    cls: float(prob) for cls, prob in zip(self.classes, probabilities)
                }
            }
            
        except Exception as e:
            logger.error(f"交通状态分类失败: {e}")
            return {
                'traffic_state': 'unknown',
                'confidence': 0.0,
                'congestion_level': 0.5,
                'probabilities': {cls: 0.0 for cls in self.classes}
            }
    
    def _extract_features(self, features: Dict) -> List[float]:
        """从输入特征中提取模型需要的特征"""
        return [
            features.get('queue_length', 0),
            features.get('average_speed', 30),
            features.get('occupancy_rate', 0),
            features.get('traffic_density', 0),
            features.get('flow_rate', 0),
            features.get('speed_variance', 0),
            features.get('direction_balance', 0.5)
        ]
    
    def _calculate_congestion_level(self, traffic_state: str, features: Dict) -> float:
        """计算拥堵等级"""
        base_levels = {
            'free': 0.0,
            'normal': 0.2,
            'congested': 0.6,
            'heavy_congested': 1.0
        }
        
        base_level = base_levels.get(traffic_state, 0.5)
        
        # 根据实际特征调整拥堵等级
        queue_factor = min(features.get('queue_length', 0) / 20.0, 1.0)
        speed_factor = max(0, (50 - features.get('average_speed', 30)) / 50.0)
        
        adjusted_level = base_level + 0.2 * (queue_factor + speed_factor) / 2
        return min(adjusted_level, 1.0)
    
    def update_model(self, new_data: List[Dict]):
        """使用新数据更新模型"""
        try:
            # 转换新数据为训练格式
            X_new = []
            y_new = []
            
            for sample in new_data:
                features = self._extract_features(sample)
                label = self.class_labels.get(sample.get('true_state', 'normal'), 1)
                
                X_new.append(features)
                y_new.append(label)
            
            if not X_new:
                logger.warning("没有有效的新数据用于更新模型")
                return
            
            # 增量学习（简化版本）
            X_new_scaled = self.scaler.transform(X_new)
            self.classifier.fit(X_new_scaled, y_new)
            
            # 保存更新后的模型
            self._save_model()
            
            logger.info(f"模型已使用 {len(X_new)} 个新样本更新")
            
        except Exception as e:
            logger.error(f"模型更新失败: {e}")
    
    def evaluate_model(self, test_data: List[Dict]) -> Dict:
        """评估模型性能"""
        try:
            X_test = []
            y_true = []
            
            for sample in test_data:
                features = self._extract_features(sample)
                true_label = self.class_labels.get(sample.get('true_state', 'normal'), 1)
                
                X_test.append(features)
                y_true.append(true_label)
            
            X_test_scaled = self.scaler.transform(X_test)
            y_pred = self.classifier.predict(X_test_scaled)
            
            accuracy = accuracy_score(y_true, y_pred)
            report = classification_report(y_true, y_pred, 
                                        target_names=self.classes, 
                                        output_dict=True)
            
            return {
                'accuracy': accuracy,
                'classification_report': report
            }
            
        except Exception as e:
            logger.error(f"模型评估失败: {e}")
            return {'accuracy': 0.0, 'classification_report': {}}

# 简化的交通状态分类器（基于规则）
class RuleBasedTrafficClassifier:
    def __init__(self):
        self.thresholds = {
            'free': {'queue_max': 3, 'speed_min': 35, 'occupancy_max': 0.1},
            'normal': {'queue_max': 8, 'speed_min': 25, 'occupancy_max': 0.25},
            'congested': {'queue_max': 15, 'speed_min': 15, 'occupancy_max': 0.5},
            'heavy_congested': {'queue_max': float('inf'), 'speed_min': 0, 'occupancy_max': 1.0}
        }
    
    def classify_traffic_state(self, features: Dict) -> Dict:
        """基于规则的交通状态分类"""
        queue_length = features.get('queue_length', 0)
        avg_speed = features.get('average_speed', 30)
        occupancy = features.get('occupancy_rate', 0)
        
        # 按优先级检查条件
        if (queue_length <= self.thresholds['free']['queue_max'] and
            avg_speed >= self.thresholds['free']['speed_min'] and
            occupancy <= self.thresholds['free']['occupancy_max']):
            state = 'free'
        elif (queue_length <= self.thresholds['normal']['queue_max'] and
              avg_speed >= self.thresholds['normal']['speed_min'] and
              occupancy <= self.thresholds['normal']['occupancy_max']):
            state = 'normal'
        elif (queue_length <= self.thresholds['congested']['queue_max'] and
              avg_speed >= self.thresholds['congested']['speed_min'] and
              occupancy <= self.thresholds['congested']['occupancy_max']):
            state = 'congested'
        else:
            state = 'heavy_congested'
        
        # 计算拥堵等级
        congestion_levels = {'free': 0.0, 'normal': 0.2, 'congested': 0.6, 'heavy_congested': 1.0}
        congestion_level = congestion_levels[state]
        
        return {
            'traffic_state': state,
            'confidence': 0.8,  # 规则-based方法给固定置信度
            'congestion_level': congestion_level,
            'probabilities': {cls: 1.0 if cls == state else 0.0 for cls in self.thresholds.keys()}
        }

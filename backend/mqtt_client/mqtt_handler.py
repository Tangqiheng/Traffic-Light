import paho.mqtt.client as mqtt
import json
import time
import threading
from typing import Dict, List, Callable
import logging

logger = logging.getLogger(__name__)

class MQTTHandler:
    def __init__(self, broker_host: str = "localhost", broker_port: int = 1883,
                 client_id: str = None, username: str = None, password: str = None):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client_id = client_id or f"traffic_light_{int(time.time())}"
        self.username = username
        self.password = password
        
        # MQTT客户端
        self.client = None
        self.is_connected = False
        
        # 主题和回调函数
        self.subscriptions = {}
        self.message_callbacks = {}
        
        # 数据缓存
        self.received_messages = {}
        
        # 线程锁
        self.lock = threading.Lock()
    
    def connect(self) -> bool:
        """连接到MQTT代理"""
        try:
            self.client = mqtt.Client(client_id=self.client_id)
            
            # 设置认证信息
            if self.username and self.password:
                self.client.username_pw_set(self.username, self.password)
            
            # 设置回调函数
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message
            
            # 连接到代理
            self.client.connect(self.broker_host, self.broker_port, keepalive=60)
            
            # 启动网络循环线程
            self.client.loop_start()
            
            # 等待连接建立
            timeout = 10
            start_time = time.time()
            while not self.is_connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if self.is_connected:
                logger.info(f"MQTT客户端 {self.client_id} 连接成功")
                return True
            else:
                logger.error("MQTT连接超时")
                return False
                
        except Exception as e:
            logger.error(f"MQTT连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开MQTT连接"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.is_connected = False
            logger.info("MQTT客户端已断开连接")
    
    def _on_connect(self, client, userdata, flags, rc):
        """连接回调"""
        if rc == 0:
            self.is_connected = True
            logger.info("MQTT连接成功")
            
            # 重新订阅所有主题
            for topic in self.subscriptions:
                self.client.subscribe(topic)
                logger.info(f"订阅主题: {topic}")
        else:
            self.is_connected = False
            logger.error(f"MQTT连接失败，返回码: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """断开连接回调"""
        self.is_connected = False
        if rc != 0:
            logger.warning(f"MQTT意外断开连接，返回码: {rc}")
    
    def _on_message(self, client, userdata, message):
        """消息接收回调"""
        try:
            topic = message.topic
            payload = message.payload.decode('utf-8')
            
            # 解析JSON消息
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                data = payload
            
            # 缓存消息
            with self.lock:
                self.received_messages[topic] = {
                    'data': data,
                    'timestamp': time.time()
                }
            
            # 调用回调函数
            if topic in self.message_callbacks:
                self.message_callbacks[topic](data, topic)
            
            logger.debug(f"收到MQTT消息 - 主题: {topic}, 数据: {data}")
            
        except Exception as e:
            logger.error(f"处理MQTT消息失败: {e}")
    
    def subscribe(self, topic: str, callback: Callable = None, qos: int = 0):
        """订阅主题"""
        if not self.is_connected:
            logger.warning("MQTT客户端未连接，无法订阅主题")
            return False
        
        try:
            self.client.subscribe(topic, qos=qos)
            self.subscriptions[topic] = qos
            
            if callback:
                self.message_callbacks[topic] = callback
            
            logger.info(f"订阅主题成功: {topic}")
            return True
            
        except Exception as e:
            logger.error(f"订阅主题失败: {e}")
            return False
    
    def unsubscribe(self, topic: str):
        """取消订阅主题"""
        if not self.is_connected:
            return False
        
        try:
            self.client.unsubscribe(topic)
            if topic in self.subscriptions:
                del self.subscriptions[topic]
            if topic in self.message_callbacks:
                del self.message_callbacks[topic]
            
            logger.info(f"取消订阅主题: {topic}")
            return True
            
        except Exception as e:
            logger.error(f"取消订阅失败: {e}")
            return False
    
    def publish(self, topic: str, message, qos: int = 0, retain: bool = False):
        """发布消息"""
        if not self.is_connected:
            logger.warning("MQTT客户端未连接，无法发布消息")
            return False
        
        try:
            # 序列化消息
            if isinstance(message, (dict, list)):
                payload = json.dumps(message, ensure_ascii=False)
            else:
                payload = str(message)
            
            result = self.client.publish(topic, payload, qos=qos, retain=retain)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"发布MQTT消息成功 - 主题: {topic}")
                return True
            else:
                logger.error(f"发布MQTT消息失败，返回码: {result.rc}")
                return False
                
        except Exception as e:
            logger.error(f"发布MQTT消息异常: {e}")
            return False
    
    def get_last_message(self, topic: str) -> Dict:
        """获取指定主题的最后一条消息"""
        with self.lock:
            return self.received_messages.get(topic, {})
    
    def get_all_messages(self) -> Dict:
        """获取所有缓存的消息"""
        with self.lock:
            return self.received_messages.copy()
    
    def clear_messages(self, topic: str = None):
        """清除缓存的消息"""
        with self.lock:
            if topic:
                self.received_messages.pop(topic, None)
            else:
                self.received_messages.clear()

class TrafficLightMQTTClient:
    """专门用于交通灯系统的MQTT客户端"""
    
    def __init__(self, intersection_id: str, broker_host: str = "localhost", 
                 broker_port: int = 1883):
        self.intersection_id = intersection_id
        self.base_topic = f"traffic/{intersection_id}"
        
        # 初始化MQTT处理器
        self.mqtt = MQTTHandler(
            broker_host=broker_host,
            broker_port=broker_port,
            client_id=f"traffic_light_{intersection_id}"
        )
        
        # 定义主题
        self.topics = {
            'sensor_data': f"{self.base_topic}/sensors/+/data",
            'control_commands': f"{self.base_topic}/control/commands",
            'status_updates': f"{self.base_topic}/status",
            'alerts': f"{self.base_topic}/alerts",
            'config_updates': f"{self.base_topic}/config"
        }
        
        # 数据回调
        self.sensor_callbacks = []
        self.control_callbacks = []
        self.status_callbacks = []
    
    def connect(self) -> bool:
        """连接到MQTT代理并订阅主题"""
        if not self.mqtt.connect():
            return False
        
        # 订阅传感器数据
        self.mqtt.subscribe(
            self.topics['sensor_data'],
            callback=self._on_sensor_data
        )
        
        # 订阅控制命令
        self.mqtt.subscribe(
            self.topics['control_commands'],
            callback=self._on_control_command
        )
        
        # 订阅配置更新
        self.mqtt.subscribe(
            self.topics['config_updates'],
            callback=self._on_config_update
        )
        
        logger.info(f"交通灯MQTT客户端 {self.intersection_id} 初始化完成")
        return True
    
    def disconnect(self):
        """断开连接"""
        self.mqtt.disconnect()
    
    def _on_sensor_data(self, data: Dict, topic: str):
        """传感器数据回调"""
        try:
            # 解析传感器类型
            topic_parts = topic.split('/')
            sensor_type = topic_parts[-2]  # sensors/{type}/data
            
            # 通知所有传感器回调
            for callback in self.sensor_callbacks:
                callback(sensor_type, data)
            
            logger.debug(f"收到传感器数据: {sensor_type} - {data}")
            
        except Exception as e:
            logger.error(f"处理传感器数据失败: {e}")
    
    def _on_control_command(self, data: Dict, topic: str):
        """控制命令回调"""
        try:
            # 通知所有控制回调
            for callback in self.control_callbacks:
                callback(data)
            
            logger.info(f"收到控制命令: {data}")
            
        except Exception as e:
            logger.error(f"处理控制命令失败: {e}")
    
    def _on_config_update(self, data: Dict, topic: str):
        """配置更新回调"""
        try:
            logger.info(f"收到配置更新: {data}")
            # 这里可以实现配置热更新逻辑
            
        except Exception as e:
            logger.error(f"处理配置更新失败: {e}")
    
    def publish_sensor_data(self, sensor_type: str, sensor_id: str, data: Dict):
        """发布传感器数据"""
        topic = f"{self.base_topic}/sensors/{sensor_type}/data"
        return self.mqtt.publish(topic, data)
    
    def publish_status(self, status_data: Dict):
        """发布状态信息"""
        return self.mqtt.publish(self.topics['status_updates'], status_data)
    
    def publish_alert(self, alert_data: Dict):
        """发布警报信息"""
        return self.mqtt.publish(self.topics['alerts'], alert_data, qos=1)
    
    def send_control_command(self, target_intersection: str, command: Dict):
        """发送控制命令到其他路口"""
        if target_intersection == self.intersection_id:
            # 本地命令
            for callback in self.control_callbacks:
                callback(command)
        else:
            # 远程命令
            topic = f"traffic/{target_intersection}/control/commands"
            return self.mqtt.publish(topic, command, qos=1)
    
    def add_sensor_callback(self, callback: Callable):
        """添加传感器数据回调"""
        self.sensor_callbacks.append(callback)
    
    def add_control_callback(self, callback: Callable):
        """添加控制命令回调"""
        self.control_callbacks.append(callback)
    
    def add_status_callback(self, callback: Callable):
        """添加状态回调"""
        self.status_callbacks.append(callback)
    
    def get_connection_status(self) -> bool:
        """获取连接状态"""
        return self.mqtt.is_connected

# MQTT代理管理器
class MQTTBrokerManager:
    """简单的MQTT代理管理器（用于开发环境）"""
    
    def __init__(self):
        self.is_running = False
        self.broker_process = None
    
    def start_broker(self):
        """启动本地MQTT代理（需要安装mosquitto）"""
        try:
            import subprocess
            
            # 检查mosquitto是否安装
            result = subprocess.run(['mosquitto', '-h'], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("Mosquitto MQTT代理未安装，请先安装: choco install mosquitto")
                return False
            
            # 启动mosquitto代理
            self.broker_process = subprocess.Popen(['mosquitto', '-v'])
            self.is_running = True
            
            logger.info("MQTT代理已启动")
            return True
            
        except Exception as e:
            logger.error(f"启动MQTT代理失败: {e}")
            return False
    
    def stop_broker(self):
        """停止MQTT代理"""
        if self.broker_process:
            self.broker_process.terminate()
            self.broker_process.wait()
            self.is_running = False
            logger.info("MQTT代理已停止")
    
    def is_broker_running(self) -> bool:
        """检查代理是否运行"""
        return self.is_running and self.broker_process and self.broker_process.poll() is None

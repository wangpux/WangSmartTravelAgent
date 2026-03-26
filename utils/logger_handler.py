import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from utils.path_tool import get_abspath

class LoggerHandler:
    """
    日志处理器
    支持控制台输出与滚动文件记录，预留隐私脱敏接口
    """

    def __init__(self, name="小王智游", log_level=logging.INFO, log_dir=get_abspath("logs")):
        self.logger = logging.getLogger(name)

        # 防止重复添加 handler
        if self.logger.handlers:
            return

        self.logger.setLevel(log_level)

        # 防止向 root logger 传播（避免重复打印）
        self.logger.propagate = False

        # 确保目录存在
        os.makedirs(log_dir, exist_ok= True)

        # 定义日志格式：时间 - 名称 - 级别 - 消息
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 1. 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # 2. 滚动文件处理器 (每个文件10MB，保留5个备份)
        log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger

    def log_agent_step(self, thought, action, observation=None):
        """
        专门用于记录 Agent 推理步骤的格式化函数
        """
        message = f"\n[Thought]: {thought}\n[Action]: {action}"
        if observation:
            message += f"\n[Observation]: {observation}"
        self.logger.info(message)


# 实例化全局单例
logger = LoggerHandler().get_logger()

if __name__ == '__main__':
    logger.error("错误测试")
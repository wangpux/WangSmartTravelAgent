import os
from utils.path_tool import get_abspath
from utils.logger_handler import logger
from utils.config_handler import config_handler

class PromptHandler:
    """
    提示词处理器：从 YAML 获取路径，从 TXT 加载内容
    """

    def __init__(self):
        # 加载 prompts.yml 配置
        self.config = config_handler.load_config("prompts")
        self.prompts = {}
        self._load_all_prompts()

    def _load_all_prompts(self):
        """
        初始化时加载所有在配置文件中定义的提示词文本
        """
        if not self.config:
            logger.error("未找到 prompts 配置，无法加载提示词文本")
            return

        for key, relative_path in self.config.items():
            # 拼接绝对路径
            full_path = get_abspath(relative_path)

            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        self.prompts[key] = f.read()
                    logger.info(f"成功加载提示词文本: {key} (路径: {relative_path})")
                except Exception as e:
                    logger.error(f"读取提示词文件 {relative_path} 出错: {e}")
            else:
                logger.warning(f"提示词文件不存在: {full_path}")

    def get_prompt(self, key):
        """
        根据键名获取提示词内容
        """
        return self.prompts.get(key, "")


# 实例化
prompt_handler = PromptHandler()
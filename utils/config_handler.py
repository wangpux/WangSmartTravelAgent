import yaml
import os
from utils.path_tool import get_abspath
from utils.logger_handler import logger


class ConfigHandler:
    """
    通用配置加载器：根据模块名（rag/chroma/prompt/agent等）动态加载 config 文件夹下的 yaml
    """

    def __init__(self, config_folder="config"):
        self.config_dir = get_abspath(config_folder)

    def load_config(self, module_name):
        """
        加载指定的模块配置文件
        :param module_name: 字符串类型，如 'rag', 'chroma', 'prompt', 'agent'
        :return: 配置字典 (dict)
        """
        file_path = os.path.join(self.config_dir, f"{module_name}.yml")

        if not os.path.exists(file_path):
            error_msg = f"配置文件不存在: {file_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # 使用 safe_load 防止 YAML 注入攻击
                config_data = yaml.safe_load(f)
                logger.info(f"成功加载配置模块: [{module_name}]")
                return config_data
        except Exception as e:
            logger.error(f"解析 {module_name}.yaml 失败: {str(e)}")
            raise e


# 实例化全局单例
config_handler = ConfigHandler()

# if __name__ == '__main__':
#     print(config_handler.load_config('rag')['model_name'])
"""
统一的绝对路径，
避免因为在不同文件夹下运行导致 FileNotFoundError
"""

import os

def get_project_root():
    current_file = os.path.abspath(__file__)

    current_dir = os.path.dirname(current_file)
    project_root = os.path.dirname(current_dir)

    return project_root

def get_abspath(relpath):
    project_root = get_project_root()

    return os.path.join(project_root, relpath)
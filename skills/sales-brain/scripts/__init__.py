"""
AI Sales Brain - 初始化模块
"""
import os

# 获取 skill 根目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(SKILL_DIR, 'data')

# 确保目录存在
os.makedirs(os.path.join(DATA_DIR, 'customers'), exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, 'conversations'), exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, 'evolution'), exist_ok=True)

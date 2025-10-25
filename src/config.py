"""配置管理模块 - 统一的配置管理"""

import json
from pathlib import Path
from typing import Dict, List, Any


class Config:
    """配置管理类 - 支持config.json和web_config.json"""
    
    def __init__(self, config_file: str = 'config.json'):
        self.config_file = Path(config_file)
        self.config = self._load_or_create()
    
    def _load_or_create(self) -> Dict[str, Any]:
        """加载或创建配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置失败 {self.config_file}: {e}，使用默认配置")
                return self._default_config()
        else:
            # 首次运行，创建默认配置
            config = self._default_config()
            self.save(config)
            print(f"已创建默认配置文件: {self.config_file}")
            return config
    
    def _default_config(self) -> Dict[str, Any]:
        """默认配置"""
        return {
            "proxy": None,
            "output": "output",
            "user": []
        }
    
    def get_global_config(self) -> Dict[str, Any]:
        """获取全局配置"""
        return {
            'proxy': self.config.get('proxy'),
            'output': self.config.get('output', 'output')
        }
    
    def get_users(self) -> List[Dict]:
        """获取用户列表"""
        return self.config.get('user', [])
    
    def save(self, config: Dict[str, Any]) -> bool:
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            self.config = config
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def get_all(self) -> Dict[str, Any]:
        """获取完整配置"""
        return self.config.copy()

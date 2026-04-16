import json
import os

CONFIG_PATH = "config.json"

DEFAULT_CONFIG = {
    "backtest": {
        "cash": 100000.0,
        "commission": 0.001,
        "slippage_perc": 0.0
    },
    "api_keys": {
        "tushare": "",
        "openai": ""
    }
}


def load_config():
    """加载配置文件，不存在则返回默认配置"""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    """保存配置到文件"""
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"保存配置失败：{e}")
        return False

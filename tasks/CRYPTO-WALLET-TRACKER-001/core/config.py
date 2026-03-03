#!/usr/bin/env python3
"""
配置模块 - CRYPTO-WALLET-TRACKER-001
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

class Config:
    DEBUG = False
    VERSION = "1.0.0"
    DATA_DIR = BASE_DIR / "data"
    LOG_DIR = BASE_DIR / "logs"

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

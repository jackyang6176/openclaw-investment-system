#!/bin/bash
# 四策略投資分析系統執行腳本

cd /home/admin/.openclaw/workspace/investment/scripts
python3 main_four_strategy.py

echo "四策略投資分析執行完成 - $(date)"
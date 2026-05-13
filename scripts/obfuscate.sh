#!/bin/bash
# Staff Engineer Obfuscation Strategy
# Uses PyArmor to protect source code before shipping to customers on Whop.

# 1. Install PyArmor
pip install pyarmor

# 2. Obfuscate core logic and services
# This creates a 'dist' folder with protected .py files
pyarmor gen --output dist/packages/core-contracts packages/core-contracts/core_contracts/*.py
pyarmor gen --output dist/services/execution-engine services/execution-engine/execution_engine/*.py
pyarmor gen --output dist/services/telegram-bot services/telegram-bot/telegram_bot/*.py
pyarmor gen --output dist/services/trainer services/trainer/trainer/*.py

echo "✅ Obfuscation complete. Ready to package dist/ for customers."
echo "⚠️ Note: Your Dockerfile should point to these obfuscated files in production."

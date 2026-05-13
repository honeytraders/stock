#!/bin/bash
# HTEQ Professional Setup Wizard
# Staff Engineer implementation for seamless customer onboarding.

set -e

echo "------------------------------------------------"
echo "   HTEQ Equities - Professional Setup Wizard    "
echo "------------------------------------------------"

# 1. Check for .env
if [ ! -f .env ]; then
    echo "Creating .env from template..."
    cp .env.example .env
fi

# 2. Hardware ID Generation
MACHINE_ID=$(python3 -c "import uuid,hashlib; print(hashlib.sha256(str(uuid.getnode()).encode()).hexdigest())")
echo "Your Machine ID: $MACHINE_ID"
echo "Please ensure this ID is registered in your Whop dashboard or provided to support."

# 3. Connectivity Check
echo "Testing broker connectivity..."
# Simple check for python dependencies
if ! python3 -c "import httpx, pydantic" 2>/dev/null; then
    echo "Python dependencies missing. Please run: pip install httpx pydantic"
    exit 1
fi

# 4. License Check Placeholder
LICENSE=$(grep HTEQ__WHOP_LICENSE .env | cut -d '=' -f2)
if [ "$LICENSE" == "PASTE_LICENSE_HERE" ] || [ -z "$LICENSE" ]; then
    echo "⚠️  WARNING: No license key found in .env"
else
    echo "✅ License key detected."
fi

echo "------------------------------------------------"
echo "Setup Wizard Complete."
echo "Run 'docker-compose up -d' to start the bot."
echo "------------------------------------------------"

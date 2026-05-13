# HoneyTrade Equities (HTEQ)

Professional trading infrastructure for US Equities (NYSE/NASDAQ) with autonomous ML-driven execution.

## Core Features

- **Autonomous Model Training:** Continuous training via LightGBM on historical data. Automatic model hot-reloading.
- **Operator Interface:** Full control via Telegram. Monitor positions, adjust risk parameters, and execute manual orders.
- **Risk Management:** Notional trade limits, position caps, and persistent state across services.
- **Efficiency:** Minimal resource footprint. Compatible with entry-level VPS instances.

## Setup

1. **Environment:** Configure `.env` based on `.env.example`.
2. **Launch:** 
   ```bash
   docker-compose up -d --build
   ```
3. **Connect:** Link your Telegram bot via the `/start` command.

## Commands

- `/status` - Account equity and buying power.
- `/positions` - Current portfolio holdings.
- `/pause` / `/resume` - Dynamic execution control.
- `/buy` / `/sell` - Manual market order execution.

## Architecture

- **Core Contracts:** Domain models, shared state, and hardware-locked licensing.
- **Broker Adapters:** Pluggable Alpaca interface.
- **Execution Engine:** Low-latency signal processing loop.
- **Trainer Service:** Background pipeline for model optimization.

## Licensing

Protected by a Hardware-Lock Licensing model. Usage is restricted to authorized servers. Valid license required from [Whop Storefront](https://whop.com/honeytrade).

---
*Disclaimer: Trading stocks involves risk. This software is provided for educational purposes. Performance is not guaranteed.*

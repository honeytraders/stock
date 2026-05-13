# HoneyTrade Equities Playbook

## Operator Manual
0. **Pre-flight**: Run `./scripts/doctor.sh` to verify ENV and connectivity.
1. **Deployment**: `docker-compose up -d`
2. **Training**: Run trainer pipeline via CLI to export artifacts to `data/models`.
3. **Paper Trading**: Default mode is paper. Ensure `HTEQ__MODE=paper`.
4. **Live Trading**:
   - Set `HTEQ__MODE=live`
   - Set `HTEQ__ACK_LIVE=I_UNDERSTAND_REAL_MONEY`
   - Set `HTEQ__TRADING_ENABLED=true`
   - Run `./scripts/doctor.sh` again to verify live connectivity.

## Emergency
- **Kill Switch**: Set `HTEQ__TRADING_ENABLED=false` and restart engine.
- **Flatten**: (Manual via Alpaca Dashboard in MVP).

## Security
- Rotate Alpaca keys every 90 days.
- Never share `.env` file.

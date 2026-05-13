FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir ./packages/core-contracts ./packages/broker-adapters ./services/execution-engine
CMD ["python", "-m", "execution_engine.main"]

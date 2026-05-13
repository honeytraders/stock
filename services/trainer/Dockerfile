FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir ./packages/core-contracts ./services/trainer
CMD ["python", "-m", "trainer.main"]

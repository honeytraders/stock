import json
import logging
import time


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "ts": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "event": record.getMessage(),
            "logger": record.name,
        }
        if hasattr(record, "symbol"):
            log_record["symbol"] = record.symbol
        if hasattr(record, "order_id"):
            log_record["order_id"] = record.order_id
        return json.dumps(log_record)


def setup_logging(level=logging.INFO):
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logging.basicConfig(level=level, handlers=[handler])


def audit_log(event: str, metadata: dict = None):
    with open("data/audit.log", "a") as f:
        log_entry = {"ts": time.time(), "event": event, "metadata": metadata or {}}
        f.write(json.dumps(log_entry) + "\n")

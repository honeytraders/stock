import hashlib
import json
import logging
import os
from typing import Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ModelManifest(BaseModel):
    version: str
    created_at: str
    features: list[str]
    model_file: str
    sha256: str
    training_window: Optional[dict] = None


def verify_bundle(bundle_path: str) -> bool:
    manifest_path = os.path.join(bundle_path, "manifest.json")
    if not os.path.exists(manifest_path):
        logger.error(f"Manifest missing at {manifest_path}")
        return False

    with open(manifest_path, "r") as f:
        try:
            manifest_data = json.load(f)
            manifest = ModelManifest(**manifest_data)
        except Exception as e:
            logger.error(f"Failed to parse manifest: {e}")
            return False

    model_path = os.path.join(bundle_path, manifest.model_file)
    if not os.path.exists(model_path):
        logger.error(f"Model file {manifest.model_file} not found in bundle")
        return False

    with open(model_path, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
        if file_hash != manifest.sha256:
            logger.error(
                f"SHA256 mismatch for model file: expected {manifest.sha256}, got {file_hash}"
            )
            return False

    logger.info(
        f"Model bundle verified: version={manifest.version}, created_at={manifest.created_at}"
    )
    return True

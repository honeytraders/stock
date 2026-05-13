import json

from core_contracts.bundle import verify_bundle


def test_verify_bundle_success(tmp_path):
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    model_file = bundle_dir / "model.txt"
    model_file.write_text("model-content")

    import hashlib

    h = hashlib.sha256(b"model-content").hexdigest()

    manifest = {
        "version": "1.0",
        "created_at": "now",
        "features": ["f1"],
        "model_file": "model.txt",
        "sha256": h,
    }
    with open(bundle_dir / "manifest.json", "w") as f:
        json.dump(manifest, f)

    assert verify_bundle(str(bundle_dir)) is True


def test_verify_bundle_hash_mismatch(tmp_path):
    bundle_dir = tmp_path / "bundle_bad"
    bundle_dir.mkdir()
    (bundle_dir / "model.txt").write_text("changed")

    with open(bundle_dir / "manifest.json", "w") as f:
        json.dump(
            {
                "version": "1.0",
                "created_at": "now",
                "features": [],
                "model_file": "model.txt",
                "sha256": "wrong",
            },
            f,
        )

    assert verify_bundle(str(bundle_dir)) is False

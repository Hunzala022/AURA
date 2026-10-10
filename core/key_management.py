"""Local Fernet key storage. Real keys and memory stores must never enter Git."""

from pathlib import Path

from cryptography.fernet import Fernet


PROJECT_ROOT = Path(__file__).resolve().parent.parent
KEY_FILE = PROJECT_ROOT / ".keys" / "aura_aes.key"


def get_or_create_key(key_file=None, data_paths=None) -> bytes:
    """Load a valid local key, or create one only for an empty installation.

    Never silently replace a missing/invalid key for retained encrypted data.
    Optional paths allow callers and isolated tests to identify their stores.
    """
    path = Path(key_file) if key_file is not None else KEY_FILE
    if path.with_name("rotation-in-progress").exists():
        raise RuntimeError("Memory key rotation is incomplete; restore or finish it before startup.")
    if path.exists():
        key = path.read_bytes()
        Fernet(key)  # Reject corrupt keys without replacing them.
        return key

    stores = data_paths if data_paths is not None else (
        Path("aura_memory.db"), Path("aura_chroma"),
        PROJECT_ROOT / "aura_memory.db", PROJECT_ROOT / "aura_chroma",
    )
    if any(Path(store).exists() for store in stores):
        raise RuntimeError("Local key is missing but memory data exists. Restore its key; do not generate a replacement.")

    path.parent.mkdir(parents=True, exist_ok=True)
    key = Fernet.generate_key()
    # Exclusive creation prevents overwriting a key created by another process.
    try:
        with path.open("xb") as stream:
            stream.write(key)
    except FileExistsError:
        key = path.read_bytes()
        Fernet(key)
    return key

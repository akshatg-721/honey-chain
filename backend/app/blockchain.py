import hashlib
from datetime import datetime


def generate_hash(batch_id: str, status: str, timestamp: datetime, previous_hash: str) -> str:
    """
    Produce a deterministic SHA-256 hex digest for a ledger block.

    Payload format (pipe-delimited, no spaces):
        {batch_id}|{status}|{timestamp.isoformat()}|{previous_hash}
    """
    payload = f"{batch_id}|{status}|{timestamp.isoformat()}|{previous_hash}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def verify_chain(checkpoints: list) -> bool:
    """
    Validate both data integrity and chain linkage for a list of checkpoint objects.

    For each checkpoint the function checks two things:
      A) Data integrity  — recompute the hash and compare to the stored hash.
      B) Chain linkage   — confirm previous_hash matches the preceding block's hash
                           (or "0" for the genesis block).

    Returns True only if every block passes both checks.
    Returns True immediately for an empty list (no chain = valid).
    """
    if not checkpoints:
        return True

    for i, cp in enumerate(checkpoints):
        # ── A: Data integrity ────────────────────────────────────────────────
        recomputed = generate_hash(cp.batch_id, cp.status, cp.timestamp, cp.previous_hash)
        if recomputed != cp.hash:
            return False

        # ── B: Chain linkage ─────────────────────────────────────────────────
        if i == 0:
            if cp.previous_hash != "0":
                return False
        else:
            if cp.previous_hash != checkpoints[i - 1].hash:
                return False

    return True

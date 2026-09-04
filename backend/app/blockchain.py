import copy
import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# Genesis block reference: The first block has no predecessor, so we use 64 zeroes.


GENESIS_PREVIOUS_HASH = "0" * 64


def get_current_timestamp() -> str:
    """
    Generate an ISO 8601 UTC timestamp string.
    Ensures a consistent time format across blockchain operations.
    Example: 2026-09-04T14:21:05Z
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def compute_hash(data: Dict[str, Any], previous_hash: str, timestamp: str) -> str:
    """
    Deterministically computes the SHA-256 hash of a block's content.

    Why deterministic?
    In blockchain verification, we later rebuild the hash from the stored block
    fields to confirm nothing was tampered with. If the key order or whitespace
    changes between runs, the resulting hash would mismatch even if data is identical.

    Args:
        data: Dictionary of data for this block (e.g. batch details or checkpoint info).
        previous_hash: 64-character SHA-256 hex string of previous block (or GENESIS_PREVIOUS_HASH).
        timestamp: ISO formatted timestamp when the block was created.

    Returns:
        64-character hexadecimal SHA-256 hash string.
    """
    payload = {
        "data": data,
        "previous_hash": previous_hash,
        "timestamp": timestamp,
    }

    # sort_keys=True ensures key ordering is identical every time.
    # separators=(',', ':') removes variable spacing between items.


    serialized_bytes = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    
    return hashlib.sha256(serialized_bytes).hexdigest()


def create_genesis_block(batch_data: Dict[str, Any], timestamp: Optional[str] = None) -> Dict[str, Any]:
    """
    Creates the first block (genesis block) in a batch's hash chain.
    Uses GENESIS_PREVIOUS_HASH since there is no prior block to reference.
    Folds 'status' directly into the hashed data payload so status is tamper-proof.
    Returns a dict ready to be persisted as a LedgerBlock row.

    Args:
        batch_data: Dictionary of initial batch details (e.g. beekeeper_name, farm_location, quantity_kg).
        timestamp: Optional ISO UTC timestamp string. If not provided, current UTC time is used.

    Returns:
        Dict containing block metadata: data (including status), previous_hash, timestamp, hash.
    """
    if timestamp is None:
        timestamp = get_current_timestamp()

    status = batch_data.get("status", "harvested")
    data_to_hash = {**batch_data, "status": status}

    block_hash = compute_hash(
        data=data_to_hash,
        previous_hash=GENESIS_PREVIOUS_HASH,
        timestamp=timestamp,
    )

    return {
        "data": data_to_hash,
        "previous_hash": GENESIS_PREVIOUS_HASH,
        "timestamp": timestamp,
        "hash": block_hash,
    }


def create_checkpoint_block(
    status: str,
    previous_hash: str,
    timestamp: Optional[str] = None,
    extra_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Creates a new checkpoint block, linked to the previous block in the chain
    via previous_hash. Represents a supply-chain stage transition (e.g. processed, packaged, shipped).

    Args:
        status: Supply-chain status for this checkpoint (e.g. "processed", "packaged", "shipped").
        previous_hash: 64-character SHA-256 hash of the immediately preceding block.
        timestamp: Optional ISO UTC timestamp string. Defaults to current UTC time.
        extra_data: Optional dict for any additional context fields (e.g. location, handler notes).

    Returns:
        Dict containing block metadata: data (including status), previous_hash, timestamp, hash.
    """
    if timestamp is None:
        timestamp = get_current_timestamp()

    data_to_hash = {"status": status, **(extra_data or {})}

    block_hash = compute_hash(
        data=data_to_hash,
        previous_hash=previous_hash,
        timestamp=timestamp,
    )

    return {
        "data": data_to_hash,
        "previous_hash": previous_hash,
        "timestamp": timestamp,
        "hash": block_hash,
    }


def verify_chain(chain: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Walks through a full stored chain and verifies:
      1. Genesis block references the expected GENESIS_PREVIOUS_HASH.
      2. Each block's stored hash matches what we recompute from its data + previous_hash + timestamp.
      3. Each block's previous_hash correctly points to the prior block's actual hash.

    Args:
        chain: Ordered list of blocks (dicts with data, previous_hash, timestamp, hash),
               genesis block first.

    Returns:
        Dict with "valid" (bool), "broken_at_index" (int or None), "reason" (str or None).
    """
    if not chain:
        return {"valid": False, "broken_at_index": None, "reason": "Chain is empty"}

    # Check the genesis block's previous_hash is the correct placeholder
    if chain[0]["previous_hash"] != GENESIS_PREVIOUS_HASH:
        return {
            "valid": False,
            "broken_at_index": 0,
            "reason": "Genesis block does not reference the expected genesis placeholder",
        }

    for i, block in enumerate(chain):
        # Check 1: does this block's stored hash match what we recompute?
        recomputed = compute_hash(block["data"], block["previous_hash"], block["timestamp"])
        if recomputed != block["hash"]:
            return {
                "valid": False,
                "broken_at_index": i,
                "reason": f"Block {i} data does not match its stored hash (tampered content)",
            }

        # Check 2: does this block correctly link to the previous block? (skip for genesis)
        if i > 0:
            if block["previous_hash"] != chain[i - 1]["hash"]:
                return {
                    "valid": False,
                    "broken_at_index": i,
                    "reason": f"Block {i} previous_hash does not match block {i - 1}'s actual hash (broken link)",
                }

    return {"valid": True, "broken_at_index": None, "reason": None}


def simulate_tampering(
    chain: List[Dict[str, Any]],
    block_index: int,
    field: str,
    new_value: Any,
) -> List[Dict[str, Any]]:
    """
    Returns a TAMPERED COPY of the given chain, for demo/testing purposes only.
    Does not mutate the original chain — always works on a deep copy.

    Args:
        chain: The original, valid chain.
        block_index: Index of the block to tamper with.
        field: Which field inside that block's "data" dict to change (e.g. "status", "quantity_kg").
        new_value: The new (fraudulent) value to insert.

    Returns:
        A new chain (list of blocks) with the specified field altered.
        Note: the block's stored "hash" is deliberately left unchanged, simulating
        what a tamperer would do — edit the data without being able to forge a valid hash.
    """
    if block_index < 0 or block_index >= len(chain):
        raise ValueError(f"block_index {block_index} out of range for chain of length {len(chain)}")

    tampered_chain = copy.deepcopy(chain)
    tampered_chain[block_index]["data"][field] = new_value
    return tampered_chain


if __name__ == "__main__":
    print("=== Testing Module 1: Deterministic Block Hashing ===\n")

    # Sample batch data matching HoneyChain's frontend/schema

    sample_data = {
        "batch_id": "HCB-2024-001",
        "status": "harvested",
        "beekeeper_name": "Arjun Sharma",
        "farm_location": "Coorg, Karnataka",
        "quantity_kg": 120,
    }
    
    timestamp = get_current_timestamp()
    prev_hash = GENESIS_PREVIOUS_HASH

    # 1. Compute hash

    hash1 = compute_hash(sample_data, prev_hash, timestamp)
    print(f"Computed Hash (64-char hex):\n  {hash1}")
    assert len(hash1) == 64, "Hash length should be 64 characters"

    # 2. Check determinism (same inputs -> identical hash)

    hash2 = compute_hash(sample_data, prev_hash, timestamp)
    print(f"\nDeterminism Check:\n  Run 1 == Run 2: {hash1 == hash2} (Expected: True)")
    assert hash1 == hash2, "Hashing must be 100% deterministic!"

    # 3. Check key-order insensitivity (dict key order shouldn't change hash)

    reordered_data = {
        "quantity_kg": 120,
        "farm_location": "Coorg, Karnataka",
        "status": "harvested",
        "batch_id": "HCB-2024-001",
        "beekeeper_name": "Arjun Sharma",
    }
    hash_reordered = compute_hash(reordered_data, prev_hash, timestamp)
    print(f"Key-order independence Check:\n  Original == Reordered: {hash1 == hash_reordered} (Expected: True)")
    assert hash1 == hash_reordered, "Key order in dictionary must not alter hash!"

    # 4. Check avalanche effect / tamper sensitivity

    tampered_data = sample_data.copy()
    tampered_data["quantity_kg"] = 121  # changed just 1 kg
    hash_tampered = compute_hash(tampered_data, prev_hash, timestamp)
    print(f"\nTamper Detection Check (Avalanche Effect):")
    print(f"  Original: {hash1}")
    print(f"  Tampered: {hash_tampered}")
    print(f"  Hashes Match: {hash1 == hash_tampered} (Expected: False)")
    assert hash1 != hash_tampered, "Any change must alter the hash completely!"

    print("\n[OK] Module 1 tests passed successfully!")

    print("\n=== Testing Module 2: Genesis Block Creation ===")
    batch_data = {
        "beekeeper_name": "Ramesh Kumar",
        "farm_location": "Rohtak, Haryana",
        "harvest_date": "2026-08-15",
        "quantity_kg": 25,
    }
    genesis = create_genesis_block(batch_data)

    print(f"Genesis block hash:\n  {genesis['hash']}")
    print(f"Status: {genesis['data']['status']}")

    # Check 1: previous_hash must be the 64-zero placeholder
    is_prev_zero = genesis["previous_hash"] == "0" * 64
    print(f"Previous hash is genesis placeholder: {is_prev_zero}")
    assert is_prev_zero, "Previous hash must be 64 zeroes!"

    # Check 2: hash must be a valid 64-char hex string
    is_valid_len = len(genesis["hash"]) == 64
    print(f"Hash length correct (64 hex): {is_valid_len}")
    assert is_valid_len, "Hash must be 64 characters long!"

    # Check 3: recomputing with the same data+timestamp should match stored hash
    recomputed = compute_hash(genesis["data"], genesis["previous_hash"], genesis["timestamp"])
    matches = recomputed == genesis["hash"]
    print(f"Recomputed hash matches stored hash: {matches}")
    assert matches, "Recomputed hash must match genesis stored hash!"

    # Check 4: tampering with status specifically alters the hash
    tampered_status_data = dict(genesis["data"])
    tampered_status_data["status"] = "shipped"  # unauthorized status jump
    tampered_status_hash = compute_hash(
        tampered_status_data, genesis["previous_hash"], genesis["timestamp"]
    )
    status_tamper_detected = tampered_status_hash != genesis["hash"]
    print(f"Tampering with status alters hash: {status_tamper_detected}")
    assert status_tamper_detected, "Tampering with status must break the hash!"

    print("\n[OK] Module 2 tests passed successfully!")

    print("\n=== Testing Module 3: Appending Checkpoint Blocks ===")

    # Build a mini chain: genesis -> processed -> packaged -> shipped
    genesis_block = create_genesis_block({
        "beekeeper_name": "Ramesh Kumar",
        "farm_location": "Rohtak, Haryana",
        "harvest_date": "2026-08-15",
        "quantity_kg": 25,
    })

    processed_block = create_checkpoint_block(status="processed", previous_hash=genesis_block["hash"])
    packaged_block = create_checkpoint_block(status="packaged", previous_hash=processed_block["hash"])
    shipped_block = create_checkpoint_block(status="shipped", previous_hash=packaged_block["hash"])

    chain = [genesis_block, processed_block, packaged_block, shipped_block]

    # Check 1: each block's previous_hash matches the prior block's actual hash
    links_correct = all(
        chain[i]["previous_hash"] == chain[i - 1]["hash"]
        for i in range(1, len(chain))
    )
    print(f"All previous_hash links correct: {links_correct}")
    assert links_correct, "Every checkpoint's previous_hash must point to the prior block's hash!"

    # Check 2: every hash in the chain is unique (no collisions or reuse)
    all_hashes = [b["hash"] for b in chain]
    hashes_unique = len(all_hashes) == len(set(all_hashes))
    print(f"All hashes unique: {hashes_unique}")
    assert hashes_unique, "All block hashes must be unique!"

    # Check 3: recomputing each block's hash from its own stored data matches
    recompute_ok = all(
        compute_hash(b["data"], b["previous_hash"], b["timestamp"]) == b["hash"]
        for b in chain
    )
    print(f"All blocks recompute correctly: {recompute_ok}")
    assert recompute_ok, "Every block's stored hash must match recomputation!"

    print("\n[OK] Module 3 tests passed successfully!")

    print("\n=== Testing Module 4: Chain Integrity Verification ===")

    # Test on the untouched valid chain
    valid_result = verify_chain(chain)
    print(f"Valid chain result: {valid_result}")
    print(f"Valid chain passes: {valid_result['valid'] is True}")
    assert valid_result["valid"] is True, "Valid chain must pass verification!"

    # Test tampering with block 2 (packaged) data while keeping hash unchanged
    import copy
    tampered_chain = copy.deepcopy(chain)
    tampered_chain[2]["data"]["status"] = "shipped"  # unauthorized status jump

    tampered_result = verify_chain(tampered_chain)
    print(f"Tampered chain result: {tampered_result}")
    print(f"Tampering correctly detected: {tampered_result['valid'] is False}")
    print(f"Correct block flagged: {tampered_result['broken_at_index'] == 2}")
    assert tampered_result["valid"] is False, "Tampered chain must fail verification!"
    assert tampered_result["broken_at_index"] == 2, "Must flag block 2 as the point of failure!"

    print("\n[OK] Module 4 tests passed successfully!")

    print("\n=== Testing Module 5: Tamper Detection Demo Helper ===")

    # Start from the same valid chain used in Module 4
    original_valid = verify_chain(chain)
    print(f"Before tampering, chain is valid: {original_valid['valid']}")
    assert original_valid["valid"] is True, "Original chain must be valid before tampering!"

    # Simulate a fraudster changing the harvest date on the genesis block
    fraudulent_chain = simulate_tampering(
        chain,
        block_index=0,
        field="harvest_date",
        new_value="2020-01-01",  # fake an older, "vintage" harvest date
    )

    fraud_result = verify_chain(fraudulent_chain)
    print(f"After tampering, chain is valid: {fraud_result['valid']}")
    print(f"Detected at block: {fraud_result['broken_at_index']}")
    print(f"Reason: {fraud_result['reason']}")
    assert fraud_result["valid"] is False, "Tampered chain must fail verification!"
    assert fraud_result["broken_at_index"] == 0, "Fraud must be caught at genesis block 0!"

    # Confirm original chain was NOT mutated (safety check)
    original_still_valid = verify_chain(chain)
    print(f"Original chain untouched and still valid: {original_still_valid['valid']}")
    assert original_still_valid["valid"] is True, "Original chain must never be mutated by demo helper!"

    print("\n[OK] Module 5 tests passed successfully!")

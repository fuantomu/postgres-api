import hashlib
import base64
import hmac


def verify_hash(check_hash: str, stored_hash: str) -> bool:
    stored_decoded = base64.b64decode(stored_hash)
    check_decoded = base64.b64decode(check_hash)

    HASH_LEN = hashlib.sha512().digest_size

    if len(check_decoded) < HASH_LEN:
        return False

    stored_hash_bytes = stored_decoded[:HASH_LEN]
    check_hash_bytes = check_decoded[:HASH_LEN]

    equal = hmac.compare_digest(stored_hash_bytes, check_hash_bytes)
    return equal

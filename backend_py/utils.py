import hashlib

def hash_password(raw):
    return hashlib.sha256(raw.encode()).hexdigest()
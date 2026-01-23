from passlib.hash import argon2

argon2_hasher = argon2.using(type="ID")

def hash_password(password: str) -> str:
    return argon2_hasher.hash(password)
    

def verify_password(password: str, stored_hash: str) -> bool:
    return argon2_hasher.verify(password, stored_hash)

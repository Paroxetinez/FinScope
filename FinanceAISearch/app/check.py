import hashlib

def hash_password(password):
    # 使用SHA-256哈希算法
    sha_signature = hashlib.sha256(password.encode()).hexdigest()
    return sha_signature

def check_password(hashed_password, user_password):
    # 对用户输入的密码进行哈希处理
    new_hashed_password = hash_password(user_password)
    # 比较存储的哈希值和新生成的哈希值是否相同
    return hashed_password == new_hashed_password
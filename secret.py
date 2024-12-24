import os

# Generate a secure random secret key
secret_key = os.urandom(32).hex()
print(secret_key)

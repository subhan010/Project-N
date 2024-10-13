from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding, serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
import os

# AES Functions

def generate_aes_key():
    return os.urandom(32)  # 256-bit key

def aes_encrypt(message, key):
    iv = os.urandom(16)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(message) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return iv + ciphertext

def aes_decrypt(ciphertext, key):
    iv = ciphertext[:16]
    actual_ciphertext = ciphertext[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(actual_ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    message = unpadder.update(padded_data) + unpadder.finalize()
    return message

# RSA Functions

def generate_rsa_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key

def rsa_encrypt(message, public_key):
    ciphertext = public_key.encrypt(
        message,
        asym_padding.OAEP(
            mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext

def rsa_decrypt(ciphertext, private_key):
    plaintext = private_key.decrypt(
        ciphertext,
        asym_padding.OAEP(
            mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return plaintext

# Hybrid Encryption Functions

# def hybrid_encrypt(message, rsa_public_key,aes_key):
#     #aes_key = generate_aes_key()
#     aes_encrypted_message = aes_encrypt(message, aes_key)
#     rsa_encrypted_aes_key = rsa_encrypt(aes_key, rsa_public_key)
#     return rsa_encrypted_aes_key, aes_encrypted_message

def encrypt_msg(message, rsa_public_key,aes_key):
    aes_encrypted_message = aes_encrypt(message, aes_key)
    return aes_encrypted_message

def decrypt_msg(aes_encrypted_message,aes_key):
    decrypted_message = aes_decrypt(aes_encrypted_message, aes_key)
    return decrypted_message

def encrypt_aes_key(aes_key, rsa_public_key):
    rsa_encrypted_key=rsa_encrypt(aes_key,rsa_public_key)
    return rsa_encrypted_key

def decrypt_aes_key(rsa_encrypted_key,rsa_priavte_key):

    decrypted_aes_key=rsa_decrypt(rsa_priavte_key,rsa_encrypted_key)
    return decrypt_aes_key


# def hybrid_decrypt(rsa_encrypted_aes_key, aes_encrypted_message, rsa_private_key):
#     aes_key = rsa_decrypt(rsa_encrypted_aes_key, rsa_private_key)
#     decrypted_message = aes_decrypt(aes_encrypted_message, aes_key)
#     return decrypted_message
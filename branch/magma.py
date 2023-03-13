from pygost.gost3412 import GOST3412Magma as Magma

def file_to_bytes(file_path: str) -> bytes:
    with open(file_path, "rb") as file:
        data = file.read()

    return data

def encrypt_data(input_data: bytes, key: bytes) -> bytes:
    cipher = Magma(key)

    padding_length = 8 - len(input_data) % 8
    padding = bytes([padding_length] * padding_length)
    padded_data = input_data + padding

    encrypted_data = b""
    for i in range(0, len(padded_data), 8):
        block = padded_data[i:i+8]
        encrypted_block = cipher.encrypt(block)
        encrypted_data += encrypted_block

    return encrypted_data


def decrypt_data(encrypted_data: bytes, key: bytes) -> bytes:
    cipher = Magma(key)

    decrypted_data = b""
    for i in range(0, len(encrypted_data), 8):
        block = encrypted_data[i:i+8]
        decrypted_block = cipher.decrypt(block)
        decrypted_data += decrypted_block

    padding_length = decrypted_data[-1]
    if padding_length > 8:
        raise ValueError("Invalid padding")
    unpadded_data = decrypted_data[:-padding_length]
    
    return unpadded_data
import zlib
import lzma
import base64
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from Crypto.Protocol.KDF import scrypt
from PIL import Image
import hashlib

# Encrypt the PEM file with a password
def encrypt_file(file_path, password, output_path):
    with open(file_path, "rb") as f:
        file_data = f.read()

    # Derive the encryption key from the password
    salt = get_random_bytes(16)
    key = scrypt(password.encode(), salt, key_len=32, N=2**14, r=8, p=1)

    # Generate a random IV for AES encryption
    iv = get_random_bytes(AES.block_size)

    # Encrypt the file data with AES in GCM mode for authentication and encryption
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    encrypted_data, tag = cipher.encrypt_and_digest(file_data)

    # Combine the salt, IV, tag, and encrypted data
    encrypted_file = salt + iv + tag + encrypted_data

    # Save the encrypted file
    with open(output_path, "wb") as f:
        f.write(encrypted_file)
    print(f"Encrypted PEM file saved to {output_path}")

# Generate RSA key pair (for demo purposes, you should store them securely)
def generate_rsa_keys():
    key = RSA.generate(4096)  # Increased to 4096 bits for more security
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key

# Encrypt the private key using AES-GCM
def encrypt_private_key(private_key, password):
    salt = get_random_bytes(16)
    key = scrypt(password.encode(), salt, key_len=32, N=2**14, r=8, p=1)

    # Encrypt the private key with AES-GCM for authenticated encryption
    cipher = AES.new(key, AES.MODE_GCM)
    encrypted_private_key, tag = cipher.encrypt_and_digest(private_key)

    # Return encrypted private key, salt, IV, and tag for later decryption
    return base64.b64encode(salt + cipher.nonce + tag + encrypted_private_key)

# Encrypt the message using AES-GCM for both encryption and authentication
def encrypt_message_with_aes(message, key):
    cipher = AES.new(hashlib.sha256(key.encode()).digest(), AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(pad(message, AES.block_size))
    return cipher.nonce + tag + ciphertext  # Combine nonce, tag, and ciphertext

# Encrypt the message using RSA
def encrypt_message_with_rsa(message, public_key):
    rsa_cipher = PKCS1_OAEP.new(RSA.import_key(public_key))
    encrypted_message = rsa_cipher.encrypt(message)
    return encrypted_message

# Compress the message using multiple algorithms (zlib + lzma)
def compress_message(message):
    message_compressed = zlib.compress(message)
    message_compressed = lzma.compress(message_compressed)
    return message_compressed

# Convert the message to binary
def message_to_bin(message):
    return ''.join(format(byte, '08b') for byte in message)

# Embed the message into the image using multiple channels (RGB + Alpha)
def embed_message_in_channels(image_path, message, output_path, private_key_file, password):
    message_bytes = message.encode()
    compressed_message = compress_message(message_bytes)

    # Encrypt the compressed message with AES
    key = "super_secret_key"
    aes_encrypted_message = encrypt_message_with_aes(compressed_message, key)

    # Generate RSA keys and encrypt the AES-encrypted message with RSA
    private_key, public_key = generate_rsa_keys()
    rsa_encrypted_message = encrypt_message_with_rsa(aes_encrypted_message, public_key)

    # Encrypt the private key and store it securely
    encrypted_private_key = encrypt_private_key(private_key, password)

    # Save the encrypted private key to a file
    with open(private_key_file, 'wb') as f:
        f.write(encrypted_private_key)

    # Convert encrypted message to binary
    binary_message = message_to_bin(rsa_encrypted_message) + '1111111111111110'  # End marker
    binary_message_length = len(binary_message)

    # Open the image and embed the message in multiple channels
    img = Image.open(image_path)
    pixels = img.load()

    message_index = 0
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            r, g, b = pixels[i, j]

            if message_index < binary_message_length:
                r = (r & 0xFE) | int(binary_message[message_index])  # Modify LSB of Red
                message_index += 1
            if message_index < binary_message_length:
                g = (g & 0xFE) | int(binary_message[message_index])  # Modify LSB of Green
                message_index += 1
            if message_index < binary_message_length:
                b = (b & 0xFE) | int(binary_message[message_index])  # Modify LSB of Blue
                message_index += 1

            if len(img.getbands()) == 4:
                a = pixels[i, j][3]
                if message_index < binary_message_length:
                    a = (a & 0xFE) | int(binary_message[message_index])  # Modify LSB of Alpha
                    message_index += 1
                pixels[i, j] = (r, g, b, a)
            else:
                pixels[i, j] = (r, g, b)

            if message_index >= binary_message_length:
                break
        if message_index >= binary_message_length:
            break

    img.save(output_path)
    print("Data Embedded Successfully!")

    return f"Encrypted private key saved to {private_key_file}"

# Example usage
private_key_file = 'private_key_encrypted.pem'
password = "strong_password_here"
result = embed_message_in_channels(
    r"input_image.jpg",
    "Voter ID: 1, Name: John Doe, Aadhaar: 123456789012, Mobile: 9876543210, Age: 28",
    r"output_image.png",
    private_key_file,
    password
)
output_path = "private_key_encrypted.pem"
encrypt_file(private_key_file, password, output_path)
print(result)

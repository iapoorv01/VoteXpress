import zlib
import lzma
import base64
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Protocol.KDF import scrypt
from Crypto.Util.Padding import unpad
from PIL import Image
import hashlib


def decrypt_file(encrypted_file_path, password, output_path):
    with open(encrypted_file_path, "rb") as f:
        encrypted_data = f.read()

    # Extract the salt, IV, tag, and the encrypted file content from the saved encrypted file
    salt = encrypted_data[:16]  # First 16 bytes are the salt
    iv = encrypted_data[16:32]  # Next 16 bytes are the IV
    tag = encrypted_data[32:48]  # The next 16 bytes are the MAC tag (authentication tag)
    encrypted_file_content = encrypted_data[48:]  # The remaining data is the encrypted file content

    # Derive the decryption key from the password using the same salt
    key = scrypt(password.encode(), salt, key_len=32, N=2 ** 14, r=8, p=1)

    # Decrypt the file content using AES-GCM
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    try:
        # Decrypt and verify the integrity using the tag
        decrypted_file_content = cipher.decrypt_and_verify(encrypted_file_content, tag)
    except ValueError:
        print("MAC verification failed! Decryption failed.")
        return

    # Save the decrypted content back to the output file
    with open(output_path, "wb") as f:
        f.write(decrypted_file_content)

    print(f"Decrypted file saved to {output_path}")


# Decrypt the private key using AES (Reverse of encryption)
def decrypt_private_key(encrypted_private_key_b64, password):
    # Decode the encrypted private key from base64
    encrypted_data = base64.b64decode(encrypted_private_key_b64)

    # Extract the salt, IV (nonce), tag, and encrypted private key from the encrypted data
    salt = encrypted_data[:16]  # The first 16 bytes are the salt
    iv = encrypted_data[16:32]  # The next 16 bytes are the IV (nonce)
    tag = encrypted_data[32:48]  # The next 16 bytes are the tag (authentication tag)
    encrypted_private_key = encrypted_data[48:]  # The remaining data is the encrypted private key

    # Derive the key from the password and salt
    key = scrypt(password.encode(), salt, key_len=32, N=2**14, r=8, p=1)

    # Initialize the AES cipher in GCM mode with the derived key and the IV (nonce)
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)

    try:
        # Decrypt the private key and verify with the tag
        decrypted_private_key = cipher.decrypt_and_verify(encrypted_private_key, tag)
    except ValueError:
        # If the MAC (Message Authentication Code) fails, decryption is not successful
        print("MAC verification failed! Decryption failed.")
        return None

    # Return the decrypted private key
    return decrypted_private_key

# Decrypt the AES-encrypted message using RSA
def decrypt_message_with_rsa(encrypted_message, private_key):
    # Import the private key for decryption
    rsa_cipher = PKCS1_OAEP.new(RSA.import_key(private_key))

    # Decrypt the encrypted message
    decrypted_message = rsa_cipher.decrypt(encrypted_message)

    return decrypted_message



def decrypt_message_with_aes(encrypted_message, key):
    # Extract nonce, tag, and ciphertext from the encrypted message
    nonce = encrypted_message[:16]  # First 16 bytes are the nonce (AES.block_size)
    tag = encrypted_message[16:32]  # Next 16 bytes are the tag
    ciphertext = encrypted_message[32:]  # The rest is the ciphertext

    # Generate the key using SHA256 (256-bit key for AES)
    aes_key = hashlib.sha256(key.encode()).digest()

    # Initialize the AES cipher in GCM mode using the nonce and key
    cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)

    try:
        # Decrypt the ciphertext and verify the tag
        decrypted_message = cipher.decrypt_and_verify(ciphertext, tag)
    except ValueError:
        print("MAC check failed! The data might have been tampered with or the key is incorrect.")
        return None

    # Return the decrypted (original) message
    return unpad(decrypted_message, AES.block_size)  # Remove padding to get the original message


# Decompress the message (Reverse of compression)
def decompress_message(message):
    """Decompress the message using zlib and lzma."""
    message_decompressed = lzma.decompress(message)
    message_decompressed = zlib.decompress(message_decompressed)
    return message_decompressed

# Extract the embedded message from the image
def extract_message_from_image(image_path, private_key_file, password):
    """Extract the hidden message from the image."""

    # Load the image
    img = Image.open(image_path)
    pixels = img.load()

    # Extract the binary message embedded in the image
    binary_message = ""
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            r, g, b = pixels[i, j]

            # Extract the LSB of Red, Green, and Blue channels
            binary_message += str(r & 1)
            binary_message += str(g & 1)
            binary_message += str(b & 1)

            # Extract from the Alpha channel if present (RGBA)
            if len(img.getbands()) == 4:
                a = pixels[i, j][3]
                binary_message += str(a & 1)

    # Remove the end marker (which is added during embedding)
    end_marker = '1111111111111110'
    binary_message = binary_message.split(end_marker)[0]

    # Convert the binary message back to bytes
    byte_message = bytearray()
    for i in range(0, len(binary_message), 8):
        byte_message.append(int(binary_message[i:i + 8], 2))

    # Load the encrypted private key from the file
    with open(private_key_file, 'rb') as f:
        encrypted_private_key_b64 = f.read()

    # Decrypt the private key
    decrypted_private_key = decrypt_private_key(encrypted_private_key_b64, password)

    # Decrypt the AES-encrypted message using RSA
    rsa_encrypted_message = byte_message
    rsa_decrypted_message = decrypt_message_with_rsa(rsa_encrypted_message, decrypted_private_key)

    # Decrypt the message using AES
    aes_encrypted_message = rsa_decrypted_message
    aes_decrypted_message = decrypt_message_with_aes(aes_encrypted_message, "super_secret_key")

    # Decompress the message
    decompressed_message = decompress_message(aes_decrypted_message)

    # Convert the decompressed message back to a string
    message = decompressed_message.decode()

    return message


# Example usage
private_key_file = 'private_key_encrypted.pem'  # File where the encrypted private key is stored
password = "strong_password_here"  # Password used to encrypt the private key
encrypted_file_path = private_key_file  # Path to the encrypted PEM file
output_path = 'private_key_encrypted.pem'  # Path to save the decrypted PEM file

# Decrypt the file
decrypt_file(encrypted_file_path, password, output_path)

extracted_message = extract_message_from_image(
    r"output_image.png",  # Path to the image with the hidden message
    private_key_file,  # Path to the encrypted private key file
    password  # Password for decrypting the private key
)
print(f"Extracted Message: {extracted_message}")

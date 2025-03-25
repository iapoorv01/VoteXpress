import qrcode


def generate_qr_code(voter_data, file_name):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    # Add voter data to the QR code
    qr.add_data(voter_data)
    qr.make(fit=True)

    # Create and save the image
    img = qr.make_image(fill='black', back_color='white')
    img.save(file_name)


# Example voter data
voter_data = "Voter ID: 1, Name: John Doe, Aadhaar: 123456789012, Mobile: 9876543210, Age: 28"
generate_qr_code(voter_data, "voter1_qr.png")

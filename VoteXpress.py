import cv2
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import tkinter as tk
from tkinter import messagebox
import speech_recognition as sr
import threading
import face_recognition
import numpy as np
import ast
# Define the scope of access for Google Sheets API
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file"]

# Path to your service account credentials file (replace with your actual file path)
creds = ServiceAccountCredentials.from_json_keyfile_name('trial.json', scope)

# Authenticate with Google Sheets API
client = gspread.authorize(creds)

# Open the Google Sheet for voter data
spreadsheet_id = '1PULy8xQG2kTreo_zxwnSVHfZ78FzdpVFUmXpipPFZ9U'
sheet = client.open_by_key(spreadsheet_id).sheet1  # Access the first sheet for voters

# Open the Google Sheet for operator data (from OperatorDatabase)
operator_spreadsheet_id = '1lu8fSY9nHvZRVracqnH2AMLsqZxm0F5P4NIWPHIEwVw'  # Operator database ID
operator_sheet = client.open_by_key(operator_spreadsheet_id).sheet1  # Access the first sheet for operators

# Language dictionary to store translations for English and Hindi
translations = {
    "en": {
        "title": "Polling Booth QR Code Scanner",
        "username": "Username:",
        "password": "Password:",
        "login_button": "Login",
        "scan_button": "Start Scanning",
        "exit_button": "Exit",
        "scan_qr_instruction": "Scan a QR code to begin",
        "please_login": "Please log in",
        "login_successful": "Login successful! Assigned to {assigned_station}.",
        "invalid_password": "Invalid password. Please try again.",
        "operator_not_found": "Operator not found in the database.",
        "command_not_recognized": "Command not recognized. Try 'scan qr' or 'exit'.",
        "voter_status_not_found": "Voter not found in the database.",
        "voter_data_mismatch": "Voter data does not match with the database.",
        "voter_underage": "Voter is below 18 years old and cannot vote.",
        "voter_already_voted": "Voter has already voted at {station}.",
        "voter_voted": "Voter {name} has been marked as 'Voted' at {station}.",
        "face_matching_in_progress": 'Face matching in progress...',
        "face_matched": 'Face matched for voter',
        'proceeding_with_status': 'Proceeding with status update.',
        'face_not_matched': 'Face not matched for voter. Please try again.'
    },
    "hi": {
        "title": "पोलिंग बूथ क्यूआर कोड स्कैनर",
        "username": "उपयोगकर्ता नाम:",
        "password": "पासवर्ड:",
        "login_button": "लॉग इन करें",
        "scan_button": "स्कैन करना शुरू करें",
        "exit_button": "बाहर निकलें",
        "scan_qr_instruction": "QR कोड स्कैन करने के लिए शुरू करें",
        "please_login": "कृपया लॉगिन करें",
        "login_successful": "लॉगिन सफल! सौंपा गया स्टेशन: {assigned_station}",
        "invalid_password": "गलत पासवर्ड। कृपया पुनः प्रयास करें।",
        "operator_not_found": "ऑपरेटर डेटा में नहीं मिला।",
        "command_not_recognized": "कमान्ड पहचानी नहीं गई। 'scan qr' या 'exit' आज़माएं।",
        "voter_status_not_found": "वोटर डेटा में नहीं मिला।",
        "voter_data_mismatch": "वोटर डेटा डेटाबेस से मेल नहीं खाता।",
        "voter_underage": "वोटर 18 साल से कम उम्र का है और वोट नहीं कर सकता।",
        "voter_already_voted": "वोटर ने पहले ही {station} पर वोट किया है।",
        "voter_voted": "वोटर {name} को '{station}' पर 'वोट' के रूप में चिह्नित किया गया है।",
        "face_matching_in_progress": "चेहरे का मिलान हो रहा है...",
        "face_matched": "वोटर के लिए चेहरा मेल खाता है",
        "proceeding_with_status": "स्थिति अपडेट की प्रक्रिया की जा रही है।",
        "face_not_matched": "वोटर के लिए चेहरा मेल नहीं खाता है। कृपया पुनः प्रयास करें।",
    }
}


# Function to get the translation for the selected language
def get_translation(language, key, **kwargs):
    translation = translations.get(language, {}).get(key, key)
    return translation.format(**kwargs) if kwargs else translation


# Function to check and update voter status
def check_and_update_voter_status(voter_data, selected_station, result_label, language):
    voter_data_split = voter_data.split(", ")
    voter_id = voter_data_split[0].split(": ")[1]
    voter_name = voter_data_split[1].split(": ")[1]
    voter_aadhaar = voter_data_split[2].split(": ")[1]
    voter_mobile = voter_data_split[3].split(": ")[1]
    voter_age = int(voter_data_split[4].split(": ")[1])

    # Search for the voter in the Google Sheet
    cell = sheet.find(voter_id)

    if cell:
        row = sheet.row_values(cell.row)  # Fetch the row details

        # Check if all data matches the corresponding fields
        if (row[0] == voter_id and row[1] == voter_name and row[2] == voter_aadhaar and row[3] == voter_mobile and row[
            4] == str(voter_age)):

            if voter_age >= 18:
                if row[5] == "Not Voted":  # Mark as "Voted" in the sheet
                    sheet.update_cell(cell.row, 6, "Voted")  # Update 'Voter Status' column
                    sheet.update_cell(cell.row, 7, selected_station)  # Store the polling station ID in column 7
                    result_label.config(
                        text=get_translation(language, "voter_voted", name=voter_name, station=selected_station),
                        fg='green')
                else:
                    result_label.config(text=get_translation(language, "voter_already_voted", station=row[6]),
                                        fg='orange')
            else:
                result_label.config(text=get_translation(language, "voter_underage"), fg='red')
        else:
            result_label.config(text=get_translation(language, "voter_data_mismatch"), fg='red')
    else:
        result_label.config(text=get_translation(language, "voter_status_not_found"), fg='red')


# Function to scan QR code using OpenCV
def scan_qr_code(result_label, selected_station, language):
    cap = cv2.VideoCapture(0)
    scanned_voter_id = None  # Variable to store voter ID

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        detector = cv2.QRCodeDetector()
        value, pts, qr_code = detector.detectAndDecode(frame)

        if value:
            print(f"QR Code detected: {value}")
            voter_data_split = value.split(", ")
            scanned_voter_id = voter_data_split[0].split(": ")[1]  # Store the voter ID here

            cap.release()
            cv2.destroyAllWindows()

            # Show the QR code scan instruction
            result_label.config(text=get_translation(language, "scan_qr_instruction") + f": {value}", fg='black')

            # Create the Scan Face button after QR code is detected
            face_scan_button = tk.Button(root, text="Scan Face", font=("Helvetica", 14),
                                         bg="#4A90E2", fg="white",
                                         command=lambda: scan_face_for_verification(scanned_voter_id, result_label,
                                                                                    value, selected_station, language, face_scan_button))
            face_scan_button.pack(pady=20)
            return value

        cv2.imshow("QR Code Scanner", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def scan_face_for_verification(voter_id, result_label, voter_data, selected_station, language, face_scan_button):
    # Show "Face matching..." message immediately after face scan button is pressed
    result_label.config(text=get_translation(language, "face_matching_in_progress"), fg='blue')
    root.update()  # Ensure real-time UI update

    # Now, we call match_face only when the button is clicked
    match_result = match_face(voter_id)  # Only passing the voter_id to match_face

    if match_result:
        # Update message and proceed with the status update
        result_label.config(
            text=f"{get_translation(language, 'face_matched')} {voter_id}. {get_translation(language, 'proceeding_with_status')}",
            fg='green')
        root.update()  # Ensure real-time UI update

        # Hide the face scan button after the process
        face_scan_button.pack_forget()

        # Now we can proceed to check and update the voter status after face verification
        check_and_update_voter_status(voter_data, selected_station, result_label, language)
    else:
        # Update message if face doesn't match
        result_label.config(text=f"{get_translation(language, 'face_not_matched')} {voter_id}.", fg='red')
        root.update()  # Ensure real-time UI update


# Ensure real-time UI update


# Capture image from webcam
def capture_image():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    return frame


# Convert image to facial encoding
def get_face_encoding(image):
    face_locations = face_recognition.face_locations(image)
    if face_locations:
        return face_recognition.face_encodings(image, face_locations)[0]
    return None



# Match face with stored encodings

# Function to retrieve stored face encoding from Google Sheets (8th column)
def get_stored_face_encoding(voter_id):
    records = sheet.get_all_values()[1:]  # Skip header row
    for row in records:
        if row[0] == voter_id:  # Assuming 1st column is voter ID
            encoding_str = row[7]  # 8th column contains face encoding
            return np.array(ast.literal_eval(encoding_str))  # Convert string back to numpy array
    return None


# Function to match the face scan with stored face encoding
def match_face(voter_id):
    stored_encoding = get_stored_face_encoding(voter_id)

    if stored_encoding is None:
        print("No face encoding found in the database.")
        return False

    # Capture a new image for face scanning
    image = capture_image()
    new_encoding = get_face_encoding(image)

    if new_encoding is None:
        print("No face detected. Try again.")
        return False

    # Compare the new encoding with the stored encoding
    match = face_recognition.compare_faces([stored_encoding], new_encoding)
    distance = face_recognition.face_distance([stored_encoding], new_encoding)[0]

    if match[0]:
        print(f"Match Found for {voter_id} (Confidence: {1 - distance:.2f})")
        return True
    else:
        print(f"No match found for {voter_id}.")
        return False


# Function to verify operator login from Google Sheet
def operator_login(username, password, result_label, login_button, language):
    try:
        cell = operator_sheet.find(username)

        if cell:
            row = operator_sheet.row_values(cell.row)

            stored_password = row[1]  # Retrieve the stored password

            if stored_password == password:
                assigned_station = row[2]
                result_label.config(
                    text=get_translation(language, "login_successful", assigned_station=assigned_station), fg='green')

                login_button.pack_forget()

                root.after(2000, lambda: result_label.config(text=get_translation(language, "scan_qr_instruction"),
                                                             fg='black'))  # Reset message after 2 seconds

                return assigned_station
            else:
                result_label.config(text=get_translation(language, "invalid_password"), fg='red')
        else:
            result_label.config(text=get_translation(language, "operator_not_found"), fg='red')

    except Exception as e:
        result_label.config(text=get_translation(language, "invalid_password"), fg='red')
        print(f"Error: {e}")

    return None


# Voice Command Listener
def listen_for_command(language):
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening for commands...")
        recognizer.adjust_for_ambient_noise(source, duration=1)  # Adjust for ambient noise (1 second)
        try:
            audio = recognizer.listen(source, timeout=10)  # Increase timeout to 10 seconds
            print("Recognizing command...")
            command = recognizer.recognize_google(audio, language=language).lower()
            print(f"Voice Command: {command}")
            return command
        except sr.UnknownValueError:
            print("Could not understand the command. Please speak more clearly.")
            return None
        except sr.RequestError as e:
            print(f"Error with speech recognition service: {e}")
            return None
        except Exception as e:
            print(f"An error occurred while listening: {e}")
            return None


# Process the voice command in a thread to not block the UI
def process_voice_command(assigned_station, result_label, language):
    while True:
        command = listen_for_command(language)

        if command:
            if 'scan qr' in command:
                result_label.config(text=get_translation(language, "scan_qr_instruction"), fg='black')
                scan_qr_code(result_label, assigned_station, language)
            elif 'exit' in command:
                print("Exiting the application.")
                root.quit()
            else:
                print(get_translation(language, "command_not_recognized"))


# Main function to create the GUI
def create_gui():
    global root
    root = tk.Tk()
    root.title("Polling Booth QR Scanner")

    # Set window size
    root.geometry("600x400")

    # Set background color and title font
    root.configure(bg="#f4f4f9")
    title_label = tk.Label(root, text=get_translation("en", "title"), font=("Helvetica", 20, "bold"), bg="#f4f4f9",
                           fg="#4A90E2")
    title_label.pack(pady=20)

    # Login Frame
    login_frame = tk.Frame(root, bg="#f4f4f9")
    login_frame.pack(pady=10)

    # Username and Password fields with modern styling
    username_label = tk.Label(login_frame, text=get_translation("en", "username"), font=("Helvetica", 12), bg="#f4f4f9")
    username_label.grid(row=0, column=0, padx=10, pady=5)
    username_entry = tk.Entry(login_frame, font=("Helvetica", 12))
    username_entry.grid(row=0, column=1, padx=10, pady=5)

    password_label = tk.Label(login_frame, text=get_translation("en", "password"), font=("Helvetica", 12), bg="#f4f4f9")
    password_label.grid(row=1, column=0, padx=10, pady=5)
    password_entry = tk.Entry(login_frame, show="*", font=("Helvetica", 12))
    password_entry.grid(row=1, column=1, padx=10, pady=5)

    # Language selection dropdown (Only English and Hindi)
    language_var = tk.StringVar(value="en")  # Default language is English
    language_options = ["en", "hi"]  # Only English and Hindi
    language_dropdown = tk.OptionMenu(root, language_var, *language_options)
    language_dropdown.pack(pady=10)

    # Result label to show login status
    result_label = tk.Label(root, text=get_translation("en", "please_login"), font=("Arial", 14), height=2,
                            bg="#f4f4f9")
    result_label.pack(pady=20)

    # Function to start the login process
    def login():
        username = username_entry.get()
        password = password_entry.get()
        language = language_var.get()
        assigned_station = operator_login(username, password, result_label, login_button, language)

        if assigned_station:
            login_frame.pack_forget()
            result_label.config(text=get_translation(language, "scan_qr_instruction"), fg='black')

            # Start listening for voice commands after login
            threading.Thread(target=process_voice_command, args=(assigned_station, result_label, language),
                             daemon=True).start()

            # Scan button to start QR code scanning
            scan_button = tk.Button(root, text=get_translation(language, "scan_button"), font=("Helvetica", 14),
                                    bg="#4A90E2", fg="white",
                                    command=lambda: start_scanning(assigned_station, result_label, language))
            scan_button.pack(pady=20)

            # Exit button to close the application
            exit_button = tk.Button(root, text=get_translation(language, "exit_button"), font=("Helvetica", 14),
                                    bg="#e94e77", fg="white", command=root.quit)
            exit_button.pack(pady=20)

    # Login button
    login_button = tk.Button(root, text=get_translation("en", "login_button"), font=("Helvetica", 14), bg="#4A90E2",
                             fg="white", command=login)
    login_button.pack(pady=20)

    # Function to start QR code scanning
    def start_scanning(assigned_station, result_label, language):
        scan_qr_code(result_label, assigned_station, language)  # Start QR scanning

    # Function to update the UI language when the dropdown changes
    def update_ui_language(*args):
        language = language_var.get()

        # Update all text elements
        title_label.config(text=get_translation(language, "title"))
        username_label.config(text=get_translation(language, "username"))
        password_label.config(text=get_translation(language, "password"))
        login_button.config(text=get_translation(language, "login_button"))
        result_label.config(text=get_translation(language, "please_login"))

        # Update buttons' texts (scan & exit)
        if 'scan_button' in locals():
            scan_button.config(text=get_translation(language, "scan_button"))
        if 'exit_button' in locals():
            exit_button.config(text=get_translation(language, "exit_button"))

    # Trace language change and update UI accordingly
    language_var.trace("w", update_ui_language)

    # Run the Tkinter event loop
    root.mainloop()


if __name__ == "__main__":
    create_gui()  # Start the GUI application

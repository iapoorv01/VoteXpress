import cv2
import firebase_admin
from firebase_admin import credentials, firestore
import tkinter as tk
from tkinter import messagebox
import speech_recognition as sr
import threading
import face_recognition
import numpy as np
import ast
import random
import math
import winsound
# Initialize Firebase Admin SDK
cred = credentials.Certificate("govt-database-firebase-adminsdk-fbsvc-a7ffad6280.json")
firebase_admin.initialize_app(cred)

# Initialize Firestore client
db = firestore.client()

# Firestore collections
voters_ref = db.collection('voters')  # Voter data
operators_ref = db.collection('operators')  # Operator data

# Language dictionary for translations (as you have defined)
translations = {
    "English": {
        "instruction_text": """
    1. Login with the authorized ID and password provided \n        by the government.
    2. Make sure no one is looking before typing your password.
    3. Do not share your password with anyone.
    """,
        "title": "Polling Booth QR Code Scanner",
        "login" : "Login",
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
        'face_not_matched': 'Face not matched for voter. Please try again.',
        'missing_info': 'Missing information in Voter ID. Please try again.',
        'QR_DATA': 'Scanned Data:',
        'scan_face': 'Scan Face'
    },
    "Hindi": {
        "instruction_text":"""
    1. सरकार द्वारा प्रदान की गई अधिकृत आईडी और पासवर्ड के साथ \n        लॉगिन करें।
    2. पासवर्ड टाइप करने से पहले यह सुनिश्चित करें कि कोई नहीं देख रहा हो।
    3. अपना पासवर्ड किसी के साथ साझा न करें।
    """,
        "title": "पोलिंग बूथ क्यूआर कोड स्कैनर",
        "login": "लॉगिन",
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
        'missing_info': 'वोटर आईडी में कुछ जानकारी गायब है। कृपया फिर से प्रयास करें।',
        'QR_DATA': 'स्कैन किया गया डेटा:',
        'scan_face': 'चेहरा स्कैन करें'


    }
}

# Function to get the translation for the selected language
def get_translation(language, key, **kwargs):
    translation = translations.get(language, {}).get(key, key)
    return translation.format(**kwargs) if kwargs else translation

def play_beep():
    # Frequency is in hertz (e.g., 1000 Hz), duration is in milliseconds (e.g., 500 ms)
    winsound.Beep(1000, 500)
# Function to check and update voter status in Firestore
def check_and_update_voter_status(voter_data, selected_station, result_label, language):
    # Parse the voter data
    voter_data_split = voter_data.split(", ")
    voter_id = voter_data_split[0].split(": ")[1]
    voter_name = voter_data_split[1].split(": ")[1]
    voter_aadhaar = voter_data_split[2].split(": ")[1]
    voter_mobile = voter_data_split[3].split(": ")[1]
    voter_age = int(voter_data_split[4].split(": ")[1])

    # Fetch the voter document from Firestore
    voter_doc = voters_ref.document(voter_id).get()

    if voter_doc.exists:
        voter_data_from_db = voter_doc.to_dict()

        # Check if all data matches the corresponding fields
        if (voter_data_from_db["name"] == voter_name and
            voter_data_from_db["aadhaar_number"] == voter_aadhaar and
            voter_data_from_db["mobile_number"] == voter_mobile and
            voter_data_from_db["age"] == voter_age):

            if voter_age >= 18:
                if voter_data_from_db["voter_status"] == "Not Voted":  # Update the status to "Voted"
                    voters_ref.document(voter_id).update({
                        "voter_status": "Voted",
                        "polling_station": selected_station
                    })
                    result_label.config(
                        text=get_translation(language, "voter_voted", name=voter_name, station=selected_station),
                        fg='green')
                else:
                    result_label.config(
                        text=get_translation(language, "voter_already_voted", station=voter_data_from_db["polling_station"]),
                        fg='orange')
            else:
                result_label.config(text=get_translation(language, "voter_underage"), fg='red')
        else:
            result_label.config(text=get_translation(language, "voter_data_mismatch"), fg='red')
    else:
        result_label.config(text=get_translation(language, "voter_status_not_found"), fg='red')



# Function to scan QR code using OpenCV
def scan_qr_code(result_label, selected_station, language, scan_button,big_canvas):
    cap = cv2.VideoCapture(0)
    scanned_voter_id = None  # Variable to store voter ID

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        detector = cv2.QRCodeDetector()
        value, pts, qr_code = detector.detectAndDecode(frame)

        if value:
            play_beep()
            print(f"QR Code detected: {value}")
            voter_data_split = value.split(", ")

            # Define the expected fields
            expected_fields = ["Voter ID", "Name", "Aadhaar", "Mobile", "Age"]

            # Initialize list for missing fields
            missing_fields = []

            # Loop through the expected fields and check for missing data
            for i, field in enumerate(expected_fields):
                # Check if the corresponding data in voter_data_split is missing
                if i >= len(voter_data_split) or not voter_data_split[i].strip():
                    missing_fields.append(field)

            # If any field is missing, show the missing fields
            if missing_fields:
                result_label.config(
                    text=f"{get_translation(language, 'missing_info')}: {', '.join(missing_fields)}",
                    fg='red'
                )
                cap.release()
                cv2.destroyAllWindows()
                return  # Stop processing if fields are missing

            # If all fields are present, store the voter ID
            scanned_voter_id = voter_data_split[0].split(": ")[1]

            cap.release()
            cv2.destroyAllWindows()
            result_label.config(
                text=get_translation(language, "QR_DATA") + "\n" + "\n".join(value.split(",")),
                fg='blue', font=("Javanese Text", 25),height=8
            )

            # Check if voter has already voted
            voter_doc = voters_ref.document(scanned_voter_id).get()
            if voter_doc.exists:
                voter_data_from_db = voter_doc.to_dict()

                if voter_data_from_db["voter_status"] == "Voted":
                    # Perform re-verification check
                    reverification_ref = db.collection('reverification_attempts')
                    reverification_doc = reverification_ref.document(scanned_voter_id)

                    # Check if the document already exists (the voter has attempted verification before)
                    reverification_data = reverification_doc.get()

                    if reverification_data.exists:
                        # If the document exists, increment the number of attempts
                        existing_data = reverification_data.to_dict()
                        new_attempt_count = existing_data["attempt_count"] + 1
                        polling_stations = existing_data["polling_stations"]

                        # Add the new polling station to the list (if not already added)
                        if selected_station not in polling_stations:
                            polling_stations.append(selected_station)

                        # Update the re-verification document with the new attempt count and polling stations
                        reverification_doc.update({
                            "attempt_count": new_attempt_count,
                            "polling_stations": polling_stations,
                            "last_attempt_time": firestore.SERVER_TIMESTAMP
                        })
                    else:
                        # If no document exists, create a new one with initial data
                        voter_name = voter_data_from_db["name"]
                        voter_aadhaar = voter_data_from_db["aadhaar_number"]
                        voter_mobile = voter_data_from_db["mobile_number"]
                        voter_age = voter_data_from_db["age"]

                        reverification_doc.set({
                            "attempt_count": 1,
                            "polling_stations": [selected_station],
                            "voter_id": scanned_voter_id,
                            "name": voter_name,
                            "aadhaar_number": voter_aadhaar,
                            "mobile_number": voter_mobile,
                            "age": voter_age,
                            "first_attempt_time": firestore.SERVER_TIMESTAMP,
                            "last_attempt_time": firestore.SERVER_TIMESTAMP
                        })
                    result_label.config(
                            text=get_translation(language, "voter_already_voted", station=voter_data_from_db["polling_station"]),
                            fg='orange',height=4)
                    return

            # Proceed to face scan only if the voter hasn't voted yet and re-verification is successful

            scan_button.pack_forget()  # Hide the QR scan button after QR scan
            # Create the Face Scan button after QR code is detected
            # Create the "Scan Face" button on canvas after QR code is scanned
            face_scan_button = tk.Button(root,
                                         text=get_translation(language, "scan_face"),
                                         font=("STENCIL", 30),
                                         bg="#4A90E2", fg="white",width=33,
                                         command=lambda: scan_face_for_verification(
                                             scanned_voter_id, result_label,
                                             value, selected_station, language,
                                             face_scan_button, scan_button,big_canvas
                                         )
            )
            face_scan_button_window = big_canvas.create_window(430, 700, window=face_scan_button)

            return value

        cv2.imshow("QR Code Scanner", frame)
        cv2.resizeWindow("QR Code Scanner", 750, 490)
        cv2.moveWindow("QR Code Scanner", 151, 192)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Function to handle face scan and hide/show buttons accordingly
def scan_face_for_verification(voter_id, result_label, voter_data, selected_station, language, face_scan_button,scan_button,big_canvas):
    # Show "Face matching..." message immediately after face scan button is pressed
    result_label.config(text=get_translation(language, "face_matching_in_progress"), fg='blue',height=4)
    root.update()  # Ensure real-time UI update

    # Call match_face only when the button is clicked
    match_result = match_face(voter_id)  # Only passing the voter_id to match_face

    if match_result:
        # Update message and proceed with the status update
        result_label.config(
            text=f"{get_translation(language, 'face_matched')} {voter_id}. {get_translation(language, 'proceeding_with_status')}",
            fg='green',height=4)
        root.update()  # Ensure real-time UI update

        # Hide the face scan button after the process

        # Proceed to check and update the voter status after face verification
        check_and_update_voter_status(voter_data, selected_station, result_label, language)

        # Re-show the QR scan button


    else:
        # Update message if face doesn't match
        result_label.config(text=f"{get_translation(language, 'face_not_matched')} {voter_id}.", fg='red',height=4)
        root.update()
    face_scan_button.pack_forget()
    scan_button = tk.Button(root, text=get_translation(language, "scan_button"), font=("Helvetica", 30),
                            bg="#4A90E2", fg="white", width=33,
                            command=lambda: scan_qr_code(result_label,selected_station, language,
                                                           scan_button, big_canvas))
    scan_button_window = big_canvas.create_window(430, 700,
                                                  window=scan_button)




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

# Face matching functions (same as before, using Firestore instead of Google Sheets)
def get_stored_face_encoding(voter_id):
    voter_doc = voters_ref.document(voter_id).get()
    if voter_doc.exists:
        voter_data = voter_doc.to_dict()
        encoding_str = voter_data.get("eye_retina")
        if encoding_str:
            return np.array(ast.literal_eval(encoding_str))
    return None


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


# Function to verify operator login from Firestore
def operator_login(username, password, login_label, login_button, language):
    try:
        operator_doc = operators_ref.document(username).get()

        if operator_doc.exists:
            operator_data = operator_doc.to_dict()
            stored_password = operator_data.get("operator_password")

            if stored_password == password:
                assigned_station = operator_data.get("operator_station")
                login_label.config(
                    text=get_translation(language, "login_successful", assigned_station=assigned_station), fg='green')

                login_button.pack_forget()

                root.after(2000, lambda: login_label.config(text=get_translation(language, "scan_qr_instruction"),
                                                             fg='black'))  # Reset message after 2 seconds

                return assigned_station
            else:
                login_label.config(text=get_translation(language, "invalid_password"), fg='red')
        else:
            login_label.config(text=get_translation(language, "operator_not_found"), fg='red')

    except Exception as e:
        login_label.config(text=get_translation(language, "invalid_password"), fg='red')
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




def create_gui():
    global root
    root = tk.Tk()
    root.title("Polling Booth QR Scanner")

    # Set window size and make it full-screen
    root.attributes("-fullscreen", True)  # Set to full screen

    # Function to toggle full screen on Escape key press
    def toggle_full_screen(event=None):
        current_state = root.attributes("-fullscreen")
        root.attributes("-fullscreen", not current_state)  # Toggle full-screen mode

    # Bind Escape key to toggle full screen
    root.bind("<Escape>", toggle_full_screen)

    # Set background color and title font
    root.configure(bg="#ffffff")

    # Create a canvas for the glitter effect
    glitter_canvas = tk.Canvas(root, width=root.winfo_screenwidth(), height=root.winfo_screenheight(), bg="white",
                               highlightthickness=0)
    glitter_canvas.place(x=0, y=0)

    # Maximum number of glitter particles allowed at a time
    MAX_GLITTER_PARTICLES = 1000
    active_glitter = []  # List to store the active glitter particle IDs

    # Store the velocities for the glitter particles
    velocities = {}

    # Function to create a random glitter particle
    def create_glitter():
        size = random.randint(2, 6)  # Random size for glitter particle
        x = random.randint(0, root.winfo_screenwidth())  # Random X position
        y = random.randint(0, root.winfo_screenheight())  # Random Y position
        glitter_color = '#38b6ff'  # Sky blue color
        # Create a glitter particle on the canvas
        glitter_id = glitter_canvas.create_oval(x, y, x + size, y + size, fill=glitter_color, outline=glitter_color)

        # Add the new glitter particle to the active list
        active_glitter.append(glitter_id)

        # Initialize its velocity to zero (its moving initially)
        velocities[glitter_id] = {'vx': random.uniform(-5, 5), 'vy': random.uniform(-5, 5)}

        # Set the glitter ball to disappear after 10 seconds
        glitter_canvas.after(10000, lambda: remove_glitter(glitter_id))  # Remove glitter after 10 seconds

        # If there are more than the maximum allowed glitter particles, remove the oldest one
        if len(active_glitter) > MAX_GLITTER_PARTICLES:
            remove_glitter(active_glitter.pop(0))  # Remove the first glitter particle

    # Function to remove a glitter particle
    def remove_glitter(glitter_id):
        glitter_canvas.delete(glitter_id)  # Delete the glitter particle
        if glitter_id in active_glitter:
            active_glitter.remove(glitter_id)
            del velocities[glitter_id]  # Remove its velocity

    # Function to animate the glitter particles
    def animate_glitter():
        create_glitter()  # Create new glitter particle
        root.after(50, animate_glitter)  # Call this function every 50 milliseconds (asynchronously)

    # Start the glitter animation
    animate_glitter()

    # Function to check if the mouse is close to a glitter particle
    def is_cursor_near_particle(glitter_id, cursor_x, cursor_y):
        coords = glitter_canvas.coords(glitter_id)
        if coords:  # Ensure coords are valid (non-empty)
            x1, y1, x2, y2 = coords
            # Check if the cursor is within a small range around the glitter particle
            distance = 15  # The distance at which the glitter particle will react to the cursor
            if x1 - distance <= cursor_x <= x2 + distance and y1 - distance <= cursor_y <= y2 + distance:
                return True
        return False

    # Function to calculate the bounce away vector and update velocity
    def bounce_away(glitter_id, cursor_x, cursor_y):
        coords = glitter_canvas.coords(glitter_id)
        if coords:
            x1, y1, x2, y2 = coords
            # Get the center of the glitter particle
            glitter_center_x = (x1 + x2) / 2
            glitter_center_y = (y1 + y2) / 2

            # Calculate the vector from the glitter to the cursor
            dx = cursor_x - glitter_center_x
            dy = cursor_y - glitter_center_y
            distance = math.sqrt(dx ** 2 + dy ** 2)

            if distance < 15:  # If the cursor is within the "bounce" distance
                # Normalize the vector (make it unit length)
                if distance != 0:
                    dx /= distance
                    dy /= distance

                # Apply a "bounce" effect by setting the velocity in the opposite direction
                velocity_factor = 10  # Adjust the bounce strength
                velocities[glitter_id]['vx'] = -dx * velocity_factor
                velocities[glitter_id]['vy'] = -dy * velocity_factor

    # Function to update glitter position and simulate bouncing effect
    def update_glitter_positions():
        for glitter_id in active_glitter:
            # Move the glitter according to its velocity
            vel = velocities[glitter_id]
            glitter_canvas.move(glitter_id, vel['vx'], vel['vy'])

            # Check for boundary collision and apply a bounce effect (bounce inside the screen)
            coords = glitter_canvas.coords(glitter_id)
            if coords:
                x1, y1, x2, y2 = coords
                if x1 <= 0 or x2 >= root.winfo_screenwidth():
                    vel['vx'] = -vel['vx']  # Reverse horizontal velocity if boundary is hit
                if y1 <= 0 or y2 >= root.winfo_screenheight():
                    vel['vy'] = -vel['vy']  # Reverse vertical velocity if boundary is hit

        root.after(50, update_glitter_positions)  # Call this function to update positions every 50ms

    # Function to move glitter particles with the cursor (this triggers the bounce effect)
    def move_glitter_with_cursor(event):
        for glitter_id in active_glitter:
            if is_cursor_near_particle(glitter_id, event.x, event.y):
                bounce_away(glitter_id, event.x, event.y)

    # Bind the mouse motion event to make glitter bounce away from the cursor
    root.bind("<Motion>", move_glitter_with_cursor)

    # Start updating the glitter positions (bouncy behavior)
    update_glitter_positions()

    # Load the logo using Tkinter's PhotoImage
    logo_image = tk.PhotoImage(file="VoteXpress logo.png")  # Replace with your logo path

    # Create label for the logo and place it at the top-left corner
    logo_label = tk.Label(root, image=logo_image, bg="#ffffff")
    logo_label.place(x=-20, y=-30)

    # Functionality for buttons
    def minimize_window():
        root.iconify()

    def toggle_maximize():
        current_state = root.state()  # Get the current window state
        if current_state == 'normal':
            root.state('zoomed')  # Maximize the window
        else:
            root.state('normal')  # Restore the window to normal size

    def close_window():
        root.destroy()

    # Create a frame to hold the buttons
    button_frame = tk.Frame(root, bg="white")
    button_frame.pack(side=tk.TOP, anchor="ne", padx=5, pady=5)

    # Button Styles
    btn_style = {
        "bg": "white",
        "fg": "#38b6ff",
        "font": ("Arial", 20),
        "width": 3,
        "bd": 4,  # Border width
        "relief": "sunken",  # Border style
        "highlightbackground": "#38b6ff",  # Border color when not focused
        "highlightcolor": "#38b6ff",  # Border color when focused
        "highlightthickness": 2  # Thickness of the highlight border
    }

    # Minimize Button
    min_btn = tk.Button(button_frame, text="-", command=minimize_window, **btn_style)
    min_btn.pack(side=tk.LEFT, padx=2)

    # Maximize Button
    max_btn = tk.Button(button_frame, text="🗖", command=toggle_maximize, **btn_style)
    max_btn.pack(side=tk.LEFT, padx=2, pady=1)

    # Close Button
    close_btn = tk.Button(button_frame, text="✖", command=close_window, **btn_style)
    close_btn.pack(side=tk.LEFT, padx=2)

    # Title label


    shadow_frame = tk.Frame(root, bg="#e0dfdf", bd=0)  # Dark gray background for the shadow frame
    shadow_frame.pack(pady=30, padx=30, expand=True)

    # Create the actual login box frame
    login_box_frame = tk.Frame(shadow_frame, bg="#ffffff", bd=4, relief=tk.GROOVE)
    login_box_frame.pack(pady=10, padx=10, expand=True)

    # Add a label with the text "Login" above the fields in the frame
    login_label = tk.Label(login_box_frame, text=get_translation("English", "login"), font=("Elephant", 95, "bold"), bg="#ffffff")
    login_label.grid(row=0, column=0,padx=20, pady=20, sticky='w')  # Align "Login" label to the top-left corner

    def on_focus_in(event, entry, placeholder, show=""):
        """Remove placeholder text when the entry field is focused."""
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg='#585858')  # Set text color to black when focused
            if show:
                entry.config(show="*")  # For password, hide the characters with "*"

    def on_focus_out(event, entry, placeholder, show=""):
        """Restore placeholder text if the entry field is empty."""
        if entry.get() == '':
            entry.insert(0, placeholder)
            entry.config(fg='#B0B0B0')  # Simulate opacity by using a lighter gray color
            if show:
                entry.config(show='')

    username_placeholder = " Username"
    password_placeholder = " Password"

    # Create the username entry with placeholder
    username_entry = tk.Entry(login_box_frame, font=("Perpetua", 40), relief=tk.GROOVE, borderwidth=2,
                              fg='#B0B0B0')  # Lighter gray for placeholder text
    username_entry.insert(0, username_placeholder)  # Insert placeholder text initially
    username_entry.grid(row=1, column=0, columnspan=4, padx=20, pady=30, sticky='ew')

    # Creating the password entry with placeholder text
    password_entry = tk.Entry(login_box_frame, font=("Perpetua", 40), relief=tk.GROOVE, borderwidth=2,
                              fg='#B0B0B0')  # Lighter gray for placeholder text
    password_entry.insert(0, password_placeholder)  # Insert placeholder text initially
    password_entry.grid(row=2, column=0, columnspan=4, padx=20, pady=10, sticky='ew')

    # Binding focus events to handle placeholder and opacity effect
    username_entry.bind("<FocusIn>", lambda event: on_focus_in(event, username_entry, username_placeholder))
    username_entry.bind("<FocusOut>", lambda event: on_focus_out(event, username_entry, username_placeholder))

    password_entry.bind("<FocusIn>", lambda event: on_focus_in(event, password_entry, password_placeholder, show="*"))
    password_entry.bind("<FocusOut>", lambda event: on_focus_out(event, password_entry, password_placeholder, show="*"))

    # Language selection dropdown inside the login box frame
    # Language selection dropdown inside the login box frame
    language_var = tk.StringVar(value="English")
    language_options = ["English", "Hindi"]

    # Custom dropdown menu using Canvas
    def update_dropdown(lang):
        language_var.set(lang)
        canvas.itemconfig(lang_text, text=lang)  # Update the text displayed on the canvas dropdown

    canvas = tk.Canvas(login_box_frame, width=232, height=60, bg="white", highlightthickness=0)
    canvas.grid(row=3, column=0, columnspan=4, pady=30, padx=10)

    canvas.create_oval(5, 5, 55, 55, outline="#24A3FF", width=2)  # Left side curve (bigger)
    canvas.create_oval(185, 5, 230, 55, outline="#24A3FF", width=2)  # Right side curve (bigger)
    canvas.create_rectangle(31, 5, 208, 55, outline="#24A3FF", width=2)  # Middle part (bigger)
    # Middle part

    # Globe icon (Unicode 🌐)
    canvas.create_text(32, 24, text="🌎", font=("Arial", 30), fill="#24A3FF")

    # "English" text (changes dynamically)
    lang_text = canvas.create_text(118, 30, text=language_var.get(), font=("Arial", 22, "bold"), fill="#24A3FF")

    # Right arrow (Unicode ➜)
    canvas.create_text(216, 30, text="➜", font=("Arial", 25), fill="#24A3FF")

    # Create a menu for language options
    menu = tk.Menu(root, tearoff=0, bg="white", fg="black", font=("Arial", 16))

    for lang in language_options:
        menu.add_command(label=lang, command=lambda l=lang: update_dropdown(l))

    def show_menu(event):
        menu.post(event.x_root, event.y_root)

    canvas.bind("<Button-1>", show_menu)

    # Result label to show login status inside the login box frame
    instruction_label = tk.Label(login_box_frame, text=get_translation("English","instruction_text"), font=("Arial", 17), height=4,justify="left", anchor="w", bg="#ffffff")
    instruction_label.grid(row=4, column=0, columnspan=2, pady=20)

    login_label=tk.Label(root, text="", font=("Arial", 17), height=4, justify="left", anchor="w", bg="#ffffff")
    login_label.place(x=800, y=900)
    # Login Button inside the login box frame


    def login():
        username = username_entry.get()
        password = password_entry.get()
        language = language_var.get()
        assigned_station = operator_login(username, password, login_label, login_button, language)

        if assigned_station:
            login_box_frame.pack_forget()
            shadow_frame.pack_forget()
            login_label.place_forget()





            # Create the big canvas
            # Create the big canvas
            big_canvas = tk.Canvas(root, width=1700, height=800, bg="#ffffff",bd=2)  # Modify the height as needed

            # Calculate the position to center the canvas
            canvas_x = (root.winfo_screenwidth() - 1700) / 2  # Centering horizontally
            canvas_y = (root.winfo_screenheight() - 800) / 2  # Centering vertically

            # Place the canvas in the center
            big_canvas.place(x=canvas_x, y=canvas_y)
            result_label = tk.Label(root, text="", font=("Javanese Text", 25), height=4, justify="left", anchor="w",
                                    bg="#ffffff")
            result_label_window = big_canvas.create_window(1300, 400,
                                                           window=result_label)  # Adjust coordinates as needed
            result_label.config(text=get_translation(language, "scan_qr_instruction"), fg='black')
            # Start listening for voice commands after login
            threading.Thread(target=process_voice_command, args=(assigned_station, result_label, language), daemon=True).start()

            # Load the logo using Tkinter's PhotoImage
            vc_image = tk.PhotoImage(file="vc.png")  # Replace with your logo path

            # Store the image in a variable so it doesn't get garbage-collected
            root.logo_image = vc_image  # This keeps the image in memory

            # Create the label for the logo and place it on the canvas using create_image
            vc_label = big_canvas.create_image(20, 30, image=vc_image, anchor="nw")

            # Create the scan button and place it on the canvas
            scan_button = tk.Button(root, text=get_translation(language, "scan_button"), font=("STENCIL", 30),
                                    bg="#4A90E2", fg="white", width=33,
                                    command=lambda: start_scanning(assigned_station, result_label, language,
                                                                   scan_button,big_canvas))
            scan_button_window = big_canvas.create_window(430, 700,
                                                          window=scan_button)  # Place the button at the specified coordinates

            # Create the exit button and place it on the canvas
            exit_button = tk.Button(root, text="Exit", font=("STENCIL", 27), bg="#e94e77", fg="white", width=20,
                                    command=root.quit)
            exit_button_window = big_canvas.create_window(1300, 700, window=exit_button)


    def on_hover(event):
        login_button.config(bg="#3c7dbd")  # Lighter blue when hovered

    def off_hover(event):
        login_button.config(bg="#4A90E2")  # Original blue color when not hovered

    login_button = tk.Button(login_box_frame, text=get_translation("English","login_button"), font=("STENCIL", 25), width=20, bg="#4A90E2", fg="white",
                              highlightthickness=3, bd=0, command=login)

    # Add the hover effect events
    login_button.grid(row=7, column=0, columnspan=20, padx=100, pady=20)
    login_button.bind("<Enter>", on_hover)  # Mouse enters
    login_button.bind("<Leave>", off_hover)
    sizeadjust = tk.Label(login_box_frame, text="", font=("Arial", 30), height=2, bg="#ffffff")
    sizeadjust.grid(row=8, column=0, columnspan=2, pady=20)



    # Function to start QR code scanning
    def start_scanning(assigned_station, result_label, language,scan_button,big_canvas):
        scan_qr_code(result_label, assigned_station, language,scan_button,big_canvas)  # Start QR scanning

    # Function to update the UI language when the dropdown changes
    def update_ui_language(*args):
        language = language_var.get()

        # Update all text elements


        login_label.config(text=get_translation(language, "login"))
        login_button.config(text=get_translation(language, "login_button"))
        instruction_label.config(text=get_translation(language, "instruction_text"))

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

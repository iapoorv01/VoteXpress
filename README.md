# ![image](https://github.com/user-attachments/assets/ebbba7fd-29be-44a4-9f69-93d51690bdfd)
# A Modern Polling Booth Verification System 📊✨

**VoteXpress** is an innovative solution designed to streamline the voter verification process at polling booths using **Advanced Steganography Scanning & Decryption**. By leveraging Firestore, biometric authentication, and an intuitive interface, it empowers polling station operators to verify voters quickly and accurately. Whether you're a tech enthusiast, a developer, or just interested in cutting-edge voting tech, this project is a game-changer!

 <img  alt="Coding" src="https://media.giphy.com/media/xUOxfdB8Ttz0ulAzPG/giphy.gif?cid=ecf05e474s11auycebwq61x7hquhdr5bz15gcm849efchq2c&ep=v1_gifs_search&rid=giphy.gif&ct=g">
 
---

## **Features:**
![image](https://github.com/user-attachments/assets/40212fe8-2393-45c2-9215-6631958487be)

- 🖼️ **Steganography Scanning & Decryption:** Extract voter details from an **image of a QR code** (not the QR code itself) using AES & RSA encryption.
- 🎤 **Voice Commands:** Use voice commands to trigger key actions like scanning and exiting the app.
- 🗳️ **Biometric Voter Verification:** Authenticate voters using **fingerprint & retina scans**.
- 🌐 **Multi-Language Support:** Seamless translation between multiple languages for accessibility.   
- 🔒 **Secure Operator Login:** Authenticate operators with assigned polling station credentials.
- 📈 **Real-time Firestore Database Integration:** Instantly updates voter status as "Voted" after verification.
- 🚨 **Fraud Prevention & Multi-Vote Detection:** Tracks attempts across polling stations & logs suspicious activity.
  
---

## **Installation and Setup** 🛠️

To get started, follow these steps to set up and run the **VoteXpress** app on your machine.

### 1. **Clone the Repository:**
   Clone this repo to your local machine using Git:
   ```bash
   git clone https://github.com/iapoorv01/VoteXpress.git
   cd VoteXpress
   ```

### 2. **Install Required Libraries:**
   Make sure you have Python 3.7 or higher installed. Then, install the dependencies using `pip`:
   ```bash
   pip install -r requirements.txt
   ```

   The `requirements.txt` file includes all necessary libraries, including:
   - `firebase-admin` - For Firestore database integration.
   - `opencv-python` - For image processing.
   - `face-recognition` - For facial authentication.
   - `speech_recognition` - For voice command processing.

### 3. **Set Up Firestore:**
   - Create a Firebase project and enable **Firestore Database**.
   - Download your **service account JSON credentials** file and save it as `firebase_credentials.json`.
   - Place this `firebase_credentials.json` file in the root directory of the project.

### 4. **Run the Application:**
   To run the app, use the following command:
   ```bash
   python VoteXpress.py
   ```
### **5. Generating an Executable (Optional)**  
If you wish to convert VoteXpress into a standalone executable:  
```bash
python -m PyInstaller --onefile --hidden-import=face_recognition --hidden-import=dlib --add-data "shape_predictor_68_face_landmarks.dat;." --icon=Poolling.ico --name=VoteXpress VoteXpress_loader.py
```  
This will generate a `VoteXpress.exe` file inside the `dist/` folder.  

✅ **Move `VoteXpress.exe` to the home directory**, as it requires access to asset files for proper functionality.

   This will launch the graphical user interface (GUI) where you can login, scan an image for steganography-encoded voter data, and track voter status.

### 🔍 **Testing the Scanning Feature**  
To test the scanning functionality, use **`voter1_qr.png`**, as we have implemented a **QR code reader** for demo purposes. You can generate a QR code using:  
```bash
python qr_generation.py
```  
Once **steganography integration** is complete, you will experience the full functionality of our system.  

### 🛠 **Understanding Our Unique Steganography Tool**  
We have designed a **custom steganography tool** for securely embedding and extracting voter data. To provide better clarity on its uniqueness, the **steganography tool for embedding and extracting files** is available separately in the repository.  

### 📌 **Adding Data to Firestore**  
To insert data into Firestore:  
- **Voter data** ➝ Add to **VoterDatabase**  
- **Operator data** ➝ Add to **OperatorDatabase**  

Use the provided script to generate and store the required data in Firestore seamlessly. 🚀  

---

   ![image](https://github.com/user-attachments/assets/0a730b59-6bd0-4524-8ff2-eab1377238d4)

---

## **How It Works** 🧐
![image](https://github.com/user-attachments/assets/3ca2b09f-4e3d-4db5-a629-1e9d140175be)

### **Login Process:**
- **Operator Login:** Operators log in using their **username** and **password** stored in Firestore.
- **Polling Station Assignment:** After a successful login, the operator is assigned to a polling station.
  
### **Steganography-Based Voter Verification:**
- Once logged in, the operator can use the **Steganography Scanner** to analyze an **image of a QR code**.
- **Data Decryption & Validation:** The app extracts and decrypts the voter data using AES & RSA encryption.
- **Biometric Verification:** The system uses **fingerprint & retina scans** to confirm the voter's identity.
- **Instant Voter Status Update:** The app instantly marks the voter as **"Voted"** in Firestore.

### **Voice Command Integration:**
- **Scan Image:** Trigger scanning using a voice command.
- **Exit:** Exit the application by saying "Exit".

---

![image](https://github.com/user-attachments/assets/023024b5-b9a9-4857-ae2b-2739df03bdc5)

## **Customizations & Future Improvements** 💡

While the current version supports multiple languages, we welcome contributions to expand translation support.

In the future, **AI-powered fraud detection** and **Gemini-based intelligent assistance** can be integrated for even more security enhancements.

---

## **Contributing** 👨‍💻👩‍💻

We welcome contributions! If you'd like to contribute to the project, here’s how:

1. Fork the repo.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add some feature'`).
5. Push to the branch (`git push origin feature/your-feature`).
6. Create a new Pull Request.

---

## **License** 📜

This project is open-source and available under the [MIT License](LICENSE).

---

## **Contact & Support** 🤝

If you have any questions or need support, feel free to contact us via [Email/LinkedIn/GitHub Issues]. We’re here to help!

---

## **Demo** 📸

Here's a sneak peek at how **VoteXpress** works:
![Screenshot 2025-03-16 155357](https://github.com/user-attachments/assets/e98bfa3c-e143-4001-9b80-2477f04303d5)

![Screenshot 2025-03-16 235047](https://github.com/user-attachments/assets/2d56f44f-d6f3-406f-a4c0-cf69e0a0dbe2)

*Login Page & Steganography Scanner*

![Screenshot 2025-03-17 000832](https://github.com/user-attachments/assets/d6e88127-4610-4e80-896b-81da1d199e57)

*Voter Verified Successfully*

---

**Join the revolution of smart, efficient, and secure voting processes!** 🚀

---
![image](https://github.com/user-attachments/assets/288b15c3-e8ba-4527-8eb3-2c9c834afb8a)
### **Thank you for using VoteXpress!** 💙


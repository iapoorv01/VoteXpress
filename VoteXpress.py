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
        "login": "Login",
        "username": "Username",
        "password": "Password",
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
        "proceeding_with_status": 'Proceeding with status update.',
        "face_not_matched": 'Face not matched for voter. Please try again.',
        "missing_info": 'Missing information in Voter ID. Please try again.',
        "QR_DATA": 'Scanned Data:',
        "scan_face": 'Scan Face'
    },
    "Hindi": {
        "instruction_text":"""
    1. सरकार द्वारा प्रदान की गई अधिकृत आईडी और पासवर्ड के साथ \n        लॉगिन करें।
    2. पासवर्ड टाइप करने से पहले यह सुनिश्चित करें कि कोई नहीं देख रहा हो।
    3. अपना पासवर्ड किसी के साथ साझा न करें।
    """,
        "title": "पोलिंग बूथ क्यूआर कोड स्कैनर",
        "login": "लॉगिन",
        "username": "उपयोगकर्ता नाम",
        "password": "पासवर्ड",
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
        "missing_info": "वोटर आईडी में कुछ जानकारी गायब है। कृपया फिर से प्रयास करें।",
        "QR_DATA": "स्कैन किया गया डेटा:",
        "scan_face": "चेहरा स्कैन करें"
    },
    "Bengali": {
        "instruction_text": """
    1. সরকার কর্তৃক প্রদত্ত অনুমোদিত আইডি এবং পাসওয়ার্ড দিয়ে লগইন করুন।
    2. পাসওয়ার্ড টাইপ করার আগে নিশ্চিত করুন যে কেউ দেখছে না।
    3. আপনার পাসওয়ার্ড কারও সাথে শেয়ার করবেন না।
    """,
        "title": "পোলিং বুথ কিউআর কোড স্ক্যানার",
        "login": "লগইন",
        "username": "ব্যবহারকারীর নাম",
        "password": "পাসওয়ার্ড",
        "login_button": "লগইন",
        "scan_button": "স্ক্যান শুরু করুন",
        "exit_button": "বের হয়ে যান",
        "scan_qr_instruction": "শুরু করতে একটি কিউআর কোড স্ক্যান করুন",
        "please_login": "দয়া করে লগইন করুন",
        "login_successful": "লগইন সফল! নিয়োগকৃত স্টেশন: {assigned_station}",
        "invalid_password": "অবৈধ পাসওয়ার্ড। আবার চেষ্টা করুন।",
        "operator_not_found": "অপারেটর ডাটাবেসে পাওয়া যায়নি।",
        "command_not_recognized": "কমান্ড চিহ্নিত হয়নি। 'scan qr' বা 'exit' চেষ্টা করুন।",
        "voter_status_not_found": "ভোটার ডাটাবেসে পাওয়া যায়নি।",
        "voter_data_mismatch": "ভোটার তথ্য ডাটাবেসের সাথে মেলে না।",
        "voter_underage": "ভোটার 18 বছরের কম এবং ভোট দিতে পারবে না।",
        "voter_already_voted": "ভোটার ইতিমধ্যেই {station} এ ভোট দিয়েছে।",
        "voter_voted": "ভোটার {name} কে '{station}' এ 'ভোট' হিসাবে চিহ্নিত করা হয়েছে।",
        "face_matching_in_progress": "মুখের মিল অনুসন্ধান চলছে...",
        "face_matched": "ভোটারের মুখ মিলেছে",
        "proceeding_with_status": "স্থিতির আপডেট প্রক্রিয়া চলছে।",
        "face_not_matched": "ভোটারের মুখ মেলেনি। আবার চেষ্টা করুন।",
        "missing_info": "ভোটার আইডিতে তথ্য অনুপস্থিত। আবার চেষ্টা করুন।",
        "QR_DATA": "স্ক্যান করা তথ্য:",
        "scan_face": "মুখ স্ক্যান করুন"
    },
    "Gujarati": {
        "instruction_text": """
    1. સરકાર દ્વારા પ્રદાન કરેલ અધિકૃત ID અને પાસવર્ડ સાથે \n        લૉગિન કરો.
    2. પાસવર્ડ ટાઇપ કરતા પહેલા ખાતરી કરો કે કોઈ જુએ નહિ.
    3. તમારું પાસવર્ડ કોઈ સાથે શેર ન કરો.
    """,
        "title": "પોલિંગ બૂથ ક્યૂઆર કોડ સ્કેનર",
        "login": "લૉગિન",
        "username": "વપરાશકર્તા નામ",
        "password": "પાસવર્ડ",
        "login_button": "લૉગિન",
        "scan_button": "સ્કેનિંગ શરૂ કરો",
        "exit_button": "બહાર નીકળો",
        "scan_qr_instruction": "શરૂ કરવા માટે ક્યૂઆર કોડ સ્કેન કરો",
        "please_login": "કૃપા કરીને લૉગિન કરો",
        "login_successful": "લૉગિન સફળ! નિમણૂક કરવામાં આવેલ સ્ટેશન: {assigned_station}",
        "invalid_password": "અમાન્ય પાસવર્ડ. કૃપા કરી ફરીથી પ્રયાસ કરો.",
        "operator_not_found": "ઑપરેટર ડેટાબેસમાં મળી નથી.",
        "command_not_recognized": "કમાન્ડ ઓળખવામાં આવી નથી. 'scan qr' અથવા 'exit' પ્રયાસ કરો.",
        "voter_status_not_found": "વોટર ડેટાબેસમાં મળી નથી.",
        "voter_data_mismatch": "વોટર ડેટા ડેટાબેસ સાથે મેચ થતું નથી.",
        "voter_underage": "વોટર 18 વર્ષથી નાની ઉંમરની છે અને મતદાન કરી શકતું નથી.",
        "voter_already_voted": "વોટરે પહેલા {station} પર મતદાન કર્યું છે.",
        "voter_voted": "વોટર {name} ને '{station}' પર 'વોટેડ' તરીકે ચિહ્નિત કરવામાં આવ્યું છે.",
        "face_matching_in_progress": "ચહેરો મેળવનાર પ્રક્રિયા ચાલુ છે...",
        "face_matched": "વોટર માટે ચહેરો મેળવે છે",
        "proceeding_with_status": "સ્થિતિ અપડેટ માટે પ્રગતિ કરવામાં આવી રહી છે.",
        "face_not_matched": "વોટર માટે ચહેરો મળતો નથી. કૃપા કરી ફરીથી પ્રયાસ કરો.",
        "missing_info": "વોટર ID માં ગુમ માહિતી. કૃપા કરી ફરીથી પ્રયાસ કરો.",
        "QR_DATA": "સ્કેન કરેલ ડેટા:",
        "scan_face": "ચહેરો સ્કેન કરો"
    },
    "Kannada": {
        "instruction_text": """
    1. ಸರ್ಕಾರದಿಂದ ಒದಗಿಸಿದ ಅನುಮತಿತ ID ಮತ್ತು ಪಾಸ್ವರ್ಡ್ ಬಳಸಿ \n        ಲಾಗಿನ್ ಮಾಡಿ.
    2. ಪಾಸ್ವರ್ಡ್ ಟೈಪ್ ಮಾಡುವ ಮೊದಲು ಯಾರೂ ನೋಡುತ್ತಿರೋದು ಎಂದು ಖಚಿತಪಡಿಸಿಕೊಳ್ಳಿ.
    3. ನಿಮ್ಮ ಪಾಸ್ವರ್ಡ್ ಅನ್ನು ಯಾರೊಂದಿಗೂ ಹಂಚಿಕೊಳ್ಳಬೇಡಿ.
    """,
        "title": "ಪೋಲಿಂಗ್ ಬುತ್ QR ಕೋಡ್ ಸ್ಕ್ಯಾನರ್",
        "login": "ಲಾಗಿನ್",
        "username": "ಬಳಕೆದಾರನ ಹೆಸರು",
        "password": "ಪಾಸ್ವರ್ಡ್",
        "login_button": "ಲಾಗಿನ್ ಮಾಡಿ",
        "scan_button": "ಸ್ಕ್ಯಾನ್ ಮಾಡುವುದು ಪ್ರಾರಂಭಿಸಿ",
        "exit_button": "ನಿರ್ಗಮಿಸಿ",
        "scan_qr_instruction": "ಪ್ರಾರಂಭಿಸಲು QR ಕೋಡ್ ಅನ್ನು ಸ್ಕ್ಯಾನ್ ಮಾಡಿ",
        "please_login": "ದಯವಿಟ್ಟು ಲಾಗಿನ್ ಮಾಡಿ",
        "login_successful": "ಲಾಗಿನ್ ಯಶಸ್ವಿ! ನಿಯೋಜಿಸಲಾಗಿದೆ {assigned_station}.",
        "invalid_password": "ಅಮಾನ್ಯ ಪಾಸ್ವರ್ಡ್. ದಯವಿಟ್ಟು ಪುನಃ ಪ್ರಯತ್ನಿಸಿ.",
        "operator_not_found": "ಆಪರೇಟರ್ ಡೇಟಾಬೇಸ್ನಲ್ಲಿ ಕಂಡುಬಂದಿಲ್ಲ.",
        "command_not_recognized": "ಕಮಾಂಡ್ ಗುರುತಿಸಲಾಗಲಿಲ್ಲ. 'scan qr' ಅಥವಾ 'exit' ಪ್ರಯತ್ನಿಸಿ.",
        "voter_status_not_found": "ಮತದಾರರ ಸ್ಥಿತಿಯನ್ನು ಡೇಟಾಬೇಸ್ನಲ್ಲಿ ಕಂಡುಬಂದಿಲ್ಲ.",
        "voter_data_mismatch": "ಮತದಾರರ ಡೇಟಾ ಡೇಟಾಬೇಸ್ನೊಂದಿಗೆ ಹೊಂದಿಕೊಳ್ಳುತ್ತಿಲ್ಲ.",
        "voter_underage": "ಮತದಾರರು 18 ವರ್ಷದ ಅಡಿಯಲ್ಲಿ ಇದ್ದಾರೆ ಮತ್ತು ಮತದಾನ ಮಾಡಲಾಗುವುದಿಲ್ಲ.",
        "voter_already_voted": "ಮತದಾರರು ಈಗಾಗಲೇ {station} ನಲ್ಲಿ ಮತದಾನ ಮಾಡಿದ್ದಾರೆ.",
        "voter_voted": "ಮತದಾರ {name} ಅನ್ನು '{station}' ನಲ್ಲಿ 'ವೋಟ್' ಎಂದು ಗುರುತಿಸಲಾಗಿದೆ.",
        "face_matching_in_progress": "ಮುಖದ ಹೋಲಿಕೆಯನ್ನು ಪ್ರಗತಿಸುತ್ತಿದೆ...",
        "face_matched": "ಮತದಾರರ ಮುಖ ಹೊಂದಿದೆ",
        "proceeding_with_status": "ಸ್ಥಿತಿಯನ್ನು ನವೀಕರಣ ಪ್ರಕ್ರಿಯೆ ಮುಂದುವರಿಯುತ್ತಿದೆ.",
        "face_not_matched": "ಮತದಾರರ ಮುಖ ಹೊಂದಿಲ್ಲ. ದಯವಿಟ್ಟು ಪುನಃ ಪ್ರಯತ್ನಿಸಿ.",
        "missing_info": "ಮತದಾರರ ಐಡಿಯಲ್ಲಿ ಗಾಬಲಾದ ಮಾಹಿತಿ ಇಲ್ಲ. ದಯವಿಟ್ಟು ಪುನಃ ಪ್ರಯತ್ನಿಸಿ.",
        "QR_DATA": "ಸ್ಕ್ಯಾನ್ ಮಾಡಿದ ಮಾಹಿತಿ:",
        "scan_face": "ಮುಖವನ್ನು ಸ್ಕ್ಯಾನ್ ಮಾಡಿ"
    },
    "Kashmiri": {
        "instruction_text": """
        1. حکومت طرف چھ فراہم کراہ آئی ڈی اتھ پاسورڈ سن لاگن کرن۔
        2. پاسورڈ ٹائپ کرن تھ پیہلاں ایہہ دھیان رکھو چھ کوئی نہ دیکھ رہا ہو۔
        3. اپنا پاسورڈ کسے نال شیئر نہ کرن۔
        """,
        "title": "پولنگ بوتھ QR کوڈ سکینر",
        "login": "لاگن",
        "username": "استعمال کنندہ کا نام:",
        "password": "پاسورڈ:",
        "login_button": "لاگن کرن",
        "scan_button": "سکیننگ شروع کرن",
        "exit_button": "باہر نکلن",
        "scan_qr_instruction": "آرگمنٹ کرن چھ QR کوڈ سکین کرن",
        "please_login": "براہ کرم لاگن کرن",
        "login_successful": "لاگن کامیاب! تفویض کردہ اسٹیشن: {assigned_station}",
        "invalid_password": "غلط پاسورڈ۔ براہ کرم دوبارہ کوشش کرن۔",
        "operator_not_found": "آپریٹر ڈیٹا بیس وچ ناں ملن۔",
        "command_not_recognized": "کمانڈ پہچانی ناں گئی۔ 'scan qr' یا 'exit' آزمانے چھ کوشش کرن۔",
        "voter_status_not_found": "ووٹر ڈیٹا بیس وچ ناں ملن۔",
        "voter_data_mismatch": "ووٹر کا ڈیٹا ڈیٹا بیس نال میل ناں کھاندے۔",
        "voter_underage": "ووٹر 18 سال توں کٹ چھ اور ووٹ ناں ڈال سگھن۔",
        "voter_already_voted": "ووٹر نے پہلے ہی {station} تے ووٹ ڈال دِتھ اے۔",
        "voter_voted": "ووٹر {name} کو '{station}' تے 'ووٹ' کے طور پر نشان زد کیا گیا ہے۔",
        "face_matching_in_progress": "چہرہ میلانے کا عمل جاری ہے...",
        "face_matched": "ووٹر کا چہرہ میل کھا گیا",
        "proceeding_with_status": "اسٹیٹس اپڈیٹ کا عمل جاری ہے۔",
        "face_not_matched": "ووٹر کا چہرہ میل ناں کھاندے۔ براہ کرم دوبارہ کوشش کرن۔",
        "missing_info": "ووٹر آئی ڈی وچ کچھ معلومات غائب ہیں۔ براہ کرم دوبارہ کوشش کرن۔",
        "QR_DATA": "اسکین کیا گیا ڈیٹا:",
        "scan_face": "چہرہ سکین کرن"
    },

    "Konkani": {
        "instruction_text": """
    1. सरकाराकडून दिलेल्या अधिकृत आयडी आणि पासवर्डसह \n        लॉगिन करा.
    2. पासवर्ड टाइप करण्यापूर्वी खात्री करा की कोणीही पाहत नाही.
    3. तुमचा पासवर्ड कोणाशीही शेअर करू नका.
    """,
        "title": "पोलिंग बूथ QR कोड स्कॅनर",
        "login": "लॉगिन",
        "username": "वापरकर्ता नाव",
        "password": "पासवर्ड",
        "login_button": "लॉगिन करा",
        "scan_button": "स्कॅनिंग सुरू करा",
        "exit_button": "बाहेर जा",
        "scan_qr_instruction": "शुरू करण्यासाठी एक QR कोड स्कॅन करा",
        "please_login": "कृपया लॉगिन करा",
        "login_successful": "लॉगिन यशस्वी! दिलेल्या स्टेशनला नियुक्त केले आहे: {assigned_station}",
        "invalid_password": "अवैध पासवर्ड. कृपया पुन्हा प्रयत्न करा.",
        "operator_not_found": "ऑपरेटर डेटाबेसमध्ये सापडले नाही.",
        "command_not_recognized": "आज्ञा ओळखली गेली नाही. 'scan qr' किंवा 'exit' प्रयत्न करा.",
        "voter_status_not_found": "मतदार डेटाबेसमध्ये सापडले नाही.",
        "voter_data_mismatch": "मतदाराचा डेटा डेटाबेसशी जुळत नाही.",
        "voter_underage": "मतदार 18 वर्षांपेक्षा कमी वयाचा आहे आणि मतदान करू शकत नाही.",
        "voter_already_voted": "मतदाराने आधीच {station} मध्ये मतदान केले आहे.",
        "voter_voted": "मतदार {name} ला '{station}' मध्ये 'मतदान' म्हणून चिन्हित केले आहे.",
        "face_matching_in_progress": "चेहरा जुळवण्याची प्रक्रिया सुरू आहे...",
        "face_matched": "मतदारासाठी चेहरा जुळला आहे",
        "proceeding_with_status": "स्थिती अद्ययावत करण्याची प्रक्रिया सुरू आहे.",
        "face_not_matched": "मतदारासाठी चेहरा जुळलेला नाही. कृपया पुन्हा प्रयत्न करा.",
        "missing_info": "मतदार ID मध्ये काही माहिती गहाळ आहे. कृपया पुन्हा प्रयत्न करा.",
        "QR_DATA": "स्कॅन केलेला डेटा:",
        "scan_face": "चेहरा स्कॅन करा"
    },
    "Maithili": {
        "instruction_text": """
    1. सरकार द्वारा प्रदान कएल गेल अधिकृत ID आ पासवर्ड सऽ \n        लॉगिन करू।
    2. पासवर्ड टाइप करबाक पहिने एह बात केँ सुनिश्चित करू जे कोनो देख नहि रहल होइ।
    3. अपन पासवर्ड ककरो संग शेयर नहि करू।
    """,
        "title": "पोलिंग बूथ QR कोड स्कैनर",
        "login": "लॉगिन",
        "username": "प्रयोगकर्ता नाम",
        "password": "पासवर्ड",
        "login_button": "लॉगिन करू",
        "scan_button": "स्कैनिंग प्रारंभ करू",
        "exit_button": "बाहर निकलू",
        "scan_qr_instruction": "प्रारंभ करबाक लेल एक QR कोड स्कैन करू",
        "please_login": "कृपया लॉगिन करू",
        "login_successful": "लॉगिन सफल! सौंपल गेल स्टेशन: {assigned_station}",
        "invalid_password": "अमान्य पासवर्ड। कृपया पुनः प्रयास करू।",
        "operator_not_found": "ऑपरेटर डाटाबेस में नहि भेटल।",
        "command_not_recognized": "आदेश नहि पहिचानल गेल। 'scan qr' या 'exit' प्रयास करू।",
        "voter_status_not_found": "वोटर डाटाबेस में नहि भेटल।",
        "voter_data_mismatch": "वोटर डेटा डाटाबेस सँ मेल नहि खाइत अछि।",
        "voter_underage": "वोटर 18 वर्ष सँ कम आयु कऽ अछि आ मतदान नहि कऽ सकैत अछि।",
        "voter_already_voted": "वोटर पहिने {station} पर मतदान कऽ चुकल अछि।",
        "voter_voted": "वोटर {name} केँ '{station}' पर 'वोट' कऽ रूप में चिन्हित कएल गेल अछि।",
        "face_matching_in_progress": "चेहरा मिलान होइ रहल अछि...",
        "face_matched": "वोटर के लेल चेहरा मेल खाइत अछि",
        "proceeding_with_status": "स्थिति अद्यतन कऽ प्रक्रिया जारी अछि।",
        "face_not_matched": "वोटर के लेल चेहरा मेल नहि खाइत अछि। कृपया पुनः प्रयास करू।",
        "missing_info": "वोटर आईडी में किछु जानकारी गुम अछि। कृपया पुनः प्रयास करू।",
        "QR_DATA": "स्कैन कएल गेल डेटा:",
        "scan_face": "चेहरा स्कैन करू"
    },
    "Malayalam": {
        "instruction_text": """
    1. സർക്കാർ നൽകുന്ന ഔതോറൈസ്ഡ് ID കൂടെ പാസ്‌വേഡ് ഉപയോഗിച്ച് \n        ലോഗിൻ ചെയ്യുക.
    2. പാസ്‌വേഡ് ടൈപ്പ് ചെയ്യുന്നതിന് മുമ്പ് മറ്റാരും കാണുന്നില്ല എന്ന് ഉറപ്പാക്കുക.
    3. നിങ്ങളുടെ പാസ്‌വേഡ് ആരുമായും പങ്കുവെക്കരുത്.
    """,
        "title": "പോലിംഗ് ബൂത്ത് QR കോഡ് സ്കാനർ",
        "login": "ലോഗിൻ",
        "username": "ഉപയോക്തൃനാമം",
        "password": "പാസ്‌വേഡ്",
        "login_button": "ലോഗിൻ ചെയ്യുക",
        "scan_button": "സ്കാനിങ് ആരംഭിക്കുക",
        "exit_button": "പുറത്തേക്ക് പോകുക",
        "scan_qr_instruction": "ആരംഭിക്കാൻ QR കോഡ് സ്കാൻ ചെയ്യുക",
        "please_login": "ദയവായി ലോഗിൻ ചെയ്യുക",
        "login_successful": "ലോഗിൻ വിജയകരമായി! നിയോഗിച്ച സ്റ്റേഷനിലേക്ക്: {assigned_station}",
        "invalid_password": "അവൈധ പാസ്‌വേഡ്. ദയവായി വീണ്ടും ശ്രമിക്കുക.",
        "operator_not_found": "ഓപ്പറേറ്റർ ഡാറ്റാബേസിൽ കണ്ടെത്തിയില്ല.",
        "command_not_recognized": "കമാൻഡ് തിരിച്ചറിയാനായില്ല. 'scan qr' അല്ലെങ്കിൽ 'exit' ശ്രമിക്കുക.",
        "voter_status_not_found": "വോട്ടർ ഡാറ്റാബേസിൽ കണ്ടെത്തിയില്ല.",
        "voter_data_mismatch": "വോട്ടർ ഡാറ്റ ഡാറ്റാബേസുമായിടയിൽ പൊരുത്തപ്പെടുന്നില്ല.",
        "voter_underage": "വോട്ടർ 18 വയസ്സിന് താഴെയുള്ളവർക്കാണ്, അതിനാൽ അവർ വോട്ട് ചെയ്യാൻ കഴിയില്ല.",
        "voter_already_voted": "വോട്ടർ മുമ്പ് {station} ൽ വോട്ട് ചെയ്തിട്ടുണ്ട്.",
        "voter_voted": "വോട്ടർ {name} നെ '{station}' ൽ 'വോട്ട്' ആയി അടയാളപ്പെടുത്തിയിട്ടുണ്ട്.",
        "face_matching_in_progress": "ചേവറു പൊരുത്തപ്പെടുത്തൽ നടക്കുന്നു...",
        "face_matched": "വോട്ടർ മുഖം പൊരുത്തപ്പെട്ടു",
        "proceeding_with_status": "സ്ഥിതിയുടെ അപ്‌ഡേറ്റ് പ്രക്രിയ പുരോഗമിക്കുന്നു.",
        "face_not_matched": "വോട്ടറിന്റെ മുഖം പൊരുത്തപ്പെടുന്നില്ല. ദയവായി വീണ്ടും ശ്രമിക്കുക.",
        "missing_info": "വോട്ടർ ഐഡി missing വിവരങ്ങൾ. ദയവായി വീണ്ടും ശ്രമിക്കുക.",
        "QR_DATA": "സ്കാൻ ചെയ്ത ഡാറ്റ:",
        "scan_face": "മുക്കുകൾ സ്കാൻ ചെയ്യുക"
    },
    "Marathi": {
        "instruction_text": """
    1. सरकाराने प्रदान केलेल्या अधिकृत ID आणि पासवर्डसह \n        लॉगिन करा.
    2. पासवर्ड टाईप करण्यापूर्वी नक्की करा की कोणीही पाहत नाही.
    3. तुमचा पासवर्ड कोणासोबतही शेअर करू नका.
    """,
        "title": "पोलिंग बूथ QR कोड स्कॅनर",
        "login": "लॉगिन",
        "username": "वापरकर्ता नाव",
        "password": "पासवर्ड",
        "login_button": "लॉगिन करा",
        "scan_button": "स्कॅनिंग प्रारंभ करा",
        "exit_button": "बाहेर जा",
        "scan_qr_instruction": "प्रारंभ करण्यासाठी QR कोड स्कॅन करा",
        "please_login": "कृपया लॉगिन करा",
        "login_successful": "लॉगिन यशस्वी! नियुक्त केलेले स्टेशन: {assigned_station}",
        "invalid_password": "अवैध पासवर्ड. कृपया पुन्हा प्रयत्न करा.",
        "operator_not_found": "ऑपरेटर डेटाबेसमध्ये सापडले नाही.",
        "command_not_recognized": "आज्ञा ओळखली गेली नाही. 'scan qr' किंवा 'exit' प्रयत्न करा.",
        "voter_status_not_found": "मतदार डेटाबेसमध्ये सापडले नाही.",
        "voter_data_mismatch": "मतदाराचा डेटा डेटाबेससह जुळत नाही.",
        "voter_underage": "मतदार 18 वर्षांपेक्षा कमी वयाचा आहे आणि मतदान करू शकत नाही.",
        "voter_already_voted": "मतदाराने आधीच {station} मध्ये मतदान केले आहे.",
        "voter_voted": "मतदार {name} ला '{station}' मध्ये 'वोट' म्हणून चिन्हित केले आहे.",
        "face_matching_in_progress": "चेहरा जुळवण्याची प्रक्रिया सुरू आहे...",
        "face_matched": "मतदाराचा चेहरा जुळला आहे",
        "proceeding_with_status": "स्थिती अद्ययावत करण्याची प्रक्रिया सुरू आहे.",
        "face_not_matched": "मतदाराचा चेहरा जुळलेला नाही. कृपया पुन्हा प्रयत्न करा.",
        "missing_info": "मतदार ID मध्ये काही माहिती गहाळ आहे. कृपया पुन्हा प्रयत्न करा.",
        "QR_DATA": "स्कॅन केलेला डेटा:",
        "scan_face": "चेहरा स्कॅन करा"
    },
    "Nepali": {
        "instruction_text": """
    1. सरकारद्वारा प्रदान गरिएको अधिकृत ID र पासवर्डसाथ \n        लगइन गर्नुहोस्।
    2. पासवर्ड टाइप गर्नु अघि कुनैले पनि हेरिरहेको छैन भने सुनिश्चित गर्नुहोस्।
    3. तपाईंको पासवर्ड अरूसँग साझा नगर्नुहोस्।
    """,
        "title": "पोलिंग बुथ QR कोड स्क्यानर",
        "login": "लगइन",
        "username": "प्रयोगकर्ता नाम",
        "password": "पासवर्ड",
        "login_button": "लगइन गर्नुहोस्",
        "scan_button": "स्क्यानिंग सुरु गर्नुहोस्",
        "exit_button": "बाहिर जानुहोस्",
        "scan_qr_instruction": "आरम्भ गर्नको लागि QR कोड स्क्यान गर्नुहोस्",
        "please_login": "कृपया लगइन गर्नुहोस्",
        "login_successful": "लगइन सफल! तोकिएको स्टेसन: {assigned_station}",
        "invalid_password": "अमान्य पासवर्ड। कृपया पुनः प्रयास गर्नुहोस्।",
        "operator_not_found": "ऑपरेटर डेटाबेसमा भेटिएन।",
        "command_not_recognized": "कमाण्ड पहिचान भएन। 'scan qr' वा 'exit' प्रयास गर्नुहोस्।",
        "voter_status_not_found": "वोटर डेटाबेसमा भेटिएन।",
        "voter_data_mismatch": "वोटरको डाटा डेटाबेससँग मेल खाँदैन।",
        "voter_underage": "वोटर 18 वर्षभन्दा तलको उमेरको छ र मतदान गर्न सक्दैन।",
        "voter_already_voted": "वोटरले पहिले नै {station} मा मतदान गरिसकेको छ।",
        "voter_voted": "वोटर {name} लाई '{station}' मा 'वोट' को रूपमा चिन्हित गरियो।",
        "face_matching_in_progress": "चाहेरा मिलाउने प्रक्रिया जारी छ...",
        "face_matched": "वोटरको लागि चाहेरा मिल्यो",
        "proceeding_with_status": "स्थिति अपडेट गर्नको लागि प्रक्रिया जारी छ।",
        "face_not_matched": "वोटरको लागि चाहेरा मिलेन। कृपया पुनः प्रयास गर्नुहोस्।",
        "missing_info": "वोटर ID मा केही जानकारी हराएको छ। कृपया पुनः प्रयास गर्नुहोस्।",
        "QR_DATA": "स्क्यान गरिएका डेटा:",
        "scan_face": "चाहेरा स्क्यान गर्नुहोस्"
    },
    "Punjabi": {
        "instruction_text": """
    1. ਸਰਕਾਰ ਵੱਲੋਂ ਦਿੱਤੀ ਹੋਈ ਅਧਿਕਾਰਤ ID ਅਤੇ ਪਾਸਵਰਡ ਨਾਲ \n        ਲੌਗਿਨ ਕਰੋ।
    2. ਪਾਸਵਰਡ ਟਾਈਪ ਕਰਨ ਤੋਂ ਪਹਿਲਾਂ ਇਹ ਯਕੀਨੀ ਬਣਾਓ ਕਿ ਕੋਈ ਨਹੀਂ ਦੇਖ ਰਿਹਾ।
    3. ਆਪਣਾ ਪਾਸਵਰਡ ਕਿਸੇ ਨਾਲ ਸਾਂਝਾ ਨਾ ਕਰੋ।
    """,
        "title": "ਪੋਲਿੰਗ ਬੂਥ QR ਕੋਡ ਸਕੈਨਰ",
        "login": "ਲੌਗਿਨ",
        "username": "ਉਪਭੋਗਤਾ ਦਾ ਨਾਮ",
        "password": "ਪਾਸਵਰਡ",
        "login_button": "ਲੌਗਿਨ ਕਰੋ",
        "scan_button": "ਸਕੈਨਿੰਗ ਸ਼ੁਰੂ ਕਰੋ",
        "exit_button": "ਬਾਹਰ ਨਿਕਲੋ",
        "scan_qr_instruction": "ਸ਼ੁਰੂ ਕਰਨ ਲਈ QR ਕੋਡ ਸਕੈਨ ਕਰੋ",
        "please_login": "ਕਿਰਪਾ ਕਰਕੇ ਲੌਗਿਨ ਕਰੋ",
        "login_successful": "ਲੌਗਿਨ ਸਫਲ! ਨਿਯੁਕਤ ਕੀਤਾ ਗਿਆ ਸਟੇਸ਼ਨ: {assigned_station}",
        "invalid_password": "ਗਲਤ ਪਾਸਵਰਡ। ਕਿਰਪਾ ਕਰਕੇ ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ।",
        "operator_not_found": "ਓਪਰੇਟਰ ਡੇਟਾਬੇਸ ਵਿੱਚ ਨਹੀਂ ਮਿਲਿਆ।",
        "command_not_recognized": "ਕਮਾਂਡ ਪਛਾਣੀ ਨਹੀਂ ਗਈ। 'scan qr' ਜਾਂ 'exit' ਕੋਸ਼ਿਸ਼ ਕਰੋ।",
        "voter_status_not_found": "ਵੋਟਰ ਡੇਟਾਬੇਸ ਵਿੱਚ ਨਹੀਂ ਮਿਲਿਆ।",
        "voter_data_mismatch": "ਵੋਟਰ ਦਾ ਡੇਟਾ ਡੇਟਾਬੇਸ ਨਾਲ ਮੇਲ ਨਹੀਂ ਖਾਂਦਾ।",
        "voter_underage": "ਵੋਟਰ 18 ਸਾਲ ਤੋਂ ਘੱਟ ਉਮਰ ਦਾ ਹੈ ਅਤੇ ਵੋਟ ਨਹੀਂ ਕਰ ਸਕਦਾ।",
        "voter_already_voted": "ਵੋਟਰ ਨੇ ਪਹਿਲਾਂ ਹੀ {station} ਤੇ ਵੋਟ ਕਰ ਦਿੱਤੀ ਹੈ।",
        "voter_voted": "ਵੋਟਰ {name} ਨੂੰ '{station}' ਤੇ 'ਵੋਟ' ਦੇ ਤੌਰ 'ਤੇ ਨਿਸ਼ਾਨਿਤ ਕੀਤਾ ਗਿਆ ਹੈ।",
        "face_matching_in_progress": "ਚਿਹਰਾ ਮਿਲਾਉਣ ਦੀ ਪ੍ਰਕਿਰਿਆ ਚੱਲ ਰਹੀ ਹੈ...",
        "face_matched": "ਵੋਟਰ ਲਈ ਚਿਹਰਾ ਮਿਲ ਗਿਆ ਹੈ",
        "proceeding_with_status": "ਸਟੇਟਸ ਅਪਡੇਟ ਕਰਨ ਦੀ ਪ੍ਰਕਿਰਿਆ ਜਾਰੀ ਹੈ।",
        "face_not_matched": "ਵੋਟਰ ਲਈ ਚਿਹਰਾ ਨਹੀਂ ਮਿਲਦਾ। ਕਿਰਪਾ ਕਰਕੇ ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ।",
        "missing_info": "ਵੋਟਰ ID ਵਿੱਚ ਕੁਝ ਜਾਣਕਾਰੀ ਗੁੰਮ ਹੈ। ਕਿਰਪਾ ਕਰਕੇ ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ।",
        "QR_DATA": "ਸਕੈਨ ਕੀਤਾ ਗਿਆ ਡੇਟਾ:",
        "scan_face": "ਚਿਹਰਾ ਸਕੈਨ ਕਰੋ"
    },

    "Tamil": {
        "instruction_text": """
    1. அரசாங்கம் வழங்கிய அனுமதிப்பட்ட ID மற்றும் கடவுச்சொல் மூலம் \n        உள்நுழையவும்.
    2. கடவுச்சொல்லை வகுத்த பிறகு யாரும் பார்க்கவில்லை என்பதை உறுதி செய்யவும்.
    3. உங்கள் கடவுச்சொல்லை வேறெவருடனும் பகிர்ந்துக்கொள்ளாதீர்கள்.
    """,
        "title": "போலிங் பூத் QR கோட் ஸ்கேனர்",
        "login": "உள்நுழையவும்",
        "username": "பயனரின் பெயர்",
        "password": "கடவுச்சொல்",
        "login_button": "உள்நுழையவும்",
        "scan_button": "ஸ்கேன் செய்ய தொடங்கவும்",
        "exit_button": "வெளியேறு",
        "scan_qr_instruction": "ஆரம்பிக்க QR கோட் ஸ்கேன் செய்யவும்",
        "please_login": "உள்நுழையவும்",
        "login_successful": "உள்நுழைவு வெற்றிகரமானது! நியமிக்கப்பட்ட நிலையம்: {assigned_station}",
        "invalid_password": "தவறான கடவுச்சொல். மீண்டும் முயற்சிக்கவும்.",
        "operator_not_found": "ஆபரேட்டர் தரவுத்தளத்தில் கிடைத்தது இல்லை.",
        "command_not_recognized": "கமாண்டு கண்டறியப்படவில்லை. 'scan qr' அல்லது 'exit' முயற்சிக்கவும்.",
        "voter_status_not_found": "வோட்டர் தரவுத்தளத்தில் கிடைத்தது இல்லை.",
        "voter_data_mismatch": "வோட்டர் தரவு தரவுத்தளத்துடன் பொருந்தவில்லை.",
        "voter_underage": "வோட்டர் 18 வயதிற்கு கீழானவர் மற்றும் வாக்களிக்க முடியாது.",
        "voter_already_voted": "வோட்டர் ஏற்கனவே {station} இல் வாக்களித்துள்ளார்.",
        "voter_voted": "வோட்டர் {name} '{station}' இல் 'வாக்களித்தார்' என குறியிடப்பட்டது.",
        "face_matching_in_progress": "முகம் பொருத்தப்படுவது நடைபெறுகிறது...",
        "face_matched": "வோட்டருக்கான முகம் பொருத்தப்பட்டது",
        "proceeding_with_status": "நிலை புதுப்பிப்பது நடைபெற்று வருகிறது.",
        "face_not_matched": "வோட்டருக்கான முகம் பொருத்தப்படவில்லை. மீண்டும் முயற்சிக்கவும்.",
        "missing_info": "வோட்டர் ஐடியின் தகவல் தவறியது. மீண்டும் முயற்சிக்கவும்.",
        "QR_DATA": "ஸ்கேன் செய்யப்பட்ட தரவு:",
        "scan_face": "முகம் ஸ்கேன் செய்யவும்"
    },
    "Telugu": {
        "instruction_text": """
    1. ప్రభుత్వము అందించిన అధికారిక ID మరియు పాస్వర్డుతో \n        లాగిన్ చేయండి.
    2. పాస్వర్డును టైప్ చేయడమునకు ముందు ఎవరో చూస్తున్నారని నిర్ధారించుకోండి.
    3. మీ పాస్వర్డును ఎవరితోనైనా పంచుకోకండి.
    """,
        "title": "పోలింగ్ బూత్ QR కోడ్ స్కానర్",
        "login": "లాగిన్",
        "username": "ఉపయోగదారుడి పేరు",
        "password": "పాస్వర్డ్",
        "login_button": "లాగిన్ చేయండి",
        "scan_button": "స్కానింగ్ ప్రారంభించండి",
        "exit_button": "ఎవిక్ట్",
        "scan_qr_instruction": "ప్రారంభించడానికి QR కోడ్ స్కాన్ చేయండి",
        "please_login": "దయచేసి లాగిన్ చేయండి",
        "login_successful": "లాగిన్ విజయవంతం! అప్పగించిన స్టేషన్: {assigned_station}",
        "invalid_password": "చెల్లని పాస్వర్డ్. దయచేసి మళ్ళీ ప్రయత్నించండి.",
        "operator_not_found": "ఆపరేటర్ డేటాబేస్‌లో కనుగొనబడలేదు.",
        "command_not_recognized": "కమాండ్ గుర్తించబడలేదు. 'scan qr' లేదా 'exit' ప్రయత్నించండి.",
        "voter_status_not_found": "వోటర్ డేటాబేస్‌లో కనుగొనబడలేదు.",
        "voter_data_mismatch": "వోటర్ డేటా డేటాబేసుతో సరిగ్గా సరిపోవట్లేదు.",
        "voter_underage": "వోటర్ 18 సంవత్సరాల కన్నా తక్కువ వయస్సు ఉన్నారు మరియు ఓటు వేసే అవకాశం లేదు.",
        "voter_already_voted": "వోటర్ {station} లో ఇప్పటికే ఓటు వేసారు.",
        "voter_voted": "వోటర్ {name} ను '{station}' లో 'వోటు' గా గుర్తించారు.",
        "face_matching_in_progress": "ముఖం సరిపోవడం జరుగుతోంది...",
        "face_matched": "వోటర్ ముఖం సరిపొయింది",
        "proceeding_with_status": "స్థితి నవీకరణలో కొనసాగుతోంది.",
        "face_not_matched": "వోటర్ ముఖం సరిపోలలేదు. దయచేసి మళ్ళీ ప్రయత్నించండి.",
        "missing_info": "వోటర్ ఐడీలో కొంత సమాచారం లేని వంటిది. దయచేసి మళ్ళీ ప్రయత్నించండి.",
        "QR_DATA": "స్కాన్ చేసిన డేటా:",
        "scan_face": "ముఖం స్కాన్ చేయండి"
    },
    "Urdu": {
        "instruction_text": """
    1. حکومت کی طرف سے فراہم کردہ منظور شدہ ID اور پاس ورڈ کے ساتھ \n        لاگ ان کریں۔
    2. پاس ورڈ ٹائپ کرنے سے پہلے اس بات کا یقین کر لیں کہ کوئی نہیں دیکھ رہا۔
    3. اپنا پاس ورڈ کسی کے ساتھ شیئر نہ کریں۔
    """,
        "title": "پولنگ بوتھ QR کوڈ اسکینر",
        "login": "لاگ ان",
        "username": "صارف کا نام:",
        "password": "پاس ورڈ:",
        "login_button": "لاگ ان کریں",
        "scan_button": "اسکیننگ شروع کریں",
        "exit_button": "باہر جائیں",
        "scan_qr_instruction": "شروع کرنے کے لئے QR کوڈ اسکین کریں",
        "please_login": "براہ کرم لاگ ان کریں",
        "login_successful": "لاگ ان کامیاب! تفویض شدہ اسٹیشن: {assigned_station}",
        "invalid_password": "غلط پاس ورڈ۔ براہ کرم دوبارہ کوشش کریں۔",
        "operator_not_found": "آپریٹر ڈیٹا بیس میں نہیں ملا۔",
        "command_not_recognized": "کمانڈ کی شناخت نہیں کی گئی۔ 'scan qr' یا 'exit' کوشش کریں۔",
        "voter_status_not_found": "ووٹر ڈیٹا بیس میں نہیں ملا۔",
        "voter_data_mismatch": "ووٹر کا ڈیٹا ڈیٹا بیس سے میل نہیں کھاتا۔",
        "voter_underage": "ووٹر کی عمر 18 سال سے کم ہے اور ووٹ نہیں دے سکتا۔",
        "voter_already_voted": "ووٹر نے پہلے ہی {station} پر ووٹ دے دیا ہے۔",
        "voter_voted": "ووٹر {name} کو '{station}' پر 'ووٹ' کے طور پر نشان زد کیا گیا ہے۔",
        "face_matching_in_progress": "چہرے کا میچ کیا جا رہا ہے...",
        "face_matched": "ووٹر کے لیے چہرہ میل کھاتا ہے",
        "proceeding_with_status": "حیثیت کی تازہ کاری کی کارروائی جاری ہے۔",
        "face_not_matched": "ووٹر کا چہرہ میل نہیں کھاتا۔ براہ کرم دوبارہ کوشش کریں۔",
        "missing_info": "ووٹر کی ID میں کچھ معلومات غائب ہیں۔ براہ کرم دوبارہ کوشش کریں۔",
        "QR_DATA": "اسکین شدہ ڈیٹا:",
        "scan_face": "چہرہ اسکین کریں"
    },
    "Sanskrit": {
            "instruction_text": """
        1. सरकारद्वारा प्रदत्तं अधिकृतं ID च पासवर्डं सह \n        लॉगिनं कुरुत।
        2. पासवर्डं लिखनं पूर्वं, यः कश्चन न दृश्यते तदर्थं सुनिश्चितं कुरुत।
        3. स्वं पासवर्डं कस्यापि सह न साझा कुरुत।
        """,
            "title": "मतदान बूथ QR कोड स्कैनर",
            "login": "लॉगिनं कुरुत",
            "username": "उपयोगकर्तृ नाम",
            "password": "पासवर्ड",
            "login_button": "लॉगिनं कुरुत",
            "scan_button": "स्कैनिंगं आरभताम्",
            "exit_button": "निर्गच्छतु",
            "scan_qr_instruction": "प्रारम्भं कर्तुम् QR कोडं स्कैन कुरुत",
            "please_login": "कृपया लॉगिनं कुरुत",
            "login_successful": "लॉगिनं सफलं! निर्दिष्टं स्टेशनम्: {assigned_station}",
            "invalid_password": "अमान्यं पासवर्डं। कृपया पुनः प्रयासं कुरुत।",
            "operator_not_found": "ऑपरेटर् डेटाबेसे न प्राप्तम्।",
            "command_not_recognized": "आदेशः न ज्ञायते। 'scan qr' अथवा 'exit' प्रयताम्।",
            "voter_status_not_found": "वोटर् डेटाबेसे न प्राप्तम्।",
            "voter_data_mismatch": "वोटर् डाटा डेटाबेसे मिलितं नास्ति।",
            "voter_underage": "वोटर् अठार वर्षेण अल्पः अस्ति, अतः मतदानं न कर्तुम् शक्नोति।",
            "voter_already_voted": "वोटर् पूर्वं {station} मध्ये मतदानं कृतम्।",
            "voter_voted": "वोटर् {name} 'वोट' इति '{station}' मध्ये चिह्नितम्।",
            "face_matching_in_progress": "मुखस्य मिलानं प्रगच्छति...",
            "face_matched": "वोटर् मुखं मेलितम्",
            "proceeding_with_status": "स्थिति अद्यतनं कर्तुं प्रगच्छति।",
            "face_not_matched": "वोटर् मुखं मेलितं नास्ति। कृपया पुनः प्रयासं कुरुत।",
            "missing_info": "वोटर् ID मध्ये किञ्चित् सूचना अनुपस्थितं अस्ति। कृपया पुनः प्रयासं कुरुत।",
            "QR_DATA": "स्कैनितं डेटा:",
            "scan_face": "मुखं स्कैन कुरुत"
        },
        "Bodo": {
            "instruction_text": """
        1. सरकार द्वारा प्रदत्त अधिकृत ID आनि पासवर्ड सँग \n        लॉगिन करा।
        2. पासवर्ड टाइप कराबर लागा, आरो सम्जन करा बोर नाकां देखाव खोनार ना होब।
        3. थुमार पासवर्ड केनायो लुकंनाय सँग न सियाबा।
        """,
            "title": "पोलिंग बूथ QR कोड स्कैनर",
            "login": "लॉगिन",
            "username": "उपयोगकर्ता नाम",
            "password": "पासवर्ड",
            "login_button": "लॉगिन करा",
            "scan_button": "स्कैनिंग सुरु करा",
            "exit_button": "बाहर जाओ",
            "scan_qr_instruction": "शुरू करबा बर QR कोड स्कैन करा",
            "please_login": "कृपया लॉगिन करा",
            "login_successful": "लॉगिन सफल! निर्दिष्ट स्टेशन: {assigned_station}",
            "invalid_password": "अमान्य पासवर्ड। कृपया पुनः प्रयास करा।",
            "operator_not_found": "ऑपरेटर डेटाबेस मं नहीं मिलाया गयो।",
            "command_not_recognized": "आदेश पहिचान नइ सकत। 'scan qr' या 'exit' आजमाय करा।",
            "voter_status_not_found": "वोटर डेटाबेस मं नहीं मिलाया गयो।",
            "voter_data_mismatch": "वोटर डेटा डेटाबेस सँग मेल नहीं खा रहे।",
            "voter_underage": "वोटर 18 बर्स साय रोंग होब आनि वोट न पाब।",
            "voter_already_voted": "वोटर पहले ही {station} मं वोट कर चुका है।",
            "voter_voted": "वोटर {name} ला '{station}' मं 'वोट' चिह्नित करा गया।",
            "face_matching_in_progress": "मुख मिलाउने प्रक्रिया चलि रिया है...",
            "face_matched": "वोटर के मुख मिलाए गए",
            "proceeding_with_status": "स्थिति अद्यतन प्रक्रिया चलि रिया है।",
            "face_not_matched": "वोटर के मुख मेल ना खा रहल। कृपया पुनः प्रयास करा।",
            "missing_info": "वोटर ID मं किछु जानकारी गुम है। कृपया पुनः प्रयास करा।",
            "QR_DATA": "स्कैन कियागा डेटा:",
            "scan_face": "मुख स्कैन करा"
        },
    "Santhali": {
        "instruction_text": """
    1. सरकार द्वारा प्रदत्त अधिकृत ID आनि पासवर्ड सँग \n        लॉगिन करा।
    2. पासवर्ड टाइप करेबा से पहला, एने हेंस के कियो नाय देख रहल हो।
    3. थुमार पासवर्ड कियो संग सियार न करी।
    """,
        "title": "पोलिंग बूथ QR कोड स्कैनर",
        "login": "लॉगिन",
        "username": "उपयोगकर्ता नाम",
        "password": "पासवर्ड",
        "login_button": "लॉगिन करा",
        "scan_button": "स्कैनिंग सुरू करा",
        "exit_button": "बाहर जाव",
        "scan_qr_instruction": "आरंभ करबा बर QR कोड स्कैन करा",
        "please_login": "कृपया लॉगिन करा",
        "login_successful": "लॉगिन सफल! निर्दिष्ट स्टेशन: {assigned_station}",
        "invalid_password": "अमान्य पासवर्ड। कृपया पुनः प्रयास करा।",
        "operator_not_found": "ऑपरेटर डेटाबेस मं नहीं मिलाया गयो।",
        "command_not_recognized": "आदेश पहिचान नइ सकत। 'scan qr' या 'exit' आजमाय करा।",
        "voter_status_not_found": "वोटर डेटाबेस मं नहीं मिलाया गयो।",
        "voter_data_mismatch": "वोटर डेटा डेटाबेस सँग मेल नहीं खा रहे।",
        "voter_underage": "वोटर 18 बर्स साय रोंग होब आनि वोट न पाब।",
        "voter_already_voted": "वोटर पहिले {station} मं वोट कर चुकल हां।",
        "voter_voted": "वोटर {name} ला '{station}' मं 'वोट' चिह्नित करल गे।",
        "face_matching_in_progress": "मुख मिलाए जा रहल हे...",
        "face_matched": "वोटर के मुख मिलाल गे",
        "proceeding_with_status": "स्थिति अद्यतन होब कर रहल हे।",
        "face_not_matched": "वोटर के मुख मेल नइ खा रहल हे। कृपया पुनः प्रयास करा।",
        "missing_info": "वोटर ID मं किछु जानकारी गुम हां। कृपया पुनः प्रयास करा।",
        "QR_DATA": "स्कैन कियागा डेटा:",
        "scan_face": "मुख स्कैन करा"
    },
        "Dogri": {
            "instruction_text": """
        1. सरकार द्वारा प्रदत्त अधिकृत ID आं पासवर्ड नाल \n        लॉगिन करो।
        2. पासवर्ड टाइप करण तो पहलां ऐ सुनिश्चित करो कि कोई नहीं देख रिया होवे।
        3. अपना पासवर्ड किसे नाल वी साझा ना करो।
        """,
            "title": "पोलिंग बूथ QR कोड स्कैनर",
            "login": "लॉगिन",
            "username": "उपयोगकर्ता नाम",
            "password": "पासवर्ड",
            "login_button": "लॉगिन करो",
            "scan_button": "स्कैनिंग शरू करो",
            "exit_button": "बाहर निकलो",
            "scan_qr_instruction": "शरू करन लई QR कोड स्कैन करो",
            "please_login": "कृपया लॉगिन करो",
            "login_successful": "लॉगिन सफल! निर्दिष्ट स्टेशन: {assigned_station}",
            "invalid_password": "अमान्य पासवर्ड। कृपया पुनः प्रयास करो।",
            "operator_not_found": "ऑपरेटर डेटाबेस विच नहीं मिलया।",
            "command_not_recognized": "आदेश पहचान विच नहीं आया। 'scan qr' या 'exit' आजमाओ।",
            "voter_status_not_found": "वोटर डेटाबेस विच नहीं मिलया।",
            "voter_data_mismatch": "वोटर डेटा डेटाबेस नाल मेल नहीं खा रिया।",
            "voter_underage": "वोटर 18 साल तो कम है अते वोट नहीं कर सकदा।",
            "voter_already_voted": "वोटर ने पहले ही {station} ते वोट कीता है।",
            "voter_voted": "वोटर {name} नू '{station}' ते 'वोट' दे तौर ते चिह्नित कीता गया है।",
            "face_matching_in_progress": "चेहरे दा मिलान हो रिया है...",
            "face_matched": "वोटर दा चेहरा मेल खा गया",
            "proceeding_with_status": "स्थिति अद्यतन हो रिया है।",
            "face_not_matched": "वोटर दा चेहरा मेल नहीं खा रिया। कृपया फिर तो प्रयास करो।",
            "missing_info": "वोटर आईडी विच कझ जानकारी गुम है। कृपया फिर तो प्रयास करो।",
            "QR_DATA": "स्कैन कीता गया डेटा:",
            "scan_face": "चेहरा स्कैन करो"
        },
        "Manipuri": {
            "instruction_text": """
        1. সরকার তোকরি অধিকারিত ID আঙ্গা পাসওয়ার্ড সঙা \n        লগইন তোরা।
        2. পাসওয়ার্ড টাইপ তোকরার আগে হৌদবা লো, কারো দেখিবে নাই।
        3. তুমার পাসওয়ার্ড মাপদা সেয়া চেংবী।
        """,
            "title": "পোলিং বুথ QR কোড স্ক্যানার",
            "login": "লগইন",
            "username": "ব্যবহারকারী নাম",
            "password": "পাসওয়ার্ড",
            "login_button": "লগইন তোরা",
            "scan_button": "স্ক্যানিং শুৰু তোরা",
            "exit_button": "বাহির তোরা",
            "scan_qr_instruction": "আরম্ভ করার জন্য QR কোড স্ক্যান তোরা",
            "please_login": "অনুগ্রহ করে লগইন তোরা",
            "login_successful": "লগইন সফল! নির্ধারিত স্টেশন: {assigned_station}",
            "invalid_password": "অবৈধ পাসওয়ার্ড। দয়া করে পুনরায় চেষ্টা তোরা।",
            "operator_not_found": "অপারেটর ডাটাবেসে পাওয়া যায়নি।",
            "command_not_recognized": "কমান্ড চিন্তানা। 'scan qr' অদা 'exit' চেষ্টা তোরা।",
            "voter_status_not_found": "ভোটার ডাটাবেসে পাওয়া যায়নি।",
            "voter_data_mismatch": "ভোটার তথ্য ডাটাবেসে মেলে না।",
            "voter_underage": "ভোটার ১৮ বছর সিংদা উঠবা অউর ভোট দেয়া পইরা নাহি।",
            "voter_already_voted": "ভোটার {station} এ আগরো ভোট দিছে।",
            "voter_voted": "ভোটার {name} নু '{station}' এ 'ভোট' এ চিহ্নিত করা গেইছে।",
            "face_matching_in_progress": "মুখ মেলানোর প্রক্রিয়া চলি রইছে...",
            "face_matched": "ভোটারের মুখ মেলানো গেইছে",
            "proceeding_with_status": "স্থিতি আপডেট প্রক্রিয়া চলি রইছে।",
            "face_not_matched": "ভোটারের মুখ মেলানো না গেইছে। পুনরায় চেষ্টা তোরা।",
            "missing_info": "ভোটার ID তে কিছুমান তথ্য অনুপস্থিত। পুনরায় চেষ্টা তোরা।",
            "QR_DATA": "স্ক্যান করা তথ্য:",
            "scan_face": "মুখ স্ক্যান তোরা"
        },

    "Marwari": {
        "instruction_text": """
        1. सरकार द्वारा दी गई अधिकृत ID और पासवर्ड के साथ \n        लॉगिन करो।
        2. पासवर्ड टाइप करने से पहले यह सुनिश्चित करो कि कोई नहीं देख रहा हो।
        3. अपना पासवर्ड किसी से भी साझा न करो।
        """,
        "title": "पोलिंग बूथ QR कोड स्कैनर",
        "login": "लॉगिन",
        "username": "उपयोगकर्ता नाम",
        "password": "पासवर्ड",
        "login_button": "लॉगिन करो",
        "scan_button": "स्कैनिंग शुरू करो",
        "exit_button": "बाहर जाओ",
        "scan_qr_instruction": "आरंभ करने के लिए QR कोड स्कैन करो",
        "please_login": "कृपया लॉगिन करो",
        "login_successful": "लॉगिन सफल! निर्दिष्ट स्टेशन: {assigned_station}",
        "invalid_password": "अमान्य पासवर्ड। कृपया पुनः प्रयास करो।",
        "operator_not_found": "ऑपरेटर डाटाबेस में नहीं मिला।",
        "command_not_recognized": "आदेश पहचाना नहीं गया। 'scan qr' या 'exit' आजमाओ।",
        "voter_status_not_found": "वोटर डाटाबेस में नहीं मिला।",
        "voter_data_mismatch": "वोटर डेटा डाटाबेस से मेल नहीं खाता।",
        "voter_underage": "वोटर 18 वर्ष से कम है और मतदान नहीं कर सकता।",
        "voter_already_voted": "वोटर ने पहले ही {station} पर मतदान किया है।",
        "voter_voted": "वोटर {name} को '{station}' पर 'वोट' के रूप में चिह्नित किया गया है।",
        "face_matching_in_progress": "चेहरे का मिलान किया जा रहा है...",
        "face_matched": "वोटर का चेहरा मेल खा गया",
        "proceeding_with_status": "स्थिति अद्यतन किया जा रहा है।",
        "face_not_matched": "वोटर का चेहरा मेल नहीं खाता है। कृपया पुनः प्रयास करो।",
        "missing_info": "वोटर आईडी में कुछ जानकारी गायब है। कृपया पुनः प्रयास करो।",
        "QR_DATA": "स्कैन किए गए डेटा:",
        "scan_face": "चेहरा स्कैन करो"
    },

    "Sindhi": {
    "instruction_text": """
1. حڪومت پاران مهيا ڪيل مجاز ID ۽ پاسورڊ سان \n        لاگ ان ٿيو.
2. پاسورڊ ٽائپ ڪرڻ کان پوء يقيني بڻايو ته ڪو نٿو ڏسي رهيو هجي.
3. پنهنجو پاسورڊ ڪنهن سان به شيئر نه ڪريو.
""",
    "title": "پولنگ بوٿ QR ڪوڊ اسڪينر",
    "login": "لاگ ان",
    "username": "استعمال ڪندڙ جو نالو:",
    "password": "پاسورڊ:",
    "login_button": "لاگ ان ڪريو",
    "scan_button": "اسڪيننگ شروع ڪريو",
    "exit_button": "ٻاهر نڪرو",
    "scan_qr_instruction": "شروع ڪرڻ لاءِ QR ڪوڊ اسڪين ڪريو",
    "please_login": "مهرباني ڪري لاگ ان ڪريو",
    "login_successful": "لاگ ان ڪامياب! مقرر ٿيل اسٽیشن: {assigned_station}",
    "invalid_password": "غلط پاسورڊ. مهرباني ڪري ٻيهر ڪوشش ڪريو.",
    "operator_not_found": "آپريٽر ڊيٽابيس ۾ ناهي مليو.",
    "command_not_recognized": "حکم کي تسليم نه ڪيو ويو. 'scan qr' يا 'exit' آزمائي ڏسو.",
    "voter_status_not_found": "ووٽر ڊيٽابيس ۾ ناهي مليو.",
    "voter_data_mismatch": "ووٽر جو ڊيٽا ڊيٽابيس سان ملندڙ ناهي.",
    "voter_underage": "ووٽر 18 سالن کان گهٽ آهي ۽ ووٽ نه ٿو ڏئي سگھي.",
    "voter_already_voted": "ووٽر اڳ ئي {station} تي ووٽ ڏئي چڪو آهي.",
    "voter_voted": "ووٽر {name} کي '{station}' تي 'ووٽ' طور نشان لڳايو ويو آهي.",
    "face_matching_in_progress": "چهره ملائڻ جو عمل جاري آهي...",
    "face_matched": "ووٽر جو چهرو مل چڪو آهي",
    "proceeding_with_status": "اسٽيٽس اپڊيٽ ٿي رهيو آهي.",
    "face_not_matched": "ووٽر جو چهرو ناهي مليو. مهرباني ڪري ٻيهر ڪوشش ڪريو.",
    "missing_info": "ووٽر ID ۾ ڪجهه معلومات گم آهي. مهرباني ڪري ٻيهر ڪوشش ڪريو.",
    "QR_DATA": "اسڪين ٿيل ڊيٽا:",
    "scan_face": "چهرو اسڪين ڪريو"
},
"Assamese": {
    "instruction_text": """
1. চৰকাৰৰ পৰা প্ৰদান কৰা অনুমোদিত ID আৰু পাসৱৰ্ডৰ সৈতে \n        লগিন কৰক।
2. পাসৱৰ্ড টাইপ কৰাৰ পূৰ্বে এইটো নিশ্চিত কৰক যে, কোনোবাই চাওঁ নাই।
3. আপোনাৰ পাসৱৰ্ড কাকো ভাগ নকৰিব।
""",
    "title": "পোলিং বুথ QR কোড স্কেনাৰ",
    "login": "লগিন",
    "username": "ব্যৱহাৰকাৰী নাম",
    "password": "পাসৱৰ্ড",
    "login_button": "লগিন কৰক",
    "scan_button": "স্কেনিং আৰম্ভ কৰক",
    "exit_button": "বাহিৰ যাৱ",
    "scan_qr_instruction": "আৰম্ভ কৰিবলৈ QR কোড স্কেন কৰক",
    "please_login": "অনুগ্ৰহ কৰি লগিন কৰক",
    "login_successful": "লগিন সফল! নিদিষ্ট ষ্টেচন: {assigned_station}",
    "invalid_password": "অবৈধ পাসৱৰ্ড। অনুগ্ৰহ কৰি পুনৰ চেষ্টা কৰক।",
    "operator_not_found": "অপাৰেটৰ ডেটাবেছত পোৱা নগ'ল।",
    "command_not_recognized": "আদেশ চিনাকি কৰা নগ'ল। 'scan qr' বা 'exit' চেষ্টা কৰক।",
    "voter_status_not_found": "ভোটাৰ ডেটাবেছত পোৱা নগ'ল।",
    "voter_data_mismatch": "ভোটাৰৰ ডেটা ডেটাবেছৰ সৈতে মিলা নাই।",
    "voter_underage": "ভোটাৰ ১৮ বছৰৰ পৰা কম আৰু ভোট দিব পৰা নাযায়।",
    "voter_already_voted": "ভোটাৰ {station} ত আগতে ভোট দিছে।",
    "voter_voted": "ভোটাৰ {name} ক '{station}' ত 'ভোট' হিচাপে চিনাক্ত কৰা হৈছে।",
    "face_matching_in_progress": "মুখ মেলাৰ প্ৰক্ৰিয়া চলি আছে...",
    "face_matched": "ভোটাৰৰ মুখ মেল খাইছে",
    "proceeding_with_status": "স্থিতি আপডেট কৰি আছে।",
    "face_not_matched": "ভোটাৰৰ মুখ মেল নাই। অনুগ্ৰহ কৰি পুনৰ চেষ্টা কৰক।",
    "missing_info": "ভোটাৰ আইডিত কিছুমান তথ্য অনুপস্থিত। অনুগ্ৰহ কৰি পুনৰ চেষ্টা কৰক।",
    "QR_DATA": "স্কেন কৰা তথ্য:",
    "scan_face": "মুখ স্কেন কৰক"
},
"Odia": {
    "instruction_text": """
1. ସରକାର ଦ୍ୱାରା ପ୍ରଦାନ କରାଯାଇଥିବା ଅଧିକୃତ ID ଓ ପାସୱାର୍ଡ ସହିତ \n        ଲଗଇନ କରନ୍ତୁ।
2. ପାସୱାର୍ଡ ଟାଇପ କରିବା ପୂର୍ବରୁ ଏହା ସୁନିଶ୍ଚିତ କରନ୍ତୁ ଯେ କେହି ଦେଖୁନାହିଁ।
3. ଆପଣଙ୍କର ପାସୱାର୍ଡ କାହା ସହିତ ଶେୟାର କରିବେନାହିଁ।
""",
    "title": "ପୋଲିଂ ବୁଥ QR କୋଡ୍ ସ୍କ୍ୟାନର",
    "login": "ଲଗଇନ",
    "username": "ଉପଯୋଗକର୍ତ୍ତା ନାମ",
    "password": "ପାସୱାର୍ଡ",
    "login_button": "ଲଗଇନ କରନ୍ତୁ",
    "scan_button": "ସ୍କ୍ୟାନିଂ ଆରମ୍ଭ କରନ୍ତୁ",
    "exit_button": "ବାହାର ଯାଆନ୍ତୁ",
    "scan_qr_instruction": "ଆରମ୍ଭ କରିବା ପାଇଁ QR କୋଡ୍ ସ୍କ୍ୟାନ କରନ୍ତୁ",
    "please_login": "ଦୟାକରି ଲଗଇନ କରନ୍ତୁ",
    "login_successful": "ଲଗଇନ ସଫଳ! ନିର୍ଦ୍ଦିଷ୍ଟ ଷ୍ଟେସନ୍: {assigned_station}",
    "invalid_password": "ଅବৈଧ ପାସୱାର୍ଡ। ଦୟାକରି ପୁନଃ ଚେଷ୍ଟା କରନ୍ତୁ।",
    "operator_not_found": "ଓପରେଟର ଡେଟାବେସରେ ମିଳିଲା ନାହିଁ।",
    "command_not_recognized": "ଆଦେଶ ପ୍ରତିଷ୍ଠାନ ହୋଇନାହିଁ। 'scan qr' କିମ୍ବା 'exit' ପରୀକ୍ଷା କରନ୍ତୁ।",
    "voter_status_not_found": "ଭୋଟର ଡେଟାବେସରେ ମିଳିଲା ନାହିଁ।",
    "voter_data_mismatch": "ଭୋଟର ତଥ୍ୟ ଡେଟାବେସ ସହିତ ମିଳୁନାହିଁ।",
    "voter_underage": "ଭୋଟର 18 ବର୍ଷରୁ କମ ଓ ଭୋଟ ଦେବାକୁ ଅସମର୍ଥ।",
    "voter_already_voted": "ଭୋଟର ପୂର୍ବରୁ {station} ରେ ଭୋଟ ଦେଇଛି।",
    "voter_voted": "ଭୋଟର {name} କୁ '{station}' ରେ 'ଭୋଟ' ଭାବେ ପରିଚିତ କରାଯାଇଛି।",
    "face_matching_in_progress": "ମୁହଁ ସମନ୍ୱୟ କରାଯାଇଛି...",
    "face_matched": "ଭୋଟରର ମୁହଁ ସମନ୍ୱୟ ହୋଇଛି",
    "proceeding_with_status": "ସ୍ଥିତି ଅପଡେଟ୍ କରାଯାଇଛି।",
    "face_not_matched": "ଭୋଟରର ମୁହଁ ସମନ୍ୱୟ ହୋଇନାହିଁ। ଦୟାକରି ପୁନଃ ଚେଷ୍ଟା କରନ୍ତୁ।",
    "missing_info": "ଭୋଟର ID ରେ କିଛି ତଥ୍ୟ ଅନୁପସ୍ଥିତ। ଦୟାକରି ପୁନଃ ଚେଷ୍ଟା କରନ୍ତୁ।",
    "QR_DATA": "ସ୍କ୍ୟାନ୍ ହୋଇଥିବା ତଥ୍ୟ:",
    "scan_face": "ମୁହଁ ସ୍କ୍ୟାନ କରନ୍ତୁ"
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
    language_options = ["English", "Hindi","Assamese","Bengali","Bodo","Dogri","Gujarati","Kannada","Kashmiri","Konkani","Maithili","Malayalam","Manipuri","Marathi","Nepali",
                        "Odia","Punjabi","Sanskrit","Santhali","Sindhi","Telugu","Tamil"]

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
            exit_button = tk.Button(root, text=get_translation(language,"exit_button"), font=("STENCIL", 27), bg="#e94e77", fg="white", width=20,
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
        username_placeholder = get_translation(language, "username")
        password_placeholder = get_translation(language, "password")
        # Update placeholders in the entry fields
        username_entry.delete(0, tk.END)  # Clear current text
        username_entry.insert(0, username_placeholder)  # Insert new placeholder text
        password_entry.delete(0, tk.END)
        password_entry.insert(0, password_placeholder)

        username_entry.config(fg='#B0B0B0')  # Reset the placeholder color (gray)

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

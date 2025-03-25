import sys
import os
import subprocess

# Get the correct path for the .dat file inside the PyInstaller bundle
if getattr(sys, 'frozen', False):
    # Running as a PyInstaller bundle
    dat_file = os.path.join(sys._MEIPASS, "shape_predictor_68_face_landmarks.dat")
else:
    # Running in normal Python environment
    dat_file = "shape_predictor_68_face_landmarks.dat"

# Pass the correct path as an argument
subprocess.run(["python", "VoteXpress.py", dat_file])

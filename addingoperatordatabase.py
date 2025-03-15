import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
cred = credentials.Certificate("govt-database-firebase-adminsdk-fbsvc-a7ffad6280.json")# Path to your Firebase service account key
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

# Function to add an operator to Firestore
def add_operator(operator_id, operator_password, operator_station):
    # Operator data to be saved
    operator_data = {
        "operator_password": operator_password,
        "operator_station": operator_station
    }

    # Insert the operator data into Firestore
    db.collection("operators").document(operator_id).set(operator_data)
    print(f"Operator with ID {operator_id} added successfully!")

# Example usage
operator_id = "operator2"  # You can change this to any unique ID for the operator
operator_password = "password456"  # You can set the operator password here
operator_station = "Station 2"  # The station the operator is associated with

# Add the operator
add_operator(operator_id, operator_password, operator_station)

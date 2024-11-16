import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import datetime
import json

# Load employee activity data
def load_data(file_path):
    try:
        data = pd.read_csv(file_path)
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

# Preprocess the data
def preprocess_data(data):
    # Convert time-based features to numerical values
    data['login_time'] = pd.to_datetime(data['login_time'], format='%Y-%m-%d %H:%M:%S').map(datetime.datetime.timestamp)
    data['access_time'] = pd.to_datetime(data['access_time'], format='%Y-%m-%d %H:%M:%S').map(datetime.datetime.timestamp)

    # Select relevant features
    features = ['employee_id', 'login_time', 'access_time', 'access_level', 'files_accessed']
    processed_data = data[features]

    # Encode categorical data (e.g., employee_id)
    processed_data = pd.get_dummies(processed_data, columns=['employee_id'])

    return processed_data

# Train an Isolation Forest model to detect anomalies
def train_model(data):
    # Normalize the data
    scaler = StandardScaler()
    normalized_data = scaler.fit_transform(data)

    # Train Isolation Forest model
    model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    model.fit(normalized_data)
    return model, scaler

# Predict insider threats based on new activity
def predict_insider_threat(model, scaler, new_data):
    # Preprocess new data in a similar manner
    processed_new_data = preprocess_data(new_data)
    normalized_new_data = scaler.transform(processed_new_data)

    # Predict using the trained model (-1 means anomaly, 1 means normal)
    predictions = model.predict(normalized_new_data)
    new_data['threat'] = predictions

    # Print detected insider threats
    insider_threats = new_data[new_data['threat'] == -1]
    if not insider_threats.empty:
        print("Insider Threats Detected:")
        print(insider_threats[['employee_id', 'login_time', 'access_time', 'access_level', 'files_accessed']])
    else:
        print("No insider threats detected.")

    return insider_threats

if __name__ == "__main__":
    # Load historical activity data to train the model
    training_data = load_data('employee_activity_log.csv')
    if training_data is None:
        exit("Error: Training data could not be loaded.")

    # Preprocess the training data
    processed_data = preprocess_data(training_data)

    # Train the model
    model, scaler = train_model(processed_data)
    print("Model training complete.")

    # Load new employee activity data to check for insider threats
    new_data = load_data('new_employee_activity.csv')
    if new_data is not None:
        predict_insider_threat(model, scaler, new_data)

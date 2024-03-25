import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# Load the data from the Excel sheet
data = pd.read_excel("Symptoms.xlsx")

# Separate features (symptoms) and target variables (conditions)
X = data.drop(['Symptom', 'Time Period'], axis=1)  # Assuming 'Symptom' and 'Time Period' are not features
y_pneumonia = data['Pnemonia']
y_heart_failure = data['Heart Failure']

# Split the data into training and testing sets
X_train, X_test, y_train_pneumonia, y_test_pneumonia = train_test_split(X, y_pneumonia, test_size=0.2, random_state=42)
X_train, X_test, y_train_heart_failure, y_test_heart_failure = train_test_split(X, y_heart_failure, test_size=0.2, random_state=42)

# Train Random Forest classifiers for pneumonia and heart failure
rf_classifier_pneumonia = RandomForestClassifier()
rf_classifier_pneumonia.fit(X_train, y_train_pneumonia)

rf_classifier_heart_failure = RandomForestClassifier()
rf_classifier_heart_failure.fit(X_train, y_train_heart_failure)

# Make predictions
y_pred_pneumonia = rf_classifier_pneumonia.predict(X_test)
y_pred_heart_failure = rf_classifier_heart_failure.predict(X_test)

# Evaluate the models
print("Classification Report for Pneumonia:")
print(classification_report(y_test_pneumonia, y_pred_pneumonia))

print("\nClassification Report for Heart Failure:")
print(classification_report(y_test_heart_failure, y_pred_heart_failure))

from keras.models import load_model
import cv2
import numpy as np
import matplotlib.pyplot as plt

model = load_model('./models/pneumonia/pneumonia_pred_new.h5')

def predict(image):
    img = cv2.imdecode(np.fromstring(image.read(), np.uint8), cv2.IMREAD_COLOR)
    img = cv2.resize(img, (64, 64))
    img = np.reshape(img, [1, 64, 64, 3])

    # Predict classes and probabilities
    predictions = model.predict(img)
    predicted_class = int(predictions[0][0])
    probability = predictions[0][0]

    if predicted_class == 1:
        pred = 'POSITIVE'
    else:
        pred = 'NEGATIVE'
        probability = 1 - probability

    return 'The probability of the test being {} is {}% '.format(pred, int(probability * 100))

# imageee = 'person1947_bacteria_4876.jpeg'
# img = cv2.imread(imageee)
# img = cv2.resize(img, (64, 64))
# img = np.reshape(img, [1, 64, 64, 3])

# # Predict classes and probabilities
# predictions = model.predict(img)
# predicted_class = int(predictions[0][0])
# probability = predictions[0][0]

# if predicted_class == 1:
#     pred = 'POSITIVE'
# else:
#     pred = 'NEGATIVE'
#     probability = 1 - probability

# print("------------PREDICTION--------------")
# print()
# print("PNEUMONIA TEST RESULT : ", pred)
# print('The probability of the test being {} is {}% '.format(pred, int(probability * 100)))
# print("------------------------------------")
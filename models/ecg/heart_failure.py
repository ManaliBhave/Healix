from models.ecg.Ecg import ECG
import cv2
import numpy as np
# Initialize ecg object
ecg = ECG()

# Get the uploaded image
# Replace this with the path to your uploaded file

def ecg_predict(image):
    print(image.filename)
    if image is not None:
        # Call the getimage method
        #ecg_user_image_read = ecg.getImage(image)
        ecg_user_image_read = cv2.imdecode(np.fromstring(image.read(), np.uint8), cv2.IMREAD_COLOR)
        # Call the convert Grayscale image method
        ecg_user_gray_image_read = ecg.GrayImgae(ecg_user_image_read)

        # Call the Divide leads method
        dividing_leads = ecg.DividingLeads(ecg_user_image_read)

        # Call the preprocessed leads method
        ecg_preprocessed_leads = ecg.PreprocessingLeads(dividing_leads)

        # Call the signal extraction method
        ec_signal_extraction = ecg.SignalExtraction_Scaling(dividing_leads)

        # Call the combine and convert to 1D signal method
        ecg_1dsignal = ecg.CombineConvert1Dsignal()

        # Call the dimensionality reduction function
        ecg_final = ecg.DimensionalReduciton(ecg_1dsignal)

        # Call the Pretrained ML model for prediction
        ecg_model = ecg.ModelLoad_predict(ecg_final)
        print(ecg_model)
        return ecg_model

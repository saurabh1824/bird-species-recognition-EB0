import numpy as np
import os
import tensorflow as tf
from tensorflow.keras.applications.efficientnet import preprocess_input
from tensorflow.keras.preprocessing.image import load_img, img_to_array


def predict_pipeline(image_path):

    # # SAMPLE OUTPUT
    # predicted_class1 = "Predicted_class"
    # confidence_score = 0 #sample accuracy
    # return predicted_class1,confidence_score
    
    try:
        threshold = 0.75
        # model_path = os.path.join(os.getcwd(),'export\\bird_species_classifier_500p.keras')
        model_path = os.path.join(os.getcwd(),'export\\wenesday_3d_001.keras')
        model = tf.keras.models.load_model(model_path)
        classes = {0: 'Common-Kingfisher', 1: 'Common-Myna',
                   2: 'Indian-Peacock', 3: 'Indian-Roller', 
                   4: 'Vulture'}
        input_shape = (224, 224)
        img = load_img(image_path, target_size=input_shape)
        x = img_to_array(img)
        x = preprocess_input(x)
        preds = model.predict(np.array([x]))
        max_confidance = np.max(preds)
        index = np.argmax(preds)

        if max_confidance > threshold:
            predicted_class= np.argmax(preds)
            return classes[predicted_class],int(max_confidance*100)

        else:
            print(max_confidance)
            return "Unknown Bird or Object",int(max_confidance*100)


    except Exception as err:
        print(f"error: {err}")
        return "Error",0
        

# check predict_pipeline manually
# img_path = input()
# print(predict_pipeline(img_path))

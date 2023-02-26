import tensorflow as tf
import numpy as np
import urllib
import cv2

# Load the pre-trained InceptionV3 model
model = tf.keras.applications.InceptionV3()

# Define the meme template classes
classes = ['meme', 'not-meme']

# Function to preprocess an image for the model
def preprocess_image(image):
    # Resize the image to the input size of the model
    image = cv2.resize(image, (299, 299))
    # Convert the image to a numpy array
    image = np.array(image)
    # Preprocess the image to match the input format of the model
    image = tf.keras.applications.inception_v3.preprocess_input(image)
    # Add an extra dimension to the image to match the batch size of the model
    image = np.expand_dims(image, axis=0)
    return image

# Function to predict the class of an image
def predict_class(image):
    # Preprocess the image for the model
    image = preprocess_image(image)
    # Make a prediction using the model
    prediction = model.predict(image)
    # Get the predicted class index
    class_index = np.argmax(prediction[0])
    print(class_index)
    # Get the predicted class name
    class_name = classes[class_index]
    # Get the confidence score for the predicted class
    confidence = prediction[0][class_index]
    return class_name, confidence

# Example usage:
# Load an image from a URL
url = 'https://media.npr.org/assets/img/2015/03/03/overly_custom-39399d2cf8b6395770e3f10fd45b22ce39df70d4-s1100-c50.jpg'
image_data = urllib.request.urlopen(url).read()
image = cv2.imdecode(np.asarray(bytearray(image_data), dtype=np.uint8), cv2.IMREAD_COLOR)

# Predict the class of the image
class_name, confidence = predict_class(image)

# Print the result
print('Class:', class_name)
print('Confidence:', confidence)

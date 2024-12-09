# train_model.py
import cv2
import face_recognition
import os
import numpy as np
from .models import UserFace

def train_face_recognition_model():
    images = []
    labels = []

    # Load images from the database
    for user_face in UserFace.objects.all():
        image_path = user_face.face_image.path
        image = face_recognition.load_image_file(image_path)
        encoding = face_recognition.face_encodings(image)[0]
        images.append(encoding)
        labels.append(user_face.name)

    # Save the encodings and labels
    np.save('face_encodings.npy', images)
    np.save('face_labels.npy', labels)
    print("Model trained and saved successfully!")

import cv2
import os
import numpy as np
from PIL import Image

cascade_path = "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(cascade_path)

# recognizer = cv2.face.LBPHFaceRecognizer_create()
# recognizer = cv2.face.EigenFaceRecognizer_create()
recognizer = cv2.face.FisherFaceRecognizer_create()


def get_images_and_labels(path):
    image_paths = [os.path.join(path, f) for f in os.listdir(path) if not f.endswith('.sad')]
    images = []
    labels = []
    for image_path in image_paths:
        image_pil = Image.open(image_path).convert('L')
        image = np.array(image_pil, 'uint8')
        nbr = int(os.path.split(image_path)[1].split(".")[0].replace("subject", ""))
        faces = face_cascade.detectMultiScale(image)

        for (x, y, w, h) in faces:

            images.append(image[y: y + h, x: x + w])
            labels.append(nbr)
            cv2.imshow("Adding faces to traning set...", image[y: y + h, x: x + w])
            cv2.waitKey(500)
    return images, labels


path = 'yalefaces'
images, labels = get_images_and_labels(path)

recognizer.train(images, np.array(labels))
recognizer.save('trainer/trainer.yml')
# recognizer.load('trainer/trainer.yml')

image_paths = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.sad')]
for image_path in image_paths:
    predict_image_pil = Image.open(image_path).convert('L')
    predict_image = np.array(predict_image_pil, 'uint8')
    faces = face_cascade.detectMultiScale(predict_image)
for (x, y, w, h) in faces:
    nbr_predicted, conf = recognizer.predict(predict_image[y: y + h, x: x + w])
    nbr_actual = int(os.path.split(image_path)[1].split(".")[0].replace("subject", ""))
    if nbr_actual == nbr_predicted:
        print("{} is Correctly Recognized with confidence {}".format(nbr_actual, conf))
    else:
        print("{} is Incorrectly Recognized as {}".format(nbr_actual, nbr_predicted))
    cv2.imshow("Recognizing Face", predict_image[y: y + h, x: x + w])
    cv2.waitKey(1000)
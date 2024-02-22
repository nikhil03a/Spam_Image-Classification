from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from keras.models import load_model
from keras.preprocessing.image import load_img, img_to_array
import numpy as np
import cv2
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
api = Api(app)
model = load_model('SpamImageClassification.h5')
target_img = os.path.join(os.getcwd(), 'static/images')

ALLOWED_EXT = set(['jpg', 'jpeg', 'png'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXT

def read_image(filename):
    image = load_img(filename)
    image = image.resize((32, 32))
    image_array = img_to_array(image)
    if image_array.shape[2] == 1:
        image_array = cv2.cvtColor(image_array, cv2.COLOR_GRAY2RGB)
    image_array = image_array.reshape((1,) + image_array.shape)
    return image_array

class Predict(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('file', type=reqparse.FileStorage, location='files')
        args = parser.parse_args()

        if not args['file']:
            return {"error": "No file part"}

        file = args['file']
        if file and allowed_file(file.filename):
            filename = file.filename
            file_path = os.path.join('static/images', filename)
            try:
                file.save(file_path)
                img = read_image(file_path)
                class_prediction = model.predict(img)
                classes_x = np.argmax(class_prediction, axis=1)
                if classes_x == 0:
                    result = "Ham"
                else:
                    result = "Spam"
                return {"result": result, "probability": class_prediction.tolist(), "user_image": file_path}
            except FileNotFoundError:
                return {"error": "File not found. Please check the file path."}
            except Exception as e:
                return {"error": "An error occurred during file processing."}
        else:
            return {"error": "Invalid file format. Please check file extension"}

api.add_resource(Predict, '/api/predict')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, port=8000)
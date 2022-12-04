from flask import Flask, render_template, request
import cv2
import numpy as np
from PIL import Image
import io
import base64
import torch

# init Flask
app = Flask(__name__)

# init yolo model
model = torch.hub.load('ultralytics/yolov5', 'custom', './weight/yolov5l.pt') 

# HomePage request handler
@app.route("/", methods=['GET', 'POST'])
def home_page():
    if request.method == "GET":
        return render_template('index.html.j2')

    elif request.method == "POST":
        
        #read image file string data
        filestr = request.files['input_img'].read()
        #convert string data to numpy array
        file_bytes = np.fromstring(filestr, np.uint8)
        # convert numpy array to image
        img = cv2.imdecode(file_bytes, cv2.IMREAD_UNCHANGED)
        # convert from rgb to bgr
        img = cv2.cvtColor(img , cv2.COLOR_BGR2RGB)

        results = model(img)
        results.render()  # updates results.ims with boxes and labels
        for im in results.ims:
            buffered = io.BytesIO()
            im_base64 = Image.fromarray(im)
            im_base64.save(buffered, format="JPEG")
            base64img = "data:image/png;base64,"+ base64.b64encode(buffered.getvalue()).decode('utf-8')

        # get class name
        
        ingredients = results.pandas().xyxy[0].name
        ingredients = list(dict.fromkeys(ingredients))

        return { "user_image": base64img, "ingredients": ingredients}


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
from flask import Flask, render_template, request
import cv2
import numpy as np
from PIL import Image
import io
import base64
import torch
import pymongo

# connect db setup
URI = "mongodb+srv://ANJITA_admin:admin_ANJITA@cluster0.1hnatpx.mongodb.net/?retryWrites=true&w=majority"

client=pymongo.MongoClient(URI)

db = client.ANJITA_DB
FRecipes = db.Food_Recipes

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

# dishes request handler
@app.route("/getDishes", methods=['GET', 'POST'])
def getDishes():
    if request.method == 'GET':
        return {"dishes": "Bun Dau Mam Tom"}

# recipe request handler
@app.route("/getRecipes", methods=['GET', 'POST'])
def getRecipes():
    if request.method == 'GET':
        RecipesObj = FRecipes.find_one({'Dish': "BunDau"})
        Recipe = RecipesObj['Recipes']
        return {"Recipe": Recipe}

# login request handler
@app.route('/login')
def login():
	return render_template('login.html.j2')

@app.route('/submit', methods=['POST'])
def login_submit():
	_user_name = request.form['user_name']
	_password = request.form['inputPassword']
	# validate the received values
	if _user_name == 'admin' and _password == '0987654321' and request.method == "POST": return render_template('index.html.j2')
	else: return render_template('login.html.j2')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
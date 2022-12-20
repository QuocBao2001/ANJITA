import sys
sys.path.insert(0, './inversecooking/src')
from inversecooking.src.model import get_model
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import numpy as np
import os
from inversecooking.src.args import get_parser
import pickle
from torchvision import transforms
from inversecooking.src.utils.output_utils import prepare_output
from PIL import Image
import time

data_dir = './inversecooking/data'

# code will run in gpu if available and if the flag is set to True, else it will run on cpu
use_gpu = True
device = torch.device('cuda' if torch.cuda.is_available() and use_gpu else 'cpu')
map_loc = None if torch.cuda.is_available() and use_gpu else 'cpu'

ingrs_vocab = pickle.load(open(os.path.join(data_dir, 'ingr_vocab.pkl'), 'rb'))
vocab = pickle.load(open(os.path.join(data_dir, 'instr_vocab.pkl'), 'rb'))

ingr_vocab_size = len(ingrs_vocab)
instrs_vocab_size = len(vocab)
output_dim = instrs_vocab_size

t = time.time()
import sys; sys.argv=['']; del sys
args = get_parser()
args.maxseqlen = 15
args.ingrs_only=False
model = get_model(args, ingr_vocab_size, instrs_vocab_size)
# Load the trained model parameters
model_path = os.path.join(data_dir, 'modelbest.ckpt')
model.load_state_dict(torch.load(model_path, map_location=map_loc))
model.to(device)
model.eval()
model.ingrs_only = False
model.recipe_only = False
print ('loaded model')
print ("Elapsed time:", time.time() -t)

transf_list_batch = []
transf_list_batch.append(transforms.ToTensor())
transf_list_batch.append(transforms.Normalize((0.485, 0.456, 0.406), 
                                              (0.229, 0.224, 0.225)))
to_input_transf = transforms.Compose(transf_list_batch)

greedy = [True, False, False, False]
beam = [-1, -1, -1, -1]
temperature = 1.0
numgens = len(greedy)

import io
from flask import Flask, render_template, request
import cv2
import base64

# init Flask
app = Flask(__name__)

# save last model outputs
current_outs = None

# HomePage request handler
@app.route("/", methods=['GET', 'POST'])
def home_page():
    if request.method == "GET":
        return render_template('index.html.j2')

    elif request.method == "POST":
        
        #read image file string data
        filestr = request.files['input_img'].read()

        img = Image.open(io.BytesIO(filestr))

        transf_list = []
        transf_list.append(transforms.Resize(256))
        transf_list.append(transforms.CenterCrop(224))
        transform = transforms.Compose(transf_list)
        
        image_transf = transform(img)
        image_tensor = to_input_transf(image_transf).unsqueeze(0).to(device)
        
        num_valid = 1
        outs = [None] * numgens
        for i in range(numgens):
            with torch.no_grad():
                outputs = model.sample(image_tensor, greedy=greedy[i], 
                                    temperature=temperature, beam=beam[i], true_ingrs=None)
                
            ingr_ids = outputs['ingr_ids'].cpu().numpy()
            recipe_ids = outputs['recipe_ids'].cpu().numpy()
                
            outs[i], valid = prepare_output(recipe_ids[0], ingr_ids[0], ingrs_vocab, vocab)
            #print ("greedy:", greedy[i], "beam:", beam[i])

            # outs['title', 'ingrs', 'recipe']
            global current_outs
            current_outs = outs
        
        return outs

# dishes request handler
@app.route("/getDishes", methods=['GET', 'POST'])
def getDishes():
    if request.method == 'GET':
        return {"dishes": current_outs['title']}

# recipe request handler
@app.route("/getRecipes", methods=['GET', 'POST'])
def getRecipes():
    if request.method == 'GET':
        return {"Recipe": "ABC"}

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
    app.run(host='0.0.0.0', debug=False)

import io
import os
import flask 
import json
import pandas as pd
import numpy
from flask import request
from flask import send_file
import base64
from keras.models import load_model
import pickle
from io import StringIO
import sys
import signal
import traceback
from sklearn.preprocessing import MinMaxScaler
from sklearn.externals import joblib
import keras

app = flask.Flask(__name__)

CONTENT_IMAGE = None
STYLE_IMAGE = None


# Image size
IMAGE_SIZE = 500

# Loss Weights
CONTENT_WEIGHT = 0.025
STYLE_WEIGHT = 1.0
STYLE_SCALE = 1.0
TOTAL_VARIATION_WEIGHT = 8.5e-5
CONTENT_LOSS_TYPE = 0

# Training arguments
NUM_ITERATIONS = 1
MODEL = 'vgg19'
RESCALE_IMAGE = 'false'
MAINTAIN_ASPECT_RATIO = 'false'  # Set to false if OOM occurs

# Transfer Arguments
CONTENT_LAYER = 'conv' + '5_2'  # only change the number 5_2 to something in a similar format
INITIALIZATION_IMAGE = 'content'
POOLING_TYPE = 'max'

# Extra arguments
PRESERVE_COLOR = 'false'
MIN_IMPROVEMENT = 0.0

FINAL_IMAGE_PATH = "/opt/ml/gen_at_iteration_%d.png" % (NUM_ITERATIONS)
RESULT_PREFIX = "/opt/ml/gen"
INPUT_IMAGE_PREFIX = "/opt/ml/"
content_img = INPUT_IMAGE_PREFIX + "image1.jpg"
style_img = INPUT_IMAGE_PREFIX + "image2.jpg"

# class ScoringService(object):
#     model = None                # Where we keep the model when it's loaded

#     @classmethod
#     def get_model(cls):
#         """Get the model object for this instance, loading it if it's not already loaded."""
#         if cls.model == None:
#             cls.model = load_model('/opt/ml/vgg19_weights_tf_dim_ordering_tf_kernels_notop.h5')
#             cls.model._make_predict_function()
#         return cls.model

#     @classmethod
#     def predict(cls, input):
#         """For the input, do the predictions and return them.

#         Args:
#             input (a pandas dataframe): The data on which to do the predictions. There will be
#                 one prediction per row in the dataframe"""
#         clf = cls.get_model()
#         return clf.predict(input)



@app.route('/ping', methods=['GET'])
def ping():
    # print("Ping endpoint has been invoked")
    """Determine if the container is working and healthy. In this sample container, we declare
    it healthy if we can load the model successfully."""
    # health = ScoringService.get_model() is not None  # You can insert a health check here
    print(keras.backend.tensorflow_backend._get_available_gpus())
    # status = 200 if health else 404
    return flask.Response(response='\n', status=200, mimetype='application/json')



@app.route('/invocations', methods=['POST'])
def generateImage():
    print("invocations endpoint has been invoked")
    if (flask.request.content_type.split('/')[0]=="multipart") and ('form' in flask.request.content_type.split('/')[1]):
        print("The file is multipart/form-data")

        if 'content' in request.files:
            CONTENT_IMAGE = request.files['content']  
            CONTENT_IMAGE.save(content_img)
            x = True
        else:
            x = False
        if 'style' in request.files:
            STYLE_IMAGE = request.files['style']  
            STYLE_IMAGE.save(style_img)
            y = True
        else:
            y = False

        if (x & y) == False :
            return flask.Response(response="Require two images", status=400, mimetype='text/plain')
            
    elif (flask.request.content_type.split('/')[0]=="application") and (flask.request.content_type.split('/')[1]=="json"):
        print("The file is application/json")
        if 'content' in request.get_json():
            CONTENT_DATA = request.get_json()['content']
            CONTENT_IMAGE = base64.b64decode(CONTENT_DATA)
            with open(content_img, 'wb') as f:
                f.write(CONTENT_IMAGE)
            x = True
        else:
            x = False
       
        if 'style' in request.get_json():
            STYLE_DATA = request.get_json()['style']
            STYLE_IMAGE = base64.b64decode(STYLE_DATA)
            with open(style_img, 'wb') as f:
                f.write(STYLE_IMAGE)
            y = True
        else:
            y = False

        if (x & y) == False :
            return flask.Response(response="Require two images", status=400, mimetype='text/plain')
            
    else:
        return flask.Response(response='This supports application/json and multipart/form-data', status=200, mimetype='text/plain')

    os.system("python3 Network.py "+ content_img +" "+style_img +" "+RESULT_PREFIX+ " --image_size "+str(IMAGE_SIZE)+ " --content_weight "+str(CONTENT_WEIGHT)+ " --style_weight "+str(STYLE_WEIGHT)+ " --style_scale "+str(STYLE_SCALE)+" --total_variation_weight "+str(TOTAL_VARIATION_WEIGHT)+" --content_loss_type "+str(CONTENT_LOSS_TYPE)+" --num_iter "+str(NUM_ITERATIONS)+" --model "+MODEL+" --rescale_image "+RESCALE_IMAGE+" --maintain_aspect_ratio "+MAINTAIN_ASPECT_RATIO+" --content_layer "+CONTENT_LAYER+" --init_image "+INITIALIZATION_IMAGE+" --pool_type "+POOLING_TYPE+" --preserve_color "+PRESERVE_COLOR+" --min_improvement "+str(MIN_IMPROVEMENT)) 
   
    return send_file(FINAL_IMAGE_PATH, mimetype='image/png')
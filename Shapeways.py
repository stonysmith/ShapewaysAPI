#https://developers.shapeways.com
import base64
import requests
from urlparse import parse_qs
import json

API_VERSION = 'v1'
API_SERVER = 'api.shapeways.com'

class Shapeways(object):
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.body = [('grant_type', 'client_credentials'),]
        self.auth = (self.client_id,self.client_secret)
        self.access_token=""
        self.header = {'Authorization':'none'}

    def get_access_token(self):
        url='https://{host}/oauth2/token'.format(host=API_SERVER)
        response=requests.post(url, data=self.body, auth=self.auth)
        t=response.json()
        self.access_token=t['access_token']
        self.header={'Authorization':'bearer '+self.access_token}
        return self.access_token

    def get_materials(self):
        r = requests.get(url="https://{host}/materials/{version}".format(host=API_SERVER, version=API_VERSION), headers=self.header)
        return r.json()

    def get_models(self, page):
        r = requests.get(url="https://{host}/model/{version}?page={page}".format(host=API_SERVER, version=API_VERSION, page=page), headers=self.header)
        return r.json()

    def get_model(self, model_id):
        r = requests.get(url="https://{host}/model/{model_id}/{version}".format(host=API_SERVER, version=API_VERSION, model_id=model_id), headers=self.header)
        return r.json()
        
    def get_model_info(self, model_id):
        r = requests.get(url="https://{host}/models/{model_id}/info/{version}".format(host=API_SERVER, version=API_VERSION, model_id=model_id), headers=self.header)
        return r.json()

    def put_model_info(self, model_id):
        r = requests.put(url="https://{host}/models/{model_id}/info/{version}".format(host=API_SERVER, version=API_VERSION, model_id=model_id), headers=self.header)
        return r.json()

    def upload_model(self, filename):
        #This uploads the model with the filename as the title, no description or tags, and 
        #sets the model to Private and NotForSale
        file=open(filename,"rb")
        payload = {
            "file": base64.b64encode(file.read()),
            "fileName": filename,
            "uploadScale":.001,   #assume millimeters
            "hasRightsToModel": 1,
            "acceptTermsAndConditions": 1
        }
        r = requests.post(url="https://{host}/model/{version}".format(host=API_SERVER, version=API_VERSION), data=json.dumps(payload), headers=self.header)
        return r.json()
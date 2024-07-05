import base64
import urllib.parse
import urllib.request
import http.client
import json
import ssl

API_VERSION = 'v1'
API_SERVER = 'api.shapeways.com'

class Shapeways(object):
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth = (self.client_id, self.client_secret)
        self.access_token = ""
        self.header = {'Authorization': 'none'}

    def readurl(self, url, data, header):
        context = ssl._create_unverified_context()
        request = urllib.request.Request(url, data=data.encode('utf-8') if data else None, headers=header)
        try:
            response = urllib.request.urlopen(request, context=context)
        except urllib.error.HTTPError as e:
            code = str(e.reason)
            r = {"result": "failure", "type": "HTTPError", "reason": code, "url": url}
        except urllib.error.URLError as e:
            code = str(e.reason)
            r = {"result": "failure", "type": "URLError", "reason": code, "url": url}
        except http.client.HTTPException as e:
            if isinstance(e, http.client.BadStatusLine):  # Handle BadStatusLine exception separately
                code = "BadStatusLine"
            else:
                code = str(e)
            r = {"result": "failure", "type": "HTTPException", "reason": code, "url": url}
        else:
            html = response.read().decode('utf-8')
            if html[0] != "{":
                r = {"result": "failure", "reason": "error " + html}
            else:
                r = json.loads(html)
        return r

    def get_access_token(self):
        self.url = 'https://{host}/oauth2/token'.format(host=API_SERVER)
        data = "grant_type=client_credentials&client_id={}&client_secret={}".format(self.client_id, self.client_secret)
        context = ssl._create_unverified_context()
        response = urllib.request.urlopen(self.url, data=data.encode('utf-8'), context=context)
        html = response.read().decode('utf-8')
        try:
            t = json.loads(html)
        except:
            print("bad json=" + html)
        self.access_token = t['access_token']
        self.header = {'Authorization': 'bearer ' + self.access_token}
        return self.access_token

    def get_materials(self):
        self.url = "https://{host}/materials/{version}".format(host=API_SERVER, version=API_VERSION)
        r = self.readurl(self.url, None, self.header)
        return r

    def get_models(self, page):
        self.url = "https://{host}/model/{version}?page={page}".format(host=API_SERVER, version=API_VERSION, page=page)
        r = self.readurl(self.url, None, self.header)
        return r

    def get_model(self, model_id):
        self.url = "https://{host}/model/{model_id}/{version}".format(host=API_SERVER, version=API_VERSION, model_id=model_id)
        r = self.readurl(self.url, None, self.header)
        return r

    def get_model_file(self, model_id, ver=0):
        self.url = "https://{host}/models/{model_id}/files/{ver}/v1?file=1".format(host=API_SERVER, version=API_VERSION, ver=ver, model_id=model_id)
        r = self.readurl(self.url, None, self.header)
        return r
    
    def get_model_info(self, model_id):
        self.url = "https://{host}/models/{model_id}/info/{version}".format(host=API_SERVER, version=API_VERSION, model_id=model_id)
        r = self.readurl(self.url, None, self.header)
        return r

    def put_model_info(self, model_id, payload):
        self.url = "https://{host}/models/{model_id}/info/{version}".format(host=API_SERVER, version=API_VERSION, model_id=model_id)
        r = self.readurl(self.url, json.dumps(payload), self.header)
        return r

    def upload_model(self, filename):
        with open(filename, "rb") as file:
            payload = {
                "file": base64.b64encode(file.read()).decode('utf-8'),
                "fileName": filename,
                "ownOrAuthorizedModel": 1,
                "acceptTermsAndConditions": 1
            }
        self.url = "https://{host}/model/{version}".format(host=API_SERVER, version=API_VERSION)
        r = self.readurl(self.url, json.dumps(payload), self.header)
        return r

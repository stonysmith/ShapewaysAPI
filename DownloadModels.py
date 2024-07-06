import json
import os
import base64
from Shapeways_nossl import Shapeways
# Visit https://developers.shapeways.com/manage-apps to get your tokens
# Enter your ClientKey and ClientSecret here:
client_id='xxxxxxxxxxxxxxxxx'
client_secret='xxxxxxxxxxxxxxxxx'

client = Shapeways(AuthKeys.client_id, AuthKeys.client_secret)
at = client.get_access_token()

outFile=open("MyShopItems.csv", "r", newline='')

page = 1
import csv
csv_file=open("MyShopItems.csv", mode='r', newline='')
csv_reader = csv.DictReader(csv_file)
outFile.close()

line_count = 0
for row in csv_reader:
    print("Model="+row['modelId'])
    line_count +=1
    model=client.get_model_file(row['modelId'], row['modelVersion'])
    print(model['fileName'])
    modelfile=open("Models/Model_"+str(row['modelId'])+"_"+model['fileName'],"wb")
    data=base64.b64decode(model['fileData'])
    modelfile.write(data)
    modelfile.close()

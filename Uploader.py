import json
import os
import AuthKeys
from Shapeways import Shapeways

client=Shapeways(AuthKeys.client_id, AuthKeys.client_secret)
at=client.get_access_token()

path="c:/users/path/to/files"
path="C:/Users/Stony/Desktop/temp"
if not os.path.exists(path):
	print("Path does not exist")
	exit()
if not os.path.exists(path+"/Archive"):
        os.mkdir(path+"/Archive")
d=os.listdir(path)
f=open("results.txt","w")
rec="FileName,Result,ModelId\n"
f.write(rec)
for file in d:
	if file<>"Archive":
		filename=path+"/"+file
		print filename
		t=client.upload_model(filename)
		result=t["result"]
		print filename+","+result
		rec=filename+","+str(result)+","+str(t["modelId"])+"\n"
		f.write(rec)
		if result == "success":
			os.rename(filename,path+"/Archive/"+file)
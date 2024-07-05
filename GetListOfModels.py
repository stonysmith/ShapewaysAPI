import json
import os
import AuthKeys
from Shapeways_nossl import Shapeways

client = Shapeways(AuthKeys.client_id, AuthKeys.client_secret)
at = client.get_access_token()

with open("MyShopItems.csv", "w", newline='') as outFile:
    outFile.write("title,modelVersion,modelId\n")

    page = 1
    t = client.get_models(page)
    q = t["models"]
    
    while q:
        print("Page=" + str(page))
        for f in q:
            rec = {}
            for p in f.items():
                rec[str(p[0])] = str(p[1])
            outFile.write(rec["title"] + "," + rec["modelVersion"] + "," + rec["modelId"] + "\n")
        
        page += 1
        t = client.get_models(page)
        q = t["models"]

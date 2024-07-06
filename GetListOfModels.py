import json
import os
from Shapeways_nossl import Shapeways

# Visit https://developers.shapeways.com/manage-apps to get your tokens
# Enter your ClientKey and ClientSecret here:
client_id='xxxxxxxxxxxxxxxxx'
client_secret='xxxxxxxxxxxxxxxxx'

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

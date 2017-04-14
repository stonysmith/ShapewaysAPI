bl_info = {
    "name": "Shapeways API",
    "author": "Stony Smith 2017-04-06",
    "version": (1, 0),
    "blender": (2, 65, 0),
    "location": "SpaceBar Search -> Shapeways API",
    "description": "Shapeways API Addon",
    "warning": "",
    "wiki_url": "https://developers.shapeways.com/docs",
    "tracker_url": "",
    "category": "Object"}

import bpy
from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty

class ShapewaysAPIAddonPreferences(AddonPreferences):
    bl_idname = __name__

    clientId = StringProperty(
            name="Client Id",
            )
    clientSecret = StringProperty(
            name="Client Secret",
            )
    AccessToken = StringProperty(
            name="Access Token",
            )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Get these values from https://developers.shapeways.com/manage-apps")
        layout.prop(self, "clientId")
        layout.prop(self, "clientSecret")
        layout.operator("props.get_access_token", text = "Get AccessToken")
        layout.prop(self, "AccessToken")
        return {'FINISHED'}

class ShapewaysAPI_GetAccessToken(Operator) :
    bl_idname = "props.get_access_token"
    bl_label = "Get AccessToken"

    def invoke(self, context, event) :
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        client_id=addon_prefs.clientId
        if client_id=="":
            client_id="clientId from https://developers.shapeways.com/manage-apps"
            addon_prefs.clientId=client_id
        client_secret=addon_prefs.clientSecret
        if client_secret=="":
            client_secret="clientSecret from https://developers.shapeways.com/manage-apps"
            addon_prefs.clientSecret=client_secret
        data = [('grant_type', 'client_credentials'),]
        self.client=Shapeways(client_id, client_secret)
        access_token=self.client.get_access_token()
        addon_prefs.AccessToken = access_token
        return {'FINISHED'}

class OBJECT_OT_shapeways_api_addon_prefs(Operator):
    """Display Shapeways API preferences"""
    bl_idname = "object.shapeways_api_addon_prefs"
    bl_label = "Shapeways API Addon Preferences"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences

        info = ("clientId: %s, clientSecret: %s, AccessToken %s" %
                (addon_prefs.clientId, addon_prefs.clientSecret, addon_prefs.AccessToken))

        self.report({'INFO'}, info)
        print(info)

        return {'FINISHED'}

class OBJECT_PT_ShapewaysAPI_Materials(bpy.types.Panel):
    bl_label = "Shapeways API"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    def draw(self, context):
        ob_cols = []
        db_cols = []

        objects = bpy.data.objects

        layout = self.layout
        
        # OBJECTS

        l_row = layout.row()
        num = len(bpy.data.objects)
        l_row.label(text=quantity_string(num, "Object", "Objects")
            + " in the scene:",
            icon='OBJECT_DATA')

        l_row = layout.row()
        ob_cols.append(l_row.column())
        ob_cols.append(l_row.column())

        row = ob_cols[0].row()
        meshes = [o for o in objects.values() if o.type == 'MESH']
        num = len(meshes)
        row.label(text=quantity_string(num, "Mesh", "Meshes"),
            icon='MESH_DATA')

        layout.separator()
        
        # DATABLOCKS

        l_row = layout.row()
        num = len(bpy.data.objects)
        l_row.label(text="Datablocks in the scene:")

        l_row = layout.row()
        db_cols.append(l_row.column())
        db_cols.append(l_row.column())

        row = db_cols[0].row()
        num = len(bpy.data.meshes)
        row.label(text=quantity_string(num, "Mesh", "Meshes"),
            icon='MESH_DATA')

import base64
import requests
#from urlparse import parse_qs
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
        self.access_token=str(t['access_token'])
        self.header={'Authorization':'bearer '+self.access_token}
        return self.access_token

    def get_materials(self):
        r = requests.get(url="https://{host}/materials/{version}".format(host=API_SERVER, version=API_VERSION), headers=self.header)
        return r.json()

    def upload_model(self, filename):
        file=open(filename,"rb")
        filedata=base64.b64encode(file.read())
        filedata=filedata.decode("utf-8")
        payload = {
            "file": filedata,
            "fileName": filename,
            "uploadScale":.001,   #assume millimeters
            "ownOrAuthorizedModel": 1,
            "acceptTermsAndConditions": 1
        }
        r = requests.post(url="https://{host}/model/{version}".format(host=API_SERVER, version=API_VERSION), data=json.dumps(payload), headers=self.header)
        return r.json()
##################################
class ShapewaysToolsPanel(bpy.types.Panel):
    bl_label = "Shapeways Tools"
    bl_category = "Shapeways"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
 
    def draw(self, context):
        self.layout.operator("shapeways.upload", text='Upload')

class Shapeways_UploadAction(bpy.types.Operator):
    bl_idname = "shapeways.upload"
    bl_label = "Shapeways Upload"

    def invoke(self, context, event) :
        addon_prefs = context.user_preferences.addons[__name__].preferences
        data = [('grant_type', 'client_credentials'),]
        client=Shapeways(addon_prefs.clientId, addon_prefs.clientSecret)
        access_token=client.get_access_token()
        #addon_prefs.AccessToken = access_token
        resp=client.upload_model("C:/Users/Stony/Desktop/box.stl")
        result=resp["result"]
        bpy.ops.shapewayserror.message('INVOKE_DEFAULT', type = "Message", message = str(resp))
        return {'FINISHED'}
##################################
class ShapewaysMessageOperator(bpy.types.Operator):
    bl_idname = "shapewayserror.message"
    bl_label = "Message"
    type = StringProperty()
    message = StringProperty()
 
    def execute(self, context):
        self.report({'INFO'}, self.message)
        print(self.message)
        return {'FINISHED'}
 
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self, width=400, height=200)
 
    def draw(self, context):
        self.layout.label("A message has arrived")
        row = self.layout.split(0.25)
        row.prop(self, "type")
        row.prop(self, "message")
        row = self.layout.split(0.80)
        row.label("") 
        row.operator("error.ok")
 
#
#   The OK button in the error dialog
#
class ShapewaysOkOperator(bpy.types.Operator):
    bl_idname = "error.ok"
    bl_label = "OK"
    def execute(self, context):
        return {'FINISHED'}
##################################
# Registration
def register():
    bpy.utils.register_class(ShapewaysAPIAddonPreferences)
    bpy.utils.register_class(ShapewaysAPI_GetAccessToken)
    bpy.utils.register_class(ShapewaysToolsPanel)
    bpy.utils.register_class(Shapeways_UploadAction)
    bpy.utils.register_class(ShapewaysMessageOperator)
    bpy.utils.register_class(ShapewaysOkOperator)
    bpy.utils.register_class(OBJECT_PT_ShapewaysAPI_Materials)

def unregister():
    bpy.utils.unregister_class(OBJECT_PT_ShapewaysAPI_Materials)
    bpy.utils.unregister_class(ShapewaysOkOperator)
    bpy.utils.unregister_class(ShapewaysMessageOperator)
    bpy.utils.unregister_class(Shapeways_UploadAction)
    bpy.utils.unregister_class(ShapewaysToolsPanel)
    bpy.utils.unregister_class(ShapewaysAPI_GetAccessToken)
    bpy.utils.unregister_class(ShapewaysAPIAddonPreferences)

if __name__ == "__main__":
    register()
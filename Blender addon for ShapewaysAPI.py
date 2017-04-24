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
from bpy.types import Panel, Operator, AddonPreferences, PropertyGroup
from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty, PointerProperty
import os

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

    def upload_model(self, filename,title):
        file=open(filename,"rb")
        filedata=base64.b64encode(file.read())
        filedata=filedata.decode("utf-8")
        payload = {
            "file": filedata,
            "fileName": title,
            "uploadScale":.001,   #assume millimeters
            "ownOrAuthorizedModel": 1,
            "acceptTermsAndConditions": 1
        }
        r = requests.post(url="https://{host}/model/{version}".format(host=API_SERVER, version=API_VERSION),data=json.dumps(payload), headers=self.header)
        return r.json()

    def get_model_info(self, model_id):
        r = requests.get(url="https://{host}/models/{model_id}/info/{version}".format(host=API_SERVER, version=API_VERSION, model_id=model_id), headers=self.header)
        return r.json()
##################################

class ShapewaysSettings(PropertyGroup):
        scale = bpy.props.EnumProperty(name="Scale",
            items = (
                ('1', "1", "Meters"),
                ('0.001', "0.001", "Millimeters"),
                ('0.0254', "0.0254", "Inches")
                ),
            description = "The scale for the model",default='0.001')
        #materials = bpy.props.EnumProperty(name="Scale",items=ShapewaysMaterialList,description='Materials',default='61')

        fn='mymodel.stl'
        filename = bpy.props.StringProperty(name="filename",description = "Output FileName",default = fn)
        message = bpy.props.StringProperty(name="message",description = "Message",default = "")
        modelid = bpy.props.StringProperty(name="modelid",description = "ModelId",default = "")
        spin = bpy.props.StringProperty(name="spin",description = "Spin",default = "")

class ShapewaysToolsPanel(bpy.types.Panel):
    bl_idname = "shapeways.tools"
    bl_label = "Shapeways Tools"
    bl_category = "Shapeways"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool

        # display the properties
        layout.prop(mytool, "scale", text="Scale")
        layout.prop(mytool, "filename", text="Filename")
        layout.operator("shapeways.upload", text='Upload')
        layout.prop(mytool, "message", text="Message")
        layout.prop(mytool, "modelid", text="modelid")
        layout.prop(mytool, "spin", text="spin")
        layout.operator("shapeways.modelinfo", text='Check Status')
        layout.operator("browser.open", text='Open at Shapeways')
 
class OpenInBrowser(bpy.types.Operator):
    bl_idname = "browser.open"
    bl_label = "Open at Shapeways"

    def invoke(self, context, event) :
        import webbrowser
        my_data=bpy.data.scenes["Scene"].my_tool
        modelId=my_data.modelid
        URL='https://www.shapeways.com/model/upload-and-buy/'+str(modelId)
        webbrowser.open(URL,new=0);
        return {'FINISHED'}

class Shapeways_ModelInfo(bpy.types.Operator):
    bl_idname = "shapeways.modelinfo"
    bl_label = "Shapeways ModelInfo"

    def invoke(self, context, event) :
        addon_prefs = context.user_preferences.addons[__name__].preferences
        data = [('grant_type', 'client_credentials'),]
        client=Shapeways(addon_prefs.clientId, addon_prefs.clientSecret)
        access_token=client.get_access_token()
        addon_prefs.AccessToken = access_token
        #access_token=addon_prefs.AccessToken
        my_data=bpy.data.scenes["Scene"].my_tool
        modelId=my_data.modelid

        bpy.context.window.cursor_set("WAIT")
        resp=client.get_model_info(modelId)
        bpy.context.window.cursor_set("DEFAULT")

        self.report({'INFO'}, "Response="+str(resp))
        result=resp["result"]
        spin=resp['spin']
        self.report({'INFO'}, "Spin="+str(spin))
        #modelId=str(resp['modelId'])
        #self.report({'INFO'}, "ModelId="+str(modelId))
        #bpy.ops.shapewayserror.message('INVOKE_DEFAULT', result = result, json = str(resp), modelid = modelId, spin = spin)
        my_data.message = result
        my_data.spin=spin
        #bpy.ops.shapeways.tools.message=str(resp)
        return {'FINISHED'}

class Shapeways_UploadAction(bpy.types.Operator):
    bl_idname = "shapeways.upload"
    bl_label = "Shapeways Upload"

    def invoke(self, context, event) :
        addon_prefs = context.user_preferences.addons[__name__].preferences
        data = [('grant_type', 'client_credentials'),]
        client=Shapeways(addon_prefs.clientId, addon_prefs.clientSecret)
        access_token=client.get_access_token()
        #addon_prefs.AccessToken = access_token
        my_data=bpy.data.scenes["Scene"].my_tool
        filepath=bpy.data.filepath
        filename = bpy.path.basename(filepath)
        filename = filename.replace(".blend",".stl")
        title=filename.replace(".blend","")
        directory = os.path.dirname(filepath)
        newfile_name = os.path.join( directory , filename)

        my_data.message = "Saving"
        self.report({'INFO'}, "Saving "+filename)
        bpy.context.window.cursor_set("WAIT")
        bpy.ops.export_mesh.stl(filepath=newfile_name, check_existing=False, ascii=False)
        bpy.context.window.cursor_set("DEFAULT")

        my_data.message = "Uploading"
        self.report({'INFO'}, "Uploading "+filename)
        bpy.context.window.cursor_set("WAIT")
        resp=client.upload_model(newfile_name,title)
        bpy.context.window.cursor_set("DEFAULT")

        self.report({'INFO'}, "Response="+str(resp))
        result=resp["result"]
        spin=resp['spin']
        self.report({'INFO'}, "Spin="+str(spin))
        modelId=str(resp['modelId'])
        self.report({'INFO'}, "ModelId="+str(modelId))
        bpy.ops.shapewayserror.message('INVOKE_DEFAULT', result = result, json = str(resp), modelid = modelId, spin = spin)
        my_data.message = result
        my_data.modelid=modelId
        my_data.spin=spin
        #bpy.ops.shapeways.tools.message=str(resp)
        return {'FINISHED'}

##################################
class ShapewaysMessagePanel(bpy.types.Operator):
    bl_idname = "shapewayserror.message"
    bl_label = "Message"
    result = StringProperty()
    json = StringProperty()
    modelid = StringProperty()
    spin= StringProperty()
 
    def execute(self, context):
        self.report({'INFO'}, self.json)
        print(self.json)
        return {'FINISHED'}
 
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self, width=500, height=200)
 
    def draw(self, context):
        self.layout.label("A message has arrived")
        row = self.layout.row()
        #row = self.layout.split(0.25)
        row.prop(self, "result")
        row = self.layout.row()
        row.prop(self, "json")
        row = self.layout.row()
        row.prop(self, "modelid")
        row = self.layout.row()
        row.prop(self, "spin")
        row = self.layout.row()
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
    bpy.utils.register_class(ShapewaysSettings)
    bpy.types.Scene.my_tool = PointerProperty(type=ShapewaysSettings)
    bpy.utils.register_class(ShapewaysAPIAddonPreferences)
    bpy.utils.register_class(ShapewaysAPI_GetAccessToken)
    bpy.utils.register_class(ShapewaysToolsPanel)
    bpy.utils.register_class(OpenInBrowser)
    bpy.utils.register_class(Shapeways_ModelInfo)
    bpy.utils.register_class(Shapeways_UploadAction)
    bpy.utils.register_class(ShapewaysMessagePanel)
    bpy.utils.register_class(ShapewaysOkOperator)
    
def unregister():
    bpy.utils.unregister_class(ShapewaysOkOperator)
    bpy.utils.unregister_class(ShapewaysMessagePanel)
    bpy.utils.unregister_class(Shapeways_UploadAction)
    bpy.utils.unregister_class(Shapeways_ModelInfo)
    bpy.utils.unregister_class(OpenInBrowser)
    bpy.utils.unregister_class(ShapewaysToolsPanel)
    bpy.utils.unregister_class(ShapewaysAPI_GetAccessToken)
    bpy.utils.unregister_class(ShapewaysAPIAddonPreferences)
    bpy.utils.unregister_class(ShapewaysSettings)
    del bpy.types.Scene.my_tool

if __name__ == "__main__":
    register()

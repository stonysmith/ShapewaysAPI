import json
import os
import AuthKeys
import requests
from Shapeways import Shapeways
from Tkinter import *
import ttk 

root = Tk()
root.wm_title("Shapeways Shop Manager")
root.iconbitmap('Shapeways.ico')

client=Shapeways(AuthKeys.client_id, AuthKeys.client_secret)
at=client.get_access_token()

def LoadPage(page):
    statusmsg.set("Asking Shapeways for page "+str(page))
    root.update_idletasks()
    t=client.get_models(page)
    statusmsg.set("")
    root.update_idletasks()
    return t

def windowBusy(busy):
    if busy==True:
        state="wait"
    else:
        state=""
    root.config(cursor=state)
    root.update()
    
def InitialLoad():
    lbox.delete(0, END)
    windowBusy(True)
    page=1
    t=LoadPage(page)
    q=t["models"]
    while q :
        for f in q:
            Title=str(f['title'])
            Spin=str(f['modelVersion'])
            ModelNo=str(f['modelId'])
            addItem(Title,Spin,ModelNo)
            lbox.update_idletasks()
        page=page+1
        t=LoadPage(page)
        q=t["models"]
        #q=[]
        statusmsg.set("%d items loaded" % lbox.size())
        for i in range(0,len(ModelIds)-1,2):
            lbox.itemconfigure(i, background='#f0f0ff')
        #root.update_idletasks()
    windowBusy(False)

# Initialize arrays
ModelIds = []
ModelTitles = {}
qerfthings = {}

# State variables
sentmsg = StringVar()
statusmsg = StringVar()

# Called when the selection in the listbox changes;
# Load materials for the box
def showMaterials(*args):
    idxs = lbox.curselection()
    if len(idxs)==1:
        idx = int(idxs[0])
        ModelId = ModelIds[idx]
        statusmsg.set("Model selected:"+str(ModelId))
        materialBox.delete(0, END)
        activeBox.delete(0, END)
        printableBox.delete(0, END)
        totalpriceBox.delete(0, END)
        windowBusy(True)
        rv=client.get_model(ModelId)
        windowBusy(False)
        #print("P=%d,A=%d" % (usePrintable.get(),useActive.get()))
        if rv["result"] <> "failure":
            matdata=rv["materials"]
            for step in matdata.iteritems():
                mats=step[1]
                #print(str(mats))
                debugbox.delete(1.0,END)
                debugbox.insert(1.0,str(mats))
                #for mat in mats.iteritems():
                    #if mat[0]=="name":
                        #m=mat[1]
                show=0
                if str(mats['isPrintable'])=="1" and usePrintable.get()==1:
                    show=1
                if str(mats['isActive'])=="1" and useActive.get()==1:
                    show=1
                if show==1:
                    materialBox.insert(END,str(mats['name']))
                    printableBox.insert(END,str(mats['isPrintable']))
                    activeBox.insert(END,str(mats['isActive']))
                    m=float(mats['markup'])
                    m="%6.2F" % m
                    totalpriceBox.insert(END,m)
        for i in range(0,materialBox.size(),2):
            materialBox.itemconfigure(i, background='#f0f0ff')
            printableBox.itemconfigure(i, background='#f0f0ff')
            activeBox.itemconfigure(i, background='#f0f0ff')
            totalpriceBox.itemconfigure(i, background='#f0f0ff')
    #sentmsg.set('')

def addItem(Title,Spin,ModelNo):
    lbox.insert(END, Title)
    m=str(ModelNo)
    ModelTitles[m]=Title
    qerfthings[m]=ModelNo
    ModelIds.append(m)
    lbox.update_idletasks()

def multiScroll(*args):
    materialBox.yview(*args)
    printableBox.yview(*args)
    activeBox.yview(*args)
    totalpriceBox.yview(*args)

# Create and grid the outer content frame
c = ttk.Frame(root, padding=(5, 5, 12, 0))
c.grid(column=0, row=0, sticky=(N,W,E,S))
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0,weight=1)

# setup main menu
mainmenu = Menu(root)
fileMenu = Menu(mainmenu,tearoff=0)
mainmenu.add_cascade(label="File",menu=fileMenu)
menuitem1 = Menu(fileMenu,tearoff=0)
fileMenu.add_command(label="Load",command=InitialLoad)
fileMenu.add_command(label="Exit",command=root.destroy)

# Create the different widgets; note the variables that many
# of them are bound to, as well as the button callback.
myframe = ttk.Frame(c)
s = Scrollbar(myframe, orient=VERTICAL)
lbox = Listbox(myframe, height=12,width=40)
s.config(command=lbox.yview)
lbox.config(yscrollcommand=s.set)
lbox.grid(row=0, column=0, sticky=(N,S))
s.grid(row=0, column=1, sticky=(N,S))

#Create placeholder for material box
myframe2 = ttk.Frame(c)
s2 = Scrollbar(myframe2, orient=VERTICAL)
materialBox = Listbox(myframe2, height=12,width=30)
printableBox = Listbox(myframe2, height=12,width=3)
activeBox = Listbox(myframe2, height=12,width=3)
totalpriceBox = Listbox(myframe2, height=12,width=10)
#
s2.config(command=multiScroll)
materialBox.config(yscrollcommand=s2.set)
printableBox.config(yscrollcommand=s2.set)
activeBox.config(yscrollcommand=s2.set)
totalpriceBox.config(yscrollcommand=s2.set)
#
materialBox.grid(row=0, column=1, sticky=(N,S))
printableBox.grid(row=0, column=2, sticky=(N,S))
activeBox.grid(row=0, column=3, sticky=(N,S))
totalpriceBox.grid(row=0, column=4, sticky=(N,S))
#
s2.grid(row=0, column=5, sticky=(N,S))

useActive=IntVar()
useActive.set(1)
usePrintable=IntVar()
lbl = ttk.Label(c, text="Choices:")
g1 = ttk.Checkbutton(c, text="Active",variable=useActive,onvalue = 1, offvalue = 0,)
g2 = ttk.Checkbutton(c, text="Printable",variable=usePrintable,onvalue = 1, offvalue = 0,)
g3 = ttk.Checkbutton(c, text="Gaff")
status = ttk.Label(c, textvariable=statusmsg, anchor=W)
debugbox=Text(root,height=3,width=75)

# Grid all the widgets

myframe.grid(column=0, row=0, rowspan=4, sticky=(N,S,E,W))
myframe2.grid(column=1, row=0, rowspan=4, sticky=(N,S,E,W))
#debugbox.grid(column=0,row=5, sticky=W)
lbl.grid(column=2, row=0, padx=10, pady=5)
g1.grid(column=2, row=1, sticky=W, padx=20)
g2.grid(column=2, row=2, sticky=W, padx=20)
g3.grid(column=2, row=3, sticky=W, padx=20)
#load.grid(column=2, row=4, sticky=E)
#send.grid(column=3, row=4, sticky=E)
#sentlbl.grid(column=2, row=5, columnspan=2, sticky=N, pady=5, padx=5)
status.grid(column=0, row=6, columnspan=2, sticky=(W,E))
c.grid_columnconfigure(0, weight=1)
c.grid_rowconfigure(5, weight=1)
root.configure(menu=mainmenu)

# Set event bindings for when the selection in the listbox changes,
# when the user double clicks the list, and when they hit the Return key
lbox.bind('<<ListboxSelect>>', showMaterials)
lbox.bind('<Double-1>', addItem)

# Colorize alternating lines of the listbox
for i in range(0,len(ModelIds),2):
    lbox.itemconfigure(i, background='#f0f0ff')

# Set the starting state of the interface
sentmsg.set('')
statusmsg.set('Click File/Load to begin')
lbox.selection_set(0)
showMaterials()

root.mainloop()

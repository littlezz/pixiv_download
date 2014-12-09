import tkinter
from tkinter import *
from tkinter import ttk
import main_pixiv
def run(*arg):
    Url=getUrl.get()
    print(Url)
    root.destroy()
    main_pixiv.main(Url)
    
root=Tk()
root.title("pixiv Download")
mainframe=ttk.Frame(root,padding="3 3 12 12")
mainframe.grid(column=0,row=0,sticky=(N,W,E,S))
mainframe.columnconfigure(0,weight=1)
mainframe.rowconfigure(0,weight=1)

getUrl=StringVar()
getUrl_entry=ttk.Entry(mainframe,width=70,textvariable=getUrl)
getUrl_entry.grid(column=0,row=1,sticky=(S,E))

ttk.Button(mainframe,text="download",command=run).grid(column=3,row=1,sticky=W)

getUrl_entry.focus()

root.mainloop()



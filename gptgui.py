'''
code file: gptgui.py
date: 1-31-2023
'''
import os
import configparser
from tkinter.font import Font
from tkinter import messagebox
import subprocess
from ttkbootstrap import *
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
import datetime
import openai

PY = "python3"  # Linux
# PY = "pythonw"  # Windows

class Application(Frame):
    ''' main class docstring '''
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.pack(fill=BOTH, expand=True, padx=4, pady=4)
        self.Saved = True
        self.create_widgets()

    def create_widgets(self):
        ''' creates GUI for app '''
        # expand widget to fill the grid
        self.columnconfigure(1, weight=1, pad=5)
        self.columnconfigure(2, weight=1, pad=5)
        self.rowconfigure(2, weight=1, pad=5)

        self.query = Text(self)
        self.query.grid(row=1, column=1, columnspan=2, sticky='nsew')
        efont = Font(family=MyFntQryF, size=MyFntQryZ)
        self.query.configure(font=efont)
        self.query.config(wrap="word", # wrap=NONE
                          undo=True, # Tk 8.4
                          width=50,
                          height=5,
                          padx=5, # inner margin
                          #insertbackground='#000',   # cursor color
                          tabs=(efont.measure(' ' * 4),))

        self.scrolly = Scrollbar(self, orient=VERTICAL,
                                 command=self.query.yview)
        self.scrolly.grid(row=1, column=3, sticky='ns')  # use nse
        self.query['yscrollcommand'] = self.scrolly.set

        self.txt = Text(self)
        self.txt.grid(row=2, column=1, columnspan=2, sticky='nsew')
        efont = Font(family=MyFntGptF, size=MyFntGptZ)
        self.txt.configure(font=efont)
        self.txt.config(wrap="word", # wrap=NONE
                        undo=True, # Tk 8.4
                        width=50,
                        height=12,
                        padx=5, # inner margin
                        #insertbackground='#000',   # cursor color
                        tabs=(efont.measure(' ' * 4),))

        self.scrolly = Scrollbar(self, orient=VERTICAL, command=self.txt.yview)
        self.scrolly.grid(row=2, column=3, sticky='ns')  # use nse
        self.txt['yscrollcommand'] = self.scrolly.set

        # BUTTON FRAME
        btn_frame = Frame(self)
        btn_frame.grid(row=4, column=1, sticky='w')

        clear = Button(btn_frame, text='Clear', command=self.on_clear_all)
        clear.grid(row=1, column=2, sticky='w',
                   pady=(5, 0), padx=(5, 7))
        self.save = Button(btn_frame, text='Save', command=self.on_save_file)
        self.save.grid(row=1, column=3, sticky='w',
                   pady=(5, 0), padx=5)
        view = Button(btn_frame, text='View', command=self.on_view_file)
        view.grid(row=1, column=4, sticky='w',
                   pady=(5, 0))
        purge = Button(btn_frame, text='Purge', command=self.on_purge)
        purge.grid(row=1, column=5, sticky='w',
                   pady=(5, 0), padx=5)
        opts = Button(btn_frame, text='Options', command=self.options)
        opts.grid(row=1, column=6, sticky='w',
                   pady=(5, 0), padx=5)
        self.sub = Button(btn_frame,
                     text='Submit Query',
                     command=self.on_submit, width=35)
        self.sub.grid(row=1, column=7, sticky='w',
                   pady=(5, 0), padx=(20, 0))

       # END BUTTON FRAME

        cls = Button(self, text='Close', command=save_location)
        cls.grid(row=4, column=2, columnspan=2, sticky='e',
                 pady=(5,0), padx=5)

        # Bindings
        root.bind("<Control-k>", self.options)
        root.bind("<Control-q>", save_location)  # Quit program

        # ToolTips
        ToolTip(self.query,
                text="Type your query here. Then hit 'Submit Query",
                bootstyle=(INFO))
        ToolTip(purge,
                text="Remove all saved query responses",
                bootstyle=(INFO))

        self.query.focus_set()

#----------------------------------------------------------------------

    def on_submit(self, e=None):
        ''' Query OpenAI Gpt engine and display response in Text widgit'''
        querytext = self.query.get("1.0", END)
        if len(querytext) < 4:
            return
        self.save.configure(bootstyle=DEFAULT) # new - not been saved
        self.Saved = False
        # get the Gpt key from the ini value
        try:
            openai.api_key = MyKey
        except Exception as e:
            messagebox.showerror("Could Not Read Key file",
                       "Did you enter your Gpt Key?")
            return
        # may take some time
        # things are locked up until response returns
        try:
            response = openai.Completion.create(
            model=MyModel,
            prompt=querytext.strip(),
            temperature=float(MyTemp),
            max_tokens=int(MyTokens),
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0)
            # display Gpt response in Text widget
            output = response["choices"][0]["text"]
            self.txt.delete("1.0", END)
            self.txt.insert("1.0", output)
        except Exception as e:
            messagebox.showerror("Problems", e)

    def on_purge(self):
        ''' User is purging the query-save file '''
        if not os.path.isfile(MyPath):
            messagebox.showwarning(MyPath, "Empty - No File to purge")
            return
        ret = messagebox.askokcancel("Purge", "Delete All Saved Queries?")
        if ret is True:
            os.remove(MyPath)
            messagebox.showinfo("Purge", "Saved Queries Deleted.")


    def on_clear_all(self):
        ''' User is clearning the GUI fields '''
        if self.Saved is False:
            if messagebox.askokcancel('GptGUI',
                                      'Last response not saved - continue?') is False:
                return

        self.txt.delete("1.0", END)
        self.query.delete("1.0", END)
        self.save.configure(bootstyle=DEFAULT) # new - not been saved
        self.Saved = True


    def on_save_file(self):
        ''' Save the current query and result to user file (MyPath) '''
        resp = self.txt.get("1.0", END).strip()
        qury = self.query.get("1.0", END).strip()
        if qury == "" or resp == "":  # make sure there is a query present
            return
        try:
            with open(MyPath, "a") as fout:
                fout.write(str(now.strftime("%Y-%m-%d %H:%M\n")))
                fout.write(qury + "\n-----\n")
                fout.write(resp.strip() + "\n----------------\n\n")
        except Exception as e:
            messagebox.showerror("Save Query Problem", e)
        # indicate that a "save" has processed
        self.save.configure(bootstyle="default-outline")
        self.Saved = True


    def on_view_file(self):
        ''' View the user saved queries file '''
        if not os.path.isfile(MyPath):
            messagebox.showwarning(MyPath, "Empty - No File")
            return
        if self.Saved is False:
            if messagebox.askokcancel('GptGUI',
                                      'Last response not saved - continue?') is False:
                return
        # self.Saved = True
        # self.save.configure(bootstyle=DEFAULT)
        self.txt.delete("1.0", END)
        with open(MyPath, "r") as fin:
            self.txt.insert("1.0", fin.read())
        self.query.delete("1.0", END)


    def options(self):
        # os.system("python3 gptopt.py") # not work well with Windows
        subprocess.Popen([PY, "gptopt.py"])


# SAVE GEOMETRY INFO AND EXIT
def save_location(e=None):
    ''' executes at WM_DELETE_WINDOW event - see below '''
    if messagebox.askokcancel('GptGUI',
                           'Did you want to close the app?') is False:
        return
    with open("winfo", "w") as fout:
        fout.write(root.geometry())
    root.destroy()

# used for saving queries with date and time
now = datetime.datetime.now()

# get settings from ini file
config = configparser.ConfigParser()
config.read('gptgui.ini')

MyTheme = config['Main']['theme']
MyPath = config['Main']['path']
MyFntQryF = config['Main']['fontqryfam']
MyFntQryZ = config['Main']['fontqrysiz']
MyFntGptF = config['Main']['fontgptfam']
MyFntGptZ = config['Main']['fontgptsiz']
MyModel = config['Main']['engine']
MyTemp = config['Main']['temperature']
MyTokens = config['Main']['tokens']
MyKey = config['Main']['gptkey']  # can be actual key or ENV var.
if len(MyKey) < 16:
    MyKey = os.environ.get(MyKey)  # Using ENV var instead of actual key string.

# define main window
root = Window("GptGUI (OpenAI)", MyTheme, iconphoto="icon.png")

# change working directory to path for this file
p = os.path.realpath(__file__)
os.chdir(os.path.dirname(p))

# ACCESS GEOMETRY INFO
if os.path.isfile("winfo"):
    with open("winfo") as f:
        lcoor = f.read()
    root.geometry(lcoor.strip())
else:
    root.geometry("675x505") # WxH+left+top

root.protocol("WM_DELETE_WINDOW", save_location)  # TO SAVE GEOMETRY INFO
root.minsize(768, 325)  # width, height
Sizegrip(root).place(rely=1.0, relx=1.0, x=0, y=0, anchor='se')

Application(root)

root.mainloop()

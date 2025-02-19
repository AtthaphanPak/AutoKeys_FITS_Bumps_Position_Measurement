import os
import glob
import time
import FITS_PY
import configparser
import tkinter as tk
from datetime import datetime
from tkinter import simpledialog, messagebox

def askAccount():
    ask_en = "xx"
    while (len(ask_en) != 6):
        ask_en = simpledialog.askstring("Question", "Enter your EN: ")
        if ask_en is None:
            messagebox.showerror("quit", "User Cancel")
            quit()
    return ask_en

def Convert_Data(array_value):
        pack_value = ";".join(array_value)
        return pack_value
    
if __name__ == "__main__":
    # Read parameters from config files
    config = configparser.ConfigParser()
    try:
        config.read("C:\Projects\AutoKeys_FITS_Bumps_Position_Measurement\Properties\config.ini")
        path = config["DEFAULT"]["file_path"]
        model = config["DEFAULT"]["model"]
        operation = config["DEFAULT"]["operation"]
        fileExtensions = config["DEFAULT"]["extensions"]
    except Exception as e:
        print(f"{e}\nPlease check config.ini")
        quit()
        
    Arhfile = os.path.join(path, "Arh")
    logfailfile = os.path.join(path, "LOGERROR")
    handfailfile = os.path.join(path, "HANDFAIL")   
    os.makedirs(Arhfile, exist_ok=True)
    os.makedirs(logfailfile, exist_ok=True)
    os.makedirs(handfailfile, exist_ok=True)
    
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    en = askAccount()
    while True:
        allfiles = glob.glob(os.path.join(path, fileExtensions))

        for f in allfiles:
            datenow = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
            base_name, extension = os.path.splitext(os.path.basename(f))
            serial = base_name[:22]
            newname = f"{serial}_{datenow}{extension}"
            FITSHandcheck = FITS_PY.Handshake(model, operation, serial)
            if FITSHandcheck != True:
                messagebox.showerror("FITS MESSAGE", f"Serial: {serial} Please Check Operation in FITS")
                print(f"--- FITS HANDCHECK ERROR ---")
                print(f"Path: {f}")
                print(FITSHandcheck)
                print(f"----------------------------")
                os.rename(f, os.path.join(handfailfile, newname))
                continue
            
            listparameters = {
                "EN" : en,
                "SN RCVR" : serial,
                "Test Report" : f,
                "File Name" : str(f),
                "Result" : "PASS"
            }

            parameters = Convert_Data(listparameters.keys())
            values = Convert_Data(listparameters.items())
            FITSLog = FITS_PY.Log(model, operation, parameters, values)
            if FITSLog == True:
                os.rename(f, os.path.join(Arhfile, newname))
                print(f"Serial: {serial} Push to FITs Successfully")
            else:
                messagebox.showerror("FITS MESSAGE", f"Serial: {serial} Please Check Log File")
                print(f"--- FITS LOG ERROR ---")
                print(f"Path: {f}")
                print(FITSLog)
                print(f"----------------------")
                os.rename(f, os.path.join(logfailfile, newname))
                
        print("Wait to Process...")        
        time.sleep(30)
        
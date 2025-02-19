from win32com.client import Dispatch 
from datetime import datetime
import glob
import re
import os

def Handshake(model: str, operation: str, serial: str):
    lib = Dispatch("FITSDLL.clsDB") 

    fn_initDB = lib.fn_initDB(f"{model}",f"{operation}","2.10","dbLuminar")
    if fn_initDB == "True":
        fn_handshake = lib.fn_handshake(f"{model}",f"{operation}","2.10",f"{serial}")
        if fn_handshake == "True":
            return True
        else:
            return FitsDebugging()
    else:
        return FitsDebugging()

def Log(model: str, operation: str, parameters: str, values: str):
    list_parameters = {}
    lib = Dispatch("FITSDLL.clsDB")
    ## Define Shift 
    start_day_shift = datetime.strptime("07:00","%H:%M").time()
    end_day_shift = datetime.strptime("19:00","%H:%M").time()
    if start_day_shift <= datetime.now().time() <= end_day_shift:
        list_parameters["Shift"] = "DAY"
    else:
        list_parameters["Shift"] = "NIGHT"
        
    list_parameters["MC"] = os.environ['COMPUTERNAME']
    
    parameters = parameters + ";" + "Shift" + ";" + "MC"
    values =  values + ";" + list_parameters["Shift"] + ";" + list_parameters["MC"]
    
    fn_initDB = lib.fn_initDB(f"{model}",f"{operation}","2.10","dbLuminar")
    if fn_initDB == "True":
        fn_log = lib.fn_log(f"{model}",f"{operation}","2.10",f"{parameters}",f"{values}",";")
        if fn_log == "True":
            return True
        else:
            
            return FitsDebugging()
    else:
        
        return FitsDebugging()

def Query(model: str, query_operation: str, serial: str, query_parameters: str):
    lib = Dispatch("FITSDLL.clsDB")
    query_array = []

    fn_initDB = lib.fn_initDB(f"{model}",f"{query_operation}","2.10","dbLuminar")
    if fn_initDB == "True":
        for param in query_parameters.split(';'):
            fn_query = lib.fn_query(f"{model}",f"{query_operation}","2.10",f"{serial}",f"{param}",";")
            fn_query = str(fn_query)
            query_values = fn_query.replace("-;","").replace(";-","").replace("-","")
            query_array.append(query_values)
        query_result = ";".join(query_array)
        return query_result
    else:
        
        return FitsDebugging()
    
def FitsDebugging():
    FitsLog_Dir = "C:\\TEMP\\FITSDLL_LOG\\*.log"
    datetime_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
    newest_datetime = None
    newest_log = None

    files = glob.glob(FitsLog_Dir)
    max_file = max(files, key=os.path.getctime)
    with open(max_file, "r") as read_log:
        for line in read_log:
            match = re.search(datetime_pattern, line)
            if match:
                current_datetime = datetime.strptime(match.group(), "%Y-%m-%d %H:%M:%S")
                
                if newest_datetime is None or current_datetime > newest_datetime:
                    newest_datetime = current_datetime
                    newest_log = line

    if newest_datetime:
        # print("Newest Log:\t", newest_log)
        output = "ERROR: ",newest_log.split("\n")[0]
    else:
        # print("No valid log")
        output = "ERROR: ","No valid log"

    return output
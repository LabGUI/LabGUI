import time
import os

def open_therm_file():
    try:
    	config_file = open("config.txt")
    except IOError as e:
    	print("No configuration file found")
          
    #therm_path = "C:/Users/Shared/data/2012/therm/"
    
    for line in config_file:
        [left,right] = line.split("=")
        left = left.strip()
        right = right.strip()
        if left == "COOLDOWN":
            cooldown = right
            print("cooldown " + cooldown)
        elif left == "SAMPLE":	
            sample_name = right
            print("sample " + sample_name)
        elif left == "THERM_PATH":
            therm_path = right
        elif left == "DATA_PATH":
            data_path = right
        
    out_file_name = therm_path + "therm_"+cooldown+"_"+time.strftime("%m%d")
    
    n = 1
    while os.path.exists(out_file_name + ".%3.3d"%n):
        n +=1
      
    out_file_name = out_file_name + ".%3.3d"%n
    print("output file: " + out_file_name)
    
    config_file.close()
    output_file = open(out_file_name,'w')

    return output_file

def open_data_file():
    try:
    	config_file = open("config.txt")
    except IOError as e:
    	print("No configuration file found")
    
    for line in config_file:
    	[left,right] = line.split("=")
    	left = left.strip()
    	right = right.strip()
    	if left == "COOLDOWN":
    		cooldown = right
    		print("cooldown " + cooldown)
    	elif left == "SAMPLE":	
    		sample_name = right
    		print("sample " + sample_name)
    
    data_path = "C:/Users/Shared/data/2012/adiabatic/"
    out_file_name = data_path + sample_name + "_"+cooldown+"_"+time.strftime("%m%d")
    
    n = 1
    while os.path.exists(out_file_name + ".%3.3d"%n):
    	n +=1
 
    out_file_name = out_file_name + ".%3.3d"%n
    print("output file: " + out_file_name)
    
    config_file.close()
    output_file = open(out_file_name,'w')
    return output_file
    
def get_debug_setting():
    try:
    	config_file = open("config.txt")
    except IOError as e:
    	print("No configuration file found")
    
    for line in config_file:
        [left,right] = line.split("=")
        if left.strip() == "DEBUG":
             setting = (right.strip().lower() == 'true')
             
             print("debug: " + str(setting))
             config_file.close()         
             return setting
    
    print ("debug setting not found, reverting to false")
    config_file.close()
    return False   
    
def get_msg_info():
    msg = {}
    
    try:
    	config_file = open("config.txt")
    except IOError as e:
    	print("No configuration file found")
    
    for line in config_file:
        [left,right] = line.split("=")
        if left.strip() == "TO":
             msg['TO'] = right.strip('" \n')
        elif left.strip() == "FROM":
             msg['FROM'] = right.strip('" \n')
        elif left.strip() == "HOST":
             msg['HOST'] = right.strip('" \n')            
    print(("Alerts to be sent to " + msg['TO'] + "when alarm is on"))
    msg['SUBJECT'] = ''
    config_file.close()
    return msg
    
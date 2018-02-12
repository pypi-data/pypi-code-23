# -*- coding: utf-8 -*-
import requests
import pickle

data_url = "http://10.90.33.95:8003/thepack/v1/packdb/download+data/from+file/data"
msg_url = "http://10.90.33.95:8003/thepack/v1/packdb/download+data/from+file/message"
menu_url = "http://10.90.33.95:8003/thepack/v1/packdb/download+data/from+file/menu"
search_url = "http://10.90.33.95:8003/thepack/v1/packdb/download+data/from+file/search"

def _get_registered_files():
    response = requests.post(menu_url, json = {})  

    if not response.ok:
        error_head = get_error_msg_header("fetch('{}')".format("", menu_url))
        error_msg = response.content.decode()
        print(error_head + error_msg)
    else:
        datasets_str = response.content.decode()
    
    return datasets_str.split(",")
    
_registered_datasets = _get_registered_files()
    

def get_error_msg_header(func_name, url):
    msg = "An unexpected error is encountered. please copy below message and send to Chen Bingyou (chenbingyou@gic.com.sg):"
    msg += "\n\n----------------------------------------------------------------------------------\n\n"
    msg += "Hi Bingyou, I encounter error when I use fidatasets.{}.\n".format(func_name)    
    msg += "This error is from endpoint: {}\n".format(url)
    msg += "Detailed error message see below:\n\n"
    return msg

    
def fetch(name):
    if name not in _registered_datasets:
        print ("dataset '{}' is not found. below are available datasets: \n".format(name))
        print (_registered_datasets)
        print("----------------\n\n")
        print("You can use .list_datasets() function to get the list of datasets")
        return None
        
    data_request = {"file_name": name}
    msg_request = {"file_name": name}
    
    data_response = requests.post(data_url, json = data_request)  
    msg_response = requests.post(msg_url, json = msg_request)  
    
    if not data_response.ok:
        error_head = get_error_msg_header("fetch('{}')".format(name), data_url)
        error_msg = data_response.content.decode()
        print(error_head + error_msg)
        return None
    else:
        data = pickle.loads(data_response.content)

    if not msg_response.ok:
        error_head = get_error_msg_header("fetch('{}')".format(name), msg_url)
        error_msg = data_response.content.decode()
        print(error_head + error_msg)
    else:
        msg = msg_response.content.decode()

    print(msg)
    return data
      
    
def list_datasets():
    return _registered_datasets

    
def search(text):
    print("not implemented yet. Can contact Chen Bingyou (chenbingyou@gic.com.sg) if you want this feature to be implemented")
    pass


#print("Available functions:\n.list_datasets(): show all available datasets' name.")
#print(".fetch(dataset_name): download dataset by its name")
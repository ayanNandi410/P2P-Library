import os
from constants import EXTENSION, FORMAT

cwd = os.getcwd()

def convert_to_string(fname):
    file_path = cwd + "/myBooks/" + fname + EXTENSION
    read_data = None
    try:
        with open(file_path, 'r') as file:
            read_data = file.read()
        return read_data
    except Exception as e:
        print("[FILE ERROR] "+repr(e))
        return False


def create_file(data, fname):
    file_path = cwd + "/recBooks/" + fname + EXTENSION
    try:
        with open(file_path, 'w') as file:
            file.write(data)
        return True
    except Exception as e:
        print("[FILE ERROR] "+repr(e))
        return False 
    
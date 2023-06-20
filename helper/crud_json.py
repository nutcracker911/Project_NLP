from variables_and_libs import json

def read_json(path:str) -> None:
    with open(path, "r") as json_file:
        data = json.load(json_file)
    return data

def write_json(data:dict,path:str) -> None:
    with open(path, 'w') as outfile:
        json.dump(data, outfile,ensure_ascii=False,indent=2)
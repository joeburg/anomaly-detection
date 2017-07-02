# python 
import json 

def LoadJsonData(filename):
	with open(filename) as data_file:    
		return json.load(data_file)

def WriteJsonData(filename, json_data):
	with open(filename, 'a') as data_file:
		json.dump(json_data, data_file)

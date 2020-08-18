import json

def load_json(data_file= 'gamedata.json'):
	with open(data_file) as file:
		data = json.load(file)
	return data

def get_sys_config(data_file= "gamedata.json"):
	with open(data_file) as file:
		data = json.load(file)
	
	return data["System"]

def get_config(data_file= "gamedata.json"):
	with open(data_file) as file:
		data = json.load(file)
	
	config= data["Settings"]
	return config

def ch_config(key, new_val):
	try:
		data= load_json()
		data["Settings"][key]["Value"]= new_val
		save_json(data)
	except:
		print("Failed!")
		return -1

def reset_config(data_file= "gamedata.json"):
	with open(data_file) as file:
		data = json.load(file)
	data["Settings"]= data["Factory Data"]["Settings"]
	save_json(data)
	
def get_user_data(user= "Guest", data_file= "gamedata.json"):
	with open(data_file) as file:
		data = json.load(file)
	
	user_data= data["Users"][user]
	return user_data

def update_user_data(key, new_val, user= "Guest"):
	try:
		data= load_json()
		data["Users"][user][key[0]][key[1]]= new_val
		save_json(data)
	except:
		pass

def get_users(data_file= "gamedata.json"):
	with open(data_file) as file:
		data = json.load(file)
	
	users= data["Users"]
	return list(users.keys())

def new_user(name, data_file= "gamedata.json"):
	data= load_json()

	if name not in get_users():
		
		data["Users"][name]= data["Factory Data"]["New User"]
		save_json(data)
	
	else:
		raise Exception("Name taken")

def del_user(name, data_file= "gamedata.json"):
	data= load_json()
	
	del data["Users"][name]
	
	save_json(data)



def get_achievements(achievement_file= "achievements.json"):
	with open(achievement_file) as file:
		achievements= json.load(file)
	return achievements

def save_json(data, data_file= "gamedata.json"):
	try:
		with open(data_file, 'w+') as file:
			json.dump(data, file, indent=4)
		print("Save successful!")
	except:
		print("Failed!")
		return -1
	
def get_curr_user(data_file="gamedata.json"):
	with open(data_file) as file:
		data = json.load(file)
	
	curr_user = data["Current User"]
	return curr_user

def ch_user(user, data_file="gamedata.json"):
	with open(data_file) as file:
		data = json.load(file)
	data["Current User"] = user
	save_json(data)

if __name__ == "__main__":
	new_user("ABC")



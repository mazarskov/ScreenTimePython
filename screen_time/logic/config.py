import os

def create_config_file(config_data=["lang=en"], file_path="config.txt"):
    try:
        with open(file_path, 'w') as config_file:
            for line in config_data:
                config_file.write(line)
            print(f"file created at {file_path}")
    except Exception as e:
        print("error creating file " + e)

def modify_config(new_data=['baka'], file_path="config.txt"):
    if os.path.exists(file_path) != True:
        create_config_file()
    try:
        create_config_file(new_data, file_path)
    except Exception as e:
        print("error creating file " + e)

def get_language(file_path="config.txt"):
    if os.path.exists(file_path) != True:
        create_config_file()
    try:
        with open(file_path, 'r') as config_file:
            for line in config_file:
                line.strip()
                return line.split('=')[1]
    except Exception as e:
        print("error creating file " + e)


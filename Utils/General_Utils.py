import json, os, random

def load_json(name_of_file:str) -> dict:
    '''
    Takes the name of a file and returns the contents of the file as a JSON object.
    args:
        name_of_file (str): The name of the file to load.
    returns:
        dict: The contents of the file as a JSON object.
    '''
    # Get the repo base directory (where this script is located)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    path_to_file = os.path.join(base_dir, "Configs", f"{name_of_file}.json")
    
    with open(path_to_file, 'r') as file:
        return json.load(file)
    
def load_random_avatar() -> bytes:
    """
    Load a random avatar from the avatars directory.
    """
    path = os.path.abspath(os.getenv('AVATAR_PATH'))
    files = os.listdir(path)

    if not files:
        raise FileNotFoundError("No avatar files found in the Avatars directory.")

    file = ""
    while file == "" or not file.endswith(('.png', '.jpg', '.jpeg')):
        file = random.choice(files)
    
    
    
    random_file = os.path.join(path, file)
    
    with open(random_file, 'rb') as f:
        return f.read()

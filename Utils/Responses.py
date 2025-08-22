import random
from Utils.General_Utils import load_json

def pick_good_bot_msg(user_name:str, bot_name:str):
    '''
    Returns a random "good bot" message from the Msg_Responses.json file.
    args:
        user_name (str): The name of the user to replace in the message.
        bot_name (str): The name of the bot to replace in the message.
    returns:
        str: A random "good bot" message with the user and bot names replaced.
    '''

    responses = load_json("Msg_Responses")['good_bot']
    msg = random.choice(responses)
    msg = msg.replace("[USER-NAME]", user_name)
    msg = msg.replace("[BOT-NAME]", bot_name)  

    return msg

def pick_mention_msg(user_name:str, bot_name:str):
    '''
    Returns a random mention message from the Msg_Responses.json file.
    args:
        user_name (str): The name of the user to replace in the message.
        bot_name (str): The name of the bot to replace in the message.
    returns:
        str: A random mention message with the user and bot names replaced.
    '''

    responses = load_json("Msg_Responses")['mention']
    msg = random.choice(responses)
    msg = msg.replace("[USER-NAME]", user_name)
    msg = msg.replace("[BOT-NAME]", bot_name)  

    return msg

def pick_activity():
    '''
    Returns a random activity from the Discord.json file.
    args:

    returns:
        str: A random activity.
    '''
    
    responses = load_json("Discord")['activities']
    activity = random.choice(responses) 

    return activity

def pick_random_msg(msgs:list=[]):
    return random.choice(msgs)
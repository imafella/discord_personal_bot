import discord, asyncio, json
import logging, datetime
from zoneinfo import ZoneInfo
import os, traceback
from dotenv import load_dotenv
import argparse
import random
from Utils import General_Utils as utility
from Utils import Responses as responses
from CommandTrees.Life import Life
from Connections.DB_Connection import DatabaseConnection



#
#Discord bot setup
#
intents = discord.Intents.all()
load_dotenv()
TOKEN = os.getenv("discord_token")
admins = json.loads(os.getenv("ALLOWED_ADMINS","[]"))
ignore_these_user_msgs = json.loads(os.getenv("ignore_user_msgs", "[]"))
ignore_these_user_reactions = json.loads(os.getenv("ignore_user_reactions", "[]"))
MAIN_ID = os.getenv("ID")
TEST_ID = os.getenv("TEST_ID")
BOT_NAME = os.getenv("bot_name", "A Robot")


client = discord.Client(intents=intents)

logging.basicConfig(
	filename="output.log", 
	filemode="w", 
	level=logging.INFO, 
	format="%(asctime)s:%(levelname)s:%(message)s"
)
command_tree = discord.app_commands.CommandTree(client)
db_connection = DatabaseConnection(os.getenv("DB_PATH"))

async def get_guild_channel_by_name(guild:discord.Guild, channel_name:str):
	"""
	Get a channel by name from a guild.
	"""
	for channel in guild.text_channels:
		if channel.name == channel_name:
			return channel
	return guild.system_channel
	# If no channel is found, return the system channel

async def get_random_guild_member(guild:discord.Guild) -> discord.Member:
	"""
	Get a random member from a guild.
	"""
	members = [member for member in guild.members if not member.bot]
	if members:
		return random.choice(members)
	else:
		return None
	# If no members are found, return None

async def has_sent_message_today(channel: discord.TextChannel, search_string: str, client: discord.Client) -> bool:
	now = datetime.datetime.now(ZoneInfo("America/St_Johns"))
	today = now.date()
	async for message in channel.history(limit=800):  # Adjust limit as needed
		if (message.author == client.user or message.author.id in ignore_these_user_msgs) and message.created_at.date() == today:
			# Check plain text content for the search string
			if search_string in message.content :          
				return True
			for embed in message.embeds:
				# Check embed title and description for the search string
				if (embed.title and search_string in embed.title) or (embed.description and search_string in embed.description):
					return True
	return False

#
# Timed things
#

async def change_presense_periodically():
	await client.wait_until_ready()
	while not client.is_closed():
		bot_activity = discord.Game(name=responses.pick_activity())
		await client.change_presence(activity=bot_activity, status=discord.Status.online)
		print(f"Changed presence to: {bot_activity.name}")
		await asyncio.sleep(13 * 60 * 60)  # Change every 13 hours

async def change_avatar_periodically():
	await client.wait_until_ready()
	while not client.is_closed() and str(client.application_id) != TEST_ID:
		await client.user.edit(avatar=utility.load_random_avatar())
		print(f"Changed avatar")
		await asyncio.sleep(14 * 60 * 60)  # Change every 14 hours

#
#Events
#

@client.event
async def on_ready():
	'''
	Starts the whole application
	'''
	life_game = Life(bot=client, database=db_connection)
	try:

		command_tree.add_command(life_game)  # Add the Life command group
		synced_commands = await command_tree.sync()

		print(f"Synced {len(synced_commands)} commands.")
		logging.info("Synced command tree successfully.")
	except discord.HTTPException as e:
		print(f"Failed to sync command tree: {e}")
		logging.error("Failed to sync command tree: %s", e)

	client.loop.create_task(change_presense_periodically())
	client.loop.create_task(change_avatar_periodically())

	print("Hello, I am online!")
	print('Connected to bot: {}'.format(client.user.name))
	print('Bot ID: {}'.format(client.user.id))
	await life_game.start_daily_life_increase_task()

@client.event
async def on_error(event, *args, **kwargs):
	logging.error("An error occurred in event: %s", event)
	logging.error("Error details:\n%s", traceback.format_exc())

@client.event
async def on_message(message:discord.Message):
	'''
	Handles messages sent in the server.
	'''
	username = message.author.mention
	if client.user in message.mentions:
		await message.channel.send(responses.pick_mention_msg(user_name=username, bot_name=BOT_NAME))
	

#
# General Commands
#


@command_tree.command(name="info",description="Info about the bot.")
async def info(interaction: discord.Interaction):
	msg = ""
	for command in command_tree.get_commands():
		msg+= f"\n\n/{command.name} - {command.description}"
	await interaction.response.send_message(content=msg)

@command_tree.command(name="good_bot",description="Tell the bot it's a good bot.")
async def good_bot(interaction: discord.Interaction):
	username = interaction.user.mention
	await interaction.response.send_message(content=responses.pick_good_bot_msg(username, BOT_NAME))


@command_tree.command(name="test",description="Testing the latest code changes that imafella is working on. Don't call this.")
async def test(interaction: discord.Interaction):
	"""
	Test command to check if the bot is working.
	"""
	username = interaction.user.mention
	interaction.response.defer()  # Deferring the response to allow for longer processing time
	

	await interaction.followup.send(content=f"{username}, this is a test command. The bot is working!")

parser = argparse.ArgumentParser(description="Run Bot")
parser.add_argument('--test', action='store_true', help="Run Bot in test mode using the test token")
args = parser.parse_args()

# Decide which token to use
selected_token = TOKEN
#Runs the bot		
client.run(selected_token)
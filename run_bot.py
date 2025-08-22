import discord, asyncio, json
import logging, datetime
from zoneinfo import ZoneInfo
import os, traceback
from dotenv import load_dotenv
import argparse


#
#Discord bot setup
#
intents = discord.Intents.all()
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
Test_TOKEN = os.getenv("DISCORD_TESTING_TOKEN")
admins = json.loads(os.getenv("ALLOWED_ADMINS","[]"))
ignore_these_user_msgs = json.loads(os.getenv("ignore_user_msgs", "[]"))
ignore_these_user_reactions = json.loads(os.getenv("ignore_user_reactions", "[]"))
MAIN_ID = os.getenv("ID")
TEST_ID = os.getenv("TEST_ID")


client = discord.Client(intents=intents)

logging.basicConfig(
	filename="output.log", 
	filemode="w", 
	level=logging.INFO, 
	format="%(asctime)s:%(levelname)s:%(message)s"
)
command_tree = discord.app_commands.CommandTree(client)

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
		bot_activity = discord.Game(name=pickRandomActivity())
		await client.change_presence(activity=bot_activity, status=discord.Status.online)
		print(f"Changed presence to: Playing{bot_activity.name}")
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
	try:
		await command_tree.sync()
	except discord.HTTPException as e:
		print(f"Failed to sync command tree: {e}")
		logging.error("Failed to sync command tree: %s", e)


	print("Hello, I am online!")
	print('Connected to bot: {}'.format(client.user.name))
	print('Bot ID: {}'.format(client.user.id))

@client.event
async def on_error(event, *args, **kwargs):
	logging.error("An error occurred in event: %s", event)
	logging.error("Error details:\n%s", traceback.format_exc())

#
# General Commands
#

@command_tree.command(name="flip",description="Flips the table")
async def flip(interaction: discord.Interaction):
	database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
	await interaction.response.send_message(content=tblFlip())

@command_tree.command(name="info",description="Info about the bot.")
async def info(interaction: discord.Interaction):
	database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
	await interaction.response.send_message(content=giveInfo())

@command_tree.command(name="good_bot",description="Tell the bot it's a good bot.")
async def good_bot(interaction: discord.Interaction):
	database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
	username = interaction.user.mention
	await interaction.response.send_message(content=pickRandomGoodBotResponse(username))


@command_tree.command(name="test",description="Testing the latest code changes that imafella is working on. Don't call this.")
async def test(interaction: discord.Interaction):
	"""
	Test command to check if the bot is working.
	"""
	database.incriment_bot_usage(guild_id=interaction.guild.id, user_id=interaction.user.id)
	username = interaction.user.mention
	interaction.response.defer()  # Deferring the response to allow for longer processing time
	

	await interaction.followup.send(content=f"{username}, this is a test command. The bot is working!")

parser = argparse.ArgumentParser(description="Run Imabot")
parser.add_argument('--test', action='store_true', help="Run Imabot in test mode using the test token")
args = parser.parse_args()

# Decide which token to use
selected_token = Test_TOKEN if args.test else TOKEN
#Runs the bot		
client.run(selected_token)
import discord, json, random, os, asyncio
from dotenv import load_dotenv
from Connections.DB_Connection import DatabaseConnection
from discord.ext import tasks
from datetime import datetime, time, timedelta

class Life(discord.app_commands.Group):
    def __init__(self, bot:discord.Client, database:DatabaseConnection):
        self.bot = bot  # Store the bot instance
        self.database = database
        self.admins = json.loads(os.getenv("ALLOWED_ADMINS","[]"))
        self.target_user = int(os.getenv("life_target_user"), 0)
        self.total = self.database.get_life_total(user_id=self.target_user)
        super().__init__(name="life", description="Life Commands") 
        self.tasks = {}

    

    async def daily_life_increase(self):

        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            print("Checking for daily life increase...")
            now = datetime.now()
            target_time = time(7, 0)  # 7:00 AM
            # If it's 7am (within the current minute)
            if now.time().hour == target_time.hour:
                self.total += 1
                hearts = "❤️" * self.total
                # Fetch the target user and send a message
                target_user = await self.bot.fetch_user(self.target_user)
                await target_user.send(
                            content=f"Good morning! Your life total has increased by 1. Total: {hearts}"
                        )
                for user in self.admins:
                    admin_user = await self.bot.fetch_user(user)
                    await admin_user.send(
                        content=f"Life total for {target_user.name} has been increased to {self.total}."
                    )  
            await asyncio.sleep(60*60) # Check every hour


    async def start_daily_life_increase_task(self):
        await self.bot.wait_until_ready()
        task = asyncio.create_task(self.daily_life_increase())
        self.tasks['daily_life_increase'] = task

    @discord.app_commands.command(name="increase", description="Increase Life total by 1.")
    async def increase(self, interaction: discord.Interaction, reason:str=None, amount:int=1):
        '''
        Increase the life total by 1.
        '''

        # If the user is not an admin, deny access
        if interaction.user.id not in self.admins:
            await interaction.response.send_message(content="You do not have permission to use this command.", ephemeral=True)
            return
        
        await interaction.response.defer()

        self.total += amount 
        hearts = "❤️" * self.total
        self.database.update_life_total(user_id=self.target_user, new_total=self.total)

        target_user = await self.bot.fetch_user(self.target_user)
        await target_user.send(content=f'''
            Your life total has been increased by {amount}. 
            Reason: {reason if reason else 'No reason provided.'}
            Total: {hearts}
            ''')
        await interaction.followup.send(content="\u200b", ephemeral=True)

    @discord.app_commands.command(name="decrease", description="Decrease Life total by 1.")
    async def decrease(self, interaction: discord.Interaction, reason:str=None, amount:int=1):
        '''
        Decrease the life total by 1.
        '''

        # If the user is not an admin, deny access
        if interaction.user.id not in self.admins:
            await interaction.response.send_message(content="You do not have permission to use this command.", ephemeral=True)
            return
        
        await interaction.response.defer()

        self.total -= amount 
        hearts = "❤️" * self.total
        self.database.update_life_total(user_id=self.target_user, new_total=self.total)

        target_user = await self.bot.fetch_user(self.target_user)
        await target_user.send(content=f'''
            Your life total has been decreased by {amount}. 
            Reason: {reason if reason else 'No reason provided.'}
            Total: {hearts}
            ''')

        if self.total <= 0:
            target_user = await self.bot.fetch_user(self.target_user)
            await target_user.send(content=f'''
                You have reached 0 life and have lost the game. Await a reset of your life total to continue playing.
                ''')
            await interaction.user.send(content="The target user has reached 0 life and has lost the game.")
        await interaction.followup.send(content="\u200b", ephemeral=True)

    @discord.app_commands.command(name="set", description="Set Life total to a specific value.")
    async def set(self, interaction: discord.Interaction, reason:str=None, amount:int=1):
        '''
        Set Life total to a specific value.
        '''

        # If the user is not an admin, deny access
        if interaction.user.id not in self.admins:
            await interaction.response.send_message(content="You do not have permission to use this command.", ephemeral=True)
            return
        
        await interaction.response.defer()

        self.total = amount 
        hearts = "❤️" * self.total
        self.database.update_life_total(user_id=self.target_user, new_total=self.total)

        target_user = await self.bot.fetch_user(self.target_user)
        await target_user.send(content=f'''
            Your life total has been set to {amount}. 
            Reason: {reason if reason else 'No reason provided.'}
            Total: {hearts}
            ''')
        await interaction.followup.send(content="\u200b", ephemeral=True)

    @discord.app_commands.command(name="current", description="See the current life total.")
    async def current(self, interaction: discord.Interaction):
        # If the user is not an admin and not the target user, deny access
        if interaction.user.id not in self.admins and not self.target_user:
            await interaction.response.send_message(content="You do not have permission to use this command.", ephemeral=True)
            return

        await interaction.response.defer()
        hearts = "❤️" * self.total
        await interaction.user.send(content=f"Current life total: {hearts}")
        await interaction.followup.send(content="\u200b", ephemeral=True)

    @discord.app_commands.command(name="info", description="Details about the Life module.")
    async def info(self, interaction: discord.Interaction):
        '''
        Provide information about the Life module and its commands.
        '''

        # If the user is not an admin and not the target user, deny access
        if interaction.user.id not in self.admins and not self.target_user:
            await interaction.response.send_message(content="You do not have permission to use this command.", ephemeral=True)
            return
        
        await interaction.response.defer()
        msg = "This module is designed to interact with life game.\n"
        msg+="**Commands:**"
        for command in self.commands:
            msg+= f"\n\n/life {command.name} - {command.description}"
        await interaction.user.send(content=msg)
        await interaction.followup.send(content="\u200b", ephemeral=True)
import discord, json, random, os, asyncio
from dotenv import load_dotenv
from Connections.DB_Connection import DatabaseConnection
from discord.ext import tasks
from datetime import datetime, time, timedelta
from Models.todo_models import Task
from enum import Enum

priority_map = {
    1: "Immediatly",
    2: "Shortly",
    3: "Today",
    4: "This Week",
    5: "This Month",
    6: "At Some Point",
}
map_priority = {
    "Immediatly" :1,
    "Shortly": 2,
    "Today":3,
    "This Week":4,
    "This Month":5,
    "At Some Point":6,
}

class Status(Enum):
    ACTIVE = 0
    INACTIVE = 1

class Todo(discord.app_commands.Group):
    def __init__(self, bot:discord.Client, database:DatabaseConnection):
        self.bot = bot  # Store the bot instance
        self.database = database
        self.admins = json.loads(os.getenv("ALLOWED_ADMINS","[]"))
        self.reminder_frequency = int(os.getenv("reminder_frequency", 1))
        super().__init__(name="todo", description="A little discord todo application") 
        self.async_tasks = {}

    async def send_reminders(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            # Sleep at the start of the loop so that multiple end points can trigger the sleep. DRY.
            await asyncio.sleep(60*60*self.reminder_frequency) # checks every reminder_frequency hours
            
            # If the time is between 11pm and 8 am, skip sending reminders
            current_time = datetime.now().time()
            if current_time >= time(23, 0) or current_time <= time(8, 0):
                continue
            print("Sending Reminders...")
            users = self.database.get_all_users_to_remind()
            for user_id in users:
                user = await self.bot.fetch_user(user_id)
                msg = "Here are your active TODO tasks:\n"
                user_tasks = self.database.get_active_tasks(user_id)
                if not user_tasks or len(user_tasks) == 0:
                    continue
                for task in user_tasks:
                        msg += f"\n**ID:** {task.id} | **Priority:** {priority_map[task.priority]} | **Details:** {task.details} | **Assigned:** {task.assigned_time_stamp}"
                await user.send(
                            content=msg
                        )            
                    
            


    async def start_reminders(self):
        await self.bot.wait_until_ready()
        task = asyncio.create_task(self.send_reminders())
        self.async_tasks['send_reminders'] = task
    
    @discord.app_commands.command(name="create_task", description="Create a new task.")
    @discord.app_commands.choices(priority=[
        discord.app_commands.Choice(name="Immediatly", value=1),
        discord.app_commands.Choice(name="Shortly", value=2),
        discord.app_commands.Choice(name="Today", value=3),
        discord.app_commands.Choice(name="This Week", value=4),
        discord.app_commands.Choice(name="This Month", value=5),
        discord.app_commands.Choice(name="Eventually", value=6)
    ])
    async def create_task(self, interaction: discord.Interaction, task_name:str,user:discord.User=None, priority:discord.app_commands.Choice[int]=None):
        '''
        Creates a new task for the user.
        '''

        await interaction.response.defer()
        
        target_user = interaction.user if user is None else user

        if priority is None:
            task_id = self.database.add_task(user_id=target_user.id, details=task_name)
        else:
            task_id = self.database.add_task(user_id=target_user.id, details=task_name, priority=priority.value)
        
        # Failed to create task
        if task_id is None:
            await interaction.followup.send(content="Failed to create task. Please try again later.", ephemeral=True)
            return
        
        created_task = self.database.get_task_by_id(task_id=task_id, user_id=target_user.id)

        await interaction.followup.send(content="\u200b", ephemeral=True)
        await target_user.send(content=f"Task created:\n{created_task.to_display_string()}")

    @discord.app_commands.command(name="get_tasks", description="Get your active tasks")
    @discord.app_commands.choices(priority=[
        discord.app_commands.Choice(name="Immediatly", value=1),
        discord.app_commands.Choice(name="Shortly", value=2),
        discord.app_commands.Choice(name="Today", value=3),
        discord.app_commands.Choice(name="This Week", value=4),
        discord.app_commands.Choice(name="This Month", value=5),
        discord.app_commands.Choice(name="Eventually", value=6)
    ])
    async def get_tasks(self, interaction: discord.Interaction, priority:discord.app_commands.Choice[int]=None, status:Status=Status.ACTIVE):
        '''
        Gets your tasks.
        '''

        await interaction.response.defer()

        is_checking_archived = status is not None and status == Status.INACTIVE
        if is_checking_archived:
            archived = 1
        else:
            archived = 0
        
        if priority is None:
            if is_checking_archived:
                user_tasks = self.database.get_archived_tasks(user_id=interaction.user.id)
            else: 
                user_tasks = self.database.get_active_tasks(user_id=interaction.user.id)
        else:
            user_tasks = self.database.get_tasks_by_priority(user_id=interaction.user.id, priority=priority.value, status=archived)
        msg = "Here are your active TODO tasks:\n"
        if not user_tasks or len(user_tasks) == 0:
            msg = f"\nYou have no {'in' if status==Status.INACTIVE else ''}active tasks."
        else:
            for task in user_tasks:
                msg += f"\n{task.to_display_string()}"
        await interaction.followup.send(content="\u200b", ephemeral=True)
        await interaction.user.send(content=msg)

    @discord.app_commands.command(name="close_task", description="close a task by its ID.")
    async def close_task(self, interaction: discord.Interaction, task_id:int):
        '''
        Close a task by its ID.
        '''

        await interaction.response.defer()

        # Verify task is real and belongs to user
        task = self.database.get_task_by_id(task_id=task_id, user_id=interaction.user.id)
        if task is None:
            await interaction.followup.send(content="\u200b", ephemeral=True)
            await interaction.user.send(content=f"Task with ID {task_id} not found or not yours.")
            return
        
        self.database.archive_task(task_id=task_id, user_id=interaction.user.id)
        await interaction.followup.send(content="\u200b", ephemeral=True)
        await interaction.user.send(content=f"Congradulations! You have closed the following task:\n{task.id}) {task.details}")
            
    @discord.app_commands.command(name="reopen_task", description="re-open a task by its ID.")
    async def reopen_task(self, interaction: discord.Interaction, task_id:int):
        '''
        reopen a task by its ID.
        '''

        await interaction.response.defer()

        # Verify task is real and belongs to user
        task = self.database.get_task_by_id(task_id=task_id, user_id=interaction.user.id)
        if task is None:
            await interaction.followup.send(content="\u200b", ephemeral=True)
            await interaction.user.send(content=f"Task with ID {task_id} not found or not yours.")
            return
        
        self.database.unarchive_task(task_id=task_id, user_id=interaction.user.id)
        await interaction.followup.send(content="\u200b", ephemeral=True)
        await interaction.user.send(content=f"You have re-opened the following task:\n{task.id}) {task.details}")
           
    @discord.app_commands.command(name="change_task_priority", description="Change the priority of a task by its ID.")
    @discord.app_commands.choices(priority=[
        discord.app_commands.Choice(name="Immediatly", value=1),
        discord.app_commands.Choice(name="Shortly", value=2),
        discord.app_commands.Choice(name="Today", value=3),
        discord.app_commands.Choice(name="This Week", value=4),
        discord.app_commands.Choice(name="This Month", value=5),
        discord.app_commands.Choice(name="Eventually", value=6)
    ])
    async def change_task_priority(self, interaction: discord.Interaction, task_id:int, priority:discord.app_commands.Choice[int]):
        '''
        Change a task's priority by its ID.
        '''

        await interaction.response.defer()

        # Verify task is real and belongs to user
        task = self.database.get_task_by_id(task_id=task_id, user_id=interaction.user.id)
        if task is None:
            await interaction.followup.send(content="\u200b", ephemeral=True)
            await interaction.user.send(content=f"Task with ID {task_id} not found or not yours.")
            return
        
        self.database.update_task_priority(task_id=task_id, new_priority=priority.value, user_id=interaction.user.id)
        await interaction.followup.send(content="\u200b", ephemeral=True)
        await interaction.user.send(content=f"You have changed priority of the following task:\n{task.id}) {task.details} to be {priority.name}")

    @discord.app_commands.command(name="change_task_details", description="Change the details of a task by its ID.")
    async def change_task_details(self, interaction: discord.Interaction, task_id:int, new_details:str):
        '''
        change a tasks details by its ID.
        '''

        await interaction.response.defer()

        # Verify task is real and belongs to user
        task = self.database.get_task_by_id(task_id=task_id, user_id=interaction.user.id)
        if task is None:
            await interaction.followup.send(content="\u200b", ephemeral=True)
            await interaction.user.send(content=f"Task with ID {task_id} not found or not yours.")
            return
        
        self.database.update_task_details(task_id=task_id, new_details=new_details, user_id=interaction.user.id)
        await interaction.followup.send(content="\u200b", ephemeral=True)
        await interaction.user.send(content=f"You have changed details of the following task:\n{task.id}) {task.details} to be {new_details}")

    @discord.app_commands.command(name="get_reminders", description="Subscribe to get reminders")
    async def get_reminders(self, interaction: discord.Interaction):
        '''
        Subscribe to get reminders
        '''

        await interaction.response.defer()
        
        self.database.add_reminder(user_id=interaction.user.id)
        await interaction.followup.send(content="\u200b", ephemeral=True)
        await interaction.user.send(content=f"You will now receive reminders about your active tasks every {self.reminder_frequency} hours.")
    
    @discord.app_commands.command(name="stop_reminders", description="Unsubscribe from reminders")
    async def stop_reminders(self, interaction: discord.Interaction):
        '''
        Unsubscribe from reminders
        '''

        await interaction.response.defer()
        
        self.database.remove_reminder(user_id=interaction.user.id)
        await interaction.followup.send(content="\u200b", ephemeral=True)
        await interaction.user.send(content=f"You will no longer receive reminders about your active tasks.")

 
    @discord.app_commands.command(name="info", description="Details about the todo module.")
    async def info(self, interaction: discord.Interaction):
        '''
        Provide information about the todo module and its commands.
        '''

        await interaction.response.defer()
        msg = "This module is designed to act as a TODO list.\n"
        msg+="**Commands:**"
        for command in self.commands:
            msg+= f"\n\n/todo {command.name} - {command.description}"
        await interaction.followup.send(content=msg, ephemeral=True)
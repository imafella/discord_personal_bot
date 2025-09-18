import sqlite3, threading
from Utils import General_Utils as utility
from Models.todo_models import Task




class DatabaseConnection:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.lock = threading.Lock()
        self.config = utility.load_json("db_config")
        self.setup_database()

    def __del__(self):
        self.close()

    def close(self):
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.connection:
            self.connection.close()
            self.connection = None


    def setup_database(self):
        with self.lock:
            for script in self.config["create"].values():
                self.cursor.execute(script)
            self.connection.commit()

    #
    # Life Queries
    #

    def get_life_total(self, user_id:int) -> int:
        with self.lock:
            self.cursor.execute(self.config['select']['select_life_totals_by_user_id'], (user_id,))
            result = self.cursor.fetchone()
            if result:
                return result[0]
            else:
                self.cursor.execute(self.config['insert']['insert_life_totals_by_user_id_and_total'], (user_id, 5))
                self.connection.commit()
                return 5

    def update_life_total(self, user_id:int, new_total:int):
        with self.lock:
            self.cursor.execute(self.config['update']['update_life_totals_by_user_id'], (new_total, user_id))
            self.connection.commit()

    #
    # Todo Queries
    #

    def get_active_tasks(self, user_id:int) -> list[Task]:
        with self.lock:
            self.cursor.execute(self.config['select']['select_active_tasks_by_user_id'], (user_id,))
            results = self.cursor.fetchall()
            tasks = []
            for row in results:
                task_dict = {
                    "id": row[0],
                    "task_assigned_time_stamp": row[1],
                    "task_details": row[2],
                    "task_priority": row[3],
                    "archived":0
                }
                task = Task()
                task.load_from_dict(task_dict)
                tasks.append(task)
            return tasks
        
    def get_archived_tasks(self, user_id:int) -> list[Task]:
        with self.lock:
            self.cursor.execute(self.config['select']['select_archived_tasks_by_user_id'], (user_id,))
            results = self.cursor.fetchall()
            tasks = []
            for row in results:
                task_dict = {
                    "id": row[0],
                    "task_assigned_time_stamp": row[1],
                    "task_closed_time_stamp": row[2],
                    "task_details": row[3],
                    "task_priority": row[4],
                    "archived":1
                }
                task = Task()
                task.load_from_dict(task_dict)
                tasks.append(task)
            return tasks
        
    def get_task_by_id(self, task_id:int, user_id:int) -> Task|None:
        with self.lock:
            self.cursor.execute(self.config['select']['select_task_by_id'], (task_id,))
            result = self.cursor.fetchone()
            if result:
                task_dict = {
                    "id": result[0],
                    "user_id": result[1],
                    "task_assigned_time_stamp": result[2],
                    "task_closed_time_stamp": result[3],
                    "archived": result[4],
                    "task_details": result[5],
                    "task_priority": result[6]
                }
                task = Task()
                task.load_from_dict(task_dict)
                if task.user_id != user_id: # Prevent access to others tasks
                    return None
                return task
            return None
        
    def get_tasks_by_priority(self, user_id:int, priority:int, status:int=0) -> list[Task]:
        with self.lock:
            if status == 0:
                self.cursor.execute(self.config['select']['select_active_tasks_by_user_id_and_priority'], (user_id, priority))
            else:
                 self.cursor.execute(self.config['select']['select_inactive_tasks_by_user_id_and_priority'], (user_id, priority))
            # 0 = active, 1 = archived
            self.cursor.execute(self.config['select']['select_active_tasks_by_user_id_and_priority'], (user_id, priority))
            results = self.cursor.fetchall()
            tasks = []
            for row in results:
                task_dict = {
                    "id": row[0],
                    "task_assigned_time_stamp": row[1],
                    "task_details": row[2],
                    "task_priority": row[3]
                }
                task = Task()
                task.load_from_dict(task_dict)
                tasks.append(task)
            return tasks
    
    def add_task(self, user_id:int, details:str, priority:int=0) -> int:
        with self.lock:
            if priority in [1,2,3,4, 5, 6]: # In order of importance immediatly, shortly, today, this week, this month, eventually
                self.cursor.execute(self.config['insert']['insert_task_by_user_id_and_task_priority'], (user_id, details, priority))
            else:
                self.cursor.execute(self.config['insert']['insert_task_by_user_id'], (user_id, details))
            self.connection.commit()
            return self.cursor.lastrowid
    
    def update_task_details(self, task_id:int, new_details:str, user_id:int):
        if not self.is_users_task(task_id, user_id):
            return
        with self.lock:
            self.cursor.execute(self.config['update']['update_task_details_by_id'], (new_details, task_id))
            self.connection.commit()

    def update_task_priority(self, task_id:int, new_priority:int, user_id:int):
        if not self.is_users_task(task_id, user_id):
            return
        with self.lock:
            self.cursor.execute(self.config['update']['update_task_priority_by_id'], (new_priority, task_id))
            self.connection.commit()

    def archive_task(self, task_id:int, user_id:int):
        if not self.is_users_task(task_id, user_id):
            return
        with self.lock:
            self.cursor.execute(self.config['update']['archive_task_by_id'], (task_id,))
            self.connection.commit()
    
    def unarchive_task(self, task_id:int, user_id:int):
        if not self.is_users_task(task_id, user_id):
            return
        with self.lock:
            self.cursor.execute(self.config['update']['unarchive_task_by_id'], (task_id,))
            self.connection.commit()

    def delete_task(self, task_id:int, user_id:int):
        if not self.is_users_task(task_id, user_id):
            return
        with self.lock:
            self.cursor.execute(self.config['delete']['delete_task_by_id'], (task_id,))
            self.connection.commit()

    def is_users_task(self, task_id:int, user_id:int) -> bool:
        '''
        Check if the task with task_id belongs to user_id.
        '''
        task = self.get_task_by_id(task_id, user_id)
        return task is not None
    
    #
    # Reminder Queries
    #

    def get_all_users_to_remind(self):
        with self.lock:
            self.cursor.execute(self.config['select']['select_all_reminders'])
            results = self.cursor.fetchall()
            reminders = []
            for row in results:
                reminder_dict = {
                    "id": row[0],
                    "user_id": row[1],
                    "archived": row[2] == 1
                }
                if not reminder_dict["archived"]:
                    reminders.append(reminder_dict["user_id"])
            return reminders
        
    def add_reminder(self, user_id:int):
        with self.lock:
            self.cursor.execute(self.config['select']['select_reminder_by_user_id'], (user_id,))
            result = self.cursor.fetchone()
            if result: # Reminder already exists
                self.cursor.execute(self.config['update']['unarchive_reminder_by_id'], (user_id,))
            else:
                self.cursor.execute(self.config['insert']['insert_reminder_by_user_id'], (user_id,))
            self.connection.commit()
            return self.cursor.lastrowid
        
    def remove_reminder(self, user_id:int):
        with self.lock:
            self.cursor.execute(self.config['update']['archive_reminder_by_id'], (user_id,))
            self.connection.commit()
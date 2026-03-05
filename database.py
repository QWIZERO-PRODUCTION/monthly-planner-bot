import os
from datetime import datetime
from supabase import create_client

class Database:
    def __init__(self):
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_KEY')
        self.client = create_client(self.url, self.key)
    
    def create_user(self, user_id, username):
        try:
            self.client.table('users').insert({'user_id': user_id, 'username': username}).execute()
        except:
            pass
    
    def create_monthly_plan(self, user_id):
        now = datetime.now()
        try:
            self.client.table('monthly_plans').insert({
                'user_id': user_id,
                'year': now.year,
                'month': now.month
            }).execute()
            return True
        except:
            return False
    
    def log_sleep(self, user_id, hours):
        now = datetime.now()
        try:
            self.client.table('sleep_log').insert({
                'user_id': user_id,
                'year': now.year,
                'month': now.month,
                'day': now.day,
                'hours': hours
            }).execute()
            return True
        except:
            return False

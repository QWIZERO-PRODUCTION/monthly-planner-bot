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
            existing = self.client.table('monthly_plans').select('*').eq('user_id', user_id).eq('year', now.year).eq('month', now.month).execute()
            if existing.data and len(existing.data) > 0:
                print(f"План уже существует")
                return False
            result = self.client.table('monthly_plans').insert({'user_id': user_id, 'year': now.year, 'month': now.month}).execute()
            print(f"План создан: {result}")
            return True
        except Exception as e:
            print(f"ОШИБКА: {e}")
            return False
    
    def log_sleep(self, user_id, hours):
        now = datetime.now()
        try:
            self.client.table('sleep_log').insert({'user_id': user_id, 'year': now.year, 'month': now.month, 'day': now.day, 'hours': hours}).execute()
            return True
        except:
            return False

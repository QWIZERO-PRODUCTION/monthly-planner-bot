import os
from supabase import create_client

class Database:
    def __init__(self):
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_KEY')
        
        if not self.url or not self.key:
            raise ValueError("❌ SUPABASE_URL или SUPABASE_KEY не установлены!")
        
        self.client = create_client(self.url, self.key)
    
    def create_user(self, user_id, username):
        try:
            existing = self.client.table('users').select('*').eq('user_id', user_id).execute()
            if existing.data:
                return existing.data[0]
            
            response = self.client.table('users').insert({
                'user_id': user_id,
                'username': username
            }).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"❌ Ошибка создания пользователя: {e}")
            return None
    
    def create_monthly_plan(self, user_id: int, year: int, month: int):
    try:
        # Сначала убедись что пользователь существует
        self.create_user(user_id, "user")
        
        # Проверь есть ли уже план
        response = self.client.table('monthly_plans').select('*').eq('user_id', user_id).eq('year', year).eq('month', month).execute()
        
        if response.data and len(response.data) > 0:
            return None  # План уже существует
        
        # Создать новый план
        new_plan = self.client.table('monthly_plans').insert({
            'user_id': user_id,
            'year': year,
            'month': month
        }).execute()
        
        if new_plan.data and len(new_plan.data) > 0:
            return new_plan.data[0]['plan_id']
        return None
    except Exception as e:
        print(f"Ошибка: {e}")
        return None
            
            return response.data[0]['plan_id'] if response.data else None
        except Exception as e:
            print(f"❌ Ошибка создания плана: {e}")
            return None
    
    def get_current_plan(self, user_id, year, month):
        try:
            response = self.client.table('monthly_plans').select('*').eq('user_id', user_id).eq('year', year).eq('month', month).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"❌ Ошибка получения плана: {e}")
            return None
    
    def create_goal(self, plan_id, user_id, title):
        try:
            response = self.client.table('goals').insert({
                'plan_id': plan_id,
                'user_id': user_id,
                'title': title
            }).execute()
            return response.data[0]['goal_id'] if response.data else None
        except Exception as e:
            print(f"❌ Ошибка создания цели: {e}")
            return None
    
    def get_goals(self, plan_id):
        try:
            response = self.client.table('goals').select('*').eq('plan_id', plan_id).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"❌ Ошибка получения целей: {e}")
            return []
    
    def create_task(self, plan_id, user_id, day, title):
        try:
            response = self.client.table('daily_tasks').insert({
                'plan_id': plan_id,
                'user_id': user_id,
                'day': day,
                'title': title
            }).execute()
            return response.data[0]['task_id'] if response.data else None
        except Exception as e:
            print(f"❌ Ошибка создания задачи: {e}")
            return None
    
    def get_tasks_by_plan(self, plan_id):
        try:
            response = self.client.table('daily_tasks').select('*').eq('plan_id', plan_id).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"❌ Ошибка получения задач: {e}")
            return []
    
    def mark_task_complete(self, task_id):
        try:
            self.client.table('daily_tasks').update({'completed': True}).eq('task_id', task_id).execute()
            return True
        except Exception as e:
            print(f"❌ Ошибка отметки задачи: {e}")
            return False
    
    def log_sleep(self, user_id, year, month, day, hours):
        try:
            existing = self.client.table('sleep_log').select('*').eq('user_id', user_id).eq('year', year).eq('month', month).eq('day', day).execute()
            
            if existing.data:
                self.client.table('sleep_log').update({'hours': hours}).eq('sleep_id', existing.data[0]['sleep_id']).execute()
                return existing.data[0]['sleep_id']
            else:
                response = self.client.table('sleep_log').insert({
                    'user_id': user_id,
                    'year': year,
                    'month': month,
                    'day': day,
                    'hours': hours
                }).execute()
                return response.data[0]['sleep_id'] if response.data else None
        except Exception as e:
            print(f"❌ Ошибка логирования сна: {e}")
            return None
    
    def get_sleep_log(self, user_id, year, month):
        try:
            response = self.client.table('sleep_log').select('*').eq('user_id', user_id).eq('year', year).eq('month', month).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"❌ Ошибка получения логов сна: {e}")
            return []

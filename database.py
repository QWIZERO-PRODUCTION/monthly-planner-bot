def create_monthly_plan(self, user_id):
    now = datetime.now()
    try:
        # Проверь есть ли уже
        existing = self.client.table('monthly_plans').select('*').eq('user_id', user_id).eq('year', now.year).eq('month', now.month).execute()
        
        if existing.data and len(existing.data) > 0:
            print(f"План уже существует для {user_id}")
            return False
        
        # Создай новый
        result = self.client.table('monthly_plans').insert({
            'user_id': user_id,
            'year': now.year,
            'month': now.month
        }).execute()
        
        print(f"План создан: {result}")
        return True
    except Exception as e:
        print(f"ОШИБКА В create_monthly_plan: {e}")
        return False

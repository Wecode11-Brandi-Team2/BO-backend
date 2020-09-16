from sqlalchemy import text

class TestDao:    
    def __init__(self, database):
            self.db = database

    def get_text(self):
        row = self.db.execute(text("""    
            SELECT text
            FROM test
        """)).fetchone()
        return row['text']

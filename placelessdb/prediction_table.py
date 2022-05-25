from .placelessdb.common import insert_table

class Prediction:
    def __init__(self, db_obj):
        self.conn = db_obj
        self.cur = db_obj.cursor()
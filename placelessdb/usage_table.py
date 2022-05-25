from .placelessdb.common import insert_table

class Usage:
    def __init__(self, db_obj):
        self.conn = db_obj
        self.cur = db_obj.cursor()

    def insert(self, cpu, mem, timestamp):
        date = pd.Timestamp(timestamp, unit='s')
        insert_table(self.conn, 'Usage', ('sampel_TS', 'sampel_date', 'cpu', 'memory'),
                                (name, timestamp, date, cpu, mem))
    def get_records(self, num_of_rec, id):

        if num_of_rec == 0:
            query = f""" SELECT * FROM PodUsagAvg where sampel_TS > 
                        (select last_train_TS from Pod where pod_id = {id}) and id = {id}"""
        else:
            query = f"""SELECT * FROM (
                            SELECT * FROM 'PodUsagAvg' where id = {id} ORDER BY 'timestamp' DESC LIMIT {num_of_rec}
                        ) sub
                        ORDER BY id ASC
                        """
        self.cur.execute(query)
        records = self.cur.fetchall()
        rows = [row for row in records]
        return rows

from .placelessdb.common import insert_table

class Residuals:
    def __init__(self, db_obj):
        self.conn = db_obj
        self.cur = db_obj.cursor()

    def insert(self, cpu_error, mem_error, timestamp):
        date = pd.Timestamp(timestamp, unit='s')
        insert_table(self.conn, 'Residuals', ('batch_TS', 'sampel_date', 'cpu_error', 'memory_error'),
                                (timestamp, date, cpu_error, mem_error))


    def get_records(self, num_of_rec,id):
        query =f"""SELECT * FROM (
                        SELECT * FROM 'Residuals' ORDER BY 'sampel_TS' WHEER Residuals.id = {id} DESC LIMIT {'number of records'}
    
                    ) sub
                    ORDER BY id ASC
                    """.format(num_of_rec)
        self.cur.execute(query)
        records = self.cur.fetchall()
        rows = [row for row in records]
        return rows

    def get_above_res_pods(self, res, param): # param = "cpu_MSE" or memory_MSE
        query =f"SELECT id FROM Residuals WHERE {param} >= {res}"
        self.cur.execute(query)
        result_set = self.cur.fetchall()
        result_set = [row for row in result_set]
        return result_set


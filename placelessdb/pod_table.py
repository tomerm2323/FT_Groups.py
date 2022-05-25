from .placelessdb.common import insert_table

class Pod:
    def __init__(self, db_obj):
        self.conn = db_obj
        self.cur = db_obj.cursor()



    def insert(self, name, cpu_limit,cpu_req,mem_limit,mem_req,FT):

        creation_timestamp = time.time()
        creation_date = pd.Timestamp(creation_timestamp, unit='s')
        insert_table(self.db_obj,'Pod', ('pod_id', 'pod_name', 'creation_TS', 'creation_Date', 'CPU_limit',
                                         'memory_limit', 'CPU_request', 'memory_request', 'AWS_FT'),
                     (name, creation_timestamp, creation_date, cpu_limit, mem_limit, cpu_req, mem_req, FT))




    def get_pk_rec(self, pod_name):
        query = "SELECT * From Pod WHERE name = {}".format(pod_name)
        self.cur.execute(query)
        return self.cur.fetchone()

    def update(self, pod_name, name=None,ct=None,cd=None,ccl=None,cml=None,ccr=None,cmr=None,ft=None):
        record = self.get_pk_rec(pod_name)
        input_arr = [name, ct, cd, ccl, cml, ccr, cmr, ft]
        new_record = [input_arr[i] if input_arr[i] is not None else record[i] for i in range(8)]
        query = "UPDATE Pod SET 'name' = {}, 'creation timeStamp' = {},'creation date' = {}" \
                "'current CPU limit' = {}, 'current memory limit' = {}, 'current CPU request' = {}," \
                " 'current memory request' = {}, 'FT' = {}  WHERE 'name' = {}".format(new_record[0], new_record[1],
                                                                                      new_record[2], new_record[3],
                                                                                      new_record[4], new_record[5],
                                                                                      new_record[6], new_record[7],
                                                                                      pod_name)


        self.cur.execute(query)
        self.conn.commit()



    def delete(self, pod_name):
        query = "DELETE FROM 'Pod' WHERE 'name' = {}".format(pod_name)
        self.cur.execute(query)
        self.conn.commit()

    def get_pods_to_train(self, param):
        if param == 'cpu_MSE':
            request = 'CPU_request'
        else:
            request = 'memory_request'
        query = "select pod_id " \
                "from Pod, Residuals on Pod.pod_id = Residuals.id " \
                "where Pod.traied  = TRUE and Pod.last_train_TS <= Residuals.batch_TS " \
                "and Residuals.{}/Pod.{} > 0.05".format(param,request)
        self.cur.execute(query)
        result_set = self.cur.fetchall()
        result_set = [row for row in result_set]
        return result_set







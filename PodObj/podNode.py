from DB import DBQ
import pandas as pd
import placelessdb
from Plog.pylog import PlaceLog
# from  AVL.AVLTree import AVLTree, Node
class Pnode(Node):
    def __init__(self, id, db_password, db_name, host, user, request=()):
        # super(Pnode, self).__init__(id)
        self.id = id
        self.mydb = placelessdb.PDB(host, user, db_password, db_name)
        self.FT = None
        self.cpu_request = request[0]
        self.cpu_limit = 0
        self.mem_request = request[1]
        self.mem_limit = 0
        self.pred_cpu = 0  # list of value and confidence interval [0, []]
        self.pred_mem = 0  # list of value and confidence interval [0, []]
        self.last_cpu_rec = 0
        self.last_mem_rec = 0
        self.cpu_pipe = None
        self.memory_pipe = None
        self.num_of_records = 0
        self.fit = False  # bool for when it's time for a process to fit a model
        self.log = PlaceLog(db_name)



    def insert_db(self,cpu, mem, timestamp,usage=True):
        if usage:
            try:
                self.mydb.usage.insert(cpu,mem,timestamp)
                self.log.info(f'Iesrtion to Usage table went well | DB : {self.log.db}')
            except Exception as message:
                self.log.error(message + f'| DB : {self.log.db} Table : Usage ')
        else:
            try:
                self.mydb.residuals.insert(cpu, mem, timestamp)
                self.log.info(f'Iesrtion to Residuals table went well | DB : {self.log.db}')
            except Exception as message:
                self.log.error(message + f'| DB : {self.log.db} Table : Residuals ')



    def get_history(self, num_of_records, usage=True):
        if usage:
            try:
                data = pd.DataFrame(self.mydb.usage.get_records(num_of_records),
                                    columns=['timestamp', 'date', 'cpu', 'memory'])
                if data is None:
                    self.log.warning(f'DB: {self.log.db}, table: Usage class: Pnode, method: get_history, df is None')
            except Exception as massage:
                self.log.error(f'DB: {self.log.db}, table: Usage class: Pnode, method: get_history, massage: {massage}')
        else:
            try:
                data = pd.DataFrame(self.mydb.residual.get_records(num_of_records),
                                    columns=['timestamp', 'date', 'cpu_error', 'memory_error'])
                if data is None:
                    self.log.warning(f'DB: {self.log.db}, table: Residuals class: Pnode, method: get_history, df is None')
                    raise Exception(f'can not get history from {self.log.db} ')

            except Exception as massage:
                self.log.error(f'DB: {self.log.db}, table: Residuals class: Pnode, method: get_history, massage: {massage}')

        data['date'] = pd.to_datetime(data['date'])
        data.set_index('date', inplace=True)
        return data

    def get_pred(self, param='cpu'):
        if param == 'cpu':
            return self.pred_cpu
        elif param == 'memory':
            return self.pred_mem
        else:
            self.log.warning(f'Someone put a wrong param to mehtod : get_pred, class: Pnode')


    def set_pred(self,value, confidence_interval, param=None):
        if param == 'cpu':
            self.pred_cpu = [value, confidence_interval]
        elif param == 'mem':
            self.pred_mem = [value, confidence_interval]
        else:
            self.log.warning(f'Someone put a wrong param to mehtod : set_pred, class: Pnode')


    def set_limit(self,value, param=None):

        if param == 'cpu':
            self.cpu_limit = value
        elif param == 'mem':
            self.mem_limit = value
        else:
            self.log.warning(f'Someone put a wrong param to mehtod : set_limit, class: Pnode')

    def set_request(self, value, param=None):
        if param == 'cpu':
            self.cpu_request = value
        elif param == 'mem':
            self.mem_request = value
        else:
            self.log.warning(f'Someone put a wrong param to mehtod : set_request, class: Pnode')

    def set_FT(self,val):
        awsft = DBQ.Groups()  # the params is constant and dose not knwon yet.
        ft = awsft.find_group()
        self.FT = ft

    def set_last_cpu(self,cpu):
        self.last_cpu_rec = cpu
    def set_last_memory(self, memory):
        self.last_mem_rec = memory

    def get_last_cpu(self):
        return self.last_cpu_rec

    def get_last_memory(self):
        return self.last_mem_rec
    def kube_update(self):  # execute rest kubernetess servis
        pass

    def get_reqlim(self,cpu_pred, memory_pred):
        return_cpu, return_mem = self.cpu_request, self.mem_request
        cpu, conf_int = cpu_pred
        if self.cpu_request < cpu:
            return_cpu = cpu * 1.05
        elif self.cpu_request * 0.95 > cpu:
            return_cpu = cpu
        mem, conf_int = memory_pred
        if self.mem_request < mem:
            return_mem = mem * 1.05
        elif self.mem_request * 0.95 > mem:
            return_mem = mem
        return [return_cpu, return_cpu * 2, return_mem, return_mem * 2]


    def update_pod(self, FT=None, cpu_request=None, cpu_limit=None, mem_request=None, mem_limit=None,
                   pred_cpu=None, pred_mem=None,last_cpu=None, last_memory=None):
        try:
            param_dic = {0: (self.set_FT, None), 1: (self.set_request,'cpu'), 2: (self.set_limit, 'cpu'),
                         3: (self.set_request, 'memory'), 4: (self.set_limit, 'memory'), 5: (self.set_pred, 'cpu'),
                         6: (self.set_pred,'memory'), 7: (self.set_cpu, None), 8: (self.set_memory, None)}
            params_values = [FT, cpu_request, cpu_limit, mem_request, mem_limit, pred_cpu, pred_mem, last_cpu, last_memory]
            for i in range(len(params_values)):
                if params_values[i] is not None:
                    func = param_dic[i][0]
                    parameter = param_dic[i][1]
                    value = params_values[i]
                    if parameter is not None:
                        func(value, parameter)
                    else:
                        func(value)

        except Exception as message:
            self.log.error(f'pod update has failed! message: {message}')
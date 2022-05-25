from placelessdb import usage_table, pod_table, FT_Groups, residual_table

class PDB:
    def __init__(self, host, user, password, database):
        self.mydb = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
    @property
    def usage(self):
        return usage_table.Usage(self.mydb)

    @property
    def residuals(self):
        return residual_table.Residuals(self.mydb)

    @property
    def pod(self):
        return pod_table.Pod(self.mydb)

    @property
    def FT(self):
        return FT_Groups.Groups(self.mydb)
    @property
    def raw_usage(self):
        return






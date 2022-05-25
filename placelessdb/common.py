def creat_attributes_str(attributes: tuple, creation=True):
    string = '('
    for attribute in attributes:
        if creation:
            string += attribute[0] + ' ' + attribute[1] + ', '
        else:
            string += attribute + ', '
    return string[:-2] + ')'

def get_type_format(num_of_values):
    string = '('
    for _ in range(num_of_values):
        string += '%s, '
    return string[:-2] + ')'

def insert_table(db,table_name, attributes: tuple, values: tuple, many=False):
    attributes_as_str = creat_attributes_str(attributes, creation=False)
    vals_format = get_type_format(len(attributes))
    q_struct = f"INSERT INTO {table_name} {attributes_as_str} VALUES {vals_format}"
    if many:
        db.cursor().executemany(q_struct, values)
    else:
        db.cursor().execute(q_struct, values)

        db.commit()

def get_residuals(db):
    query = "SELECT PodUsagAvg.cpu - Predictions.cpu_pred, PodUsagAvg.memory - Predictions.cpu_pred, PodUsagAvg.TS AS TS," \
            "PodUsagAvg.date,PodUsagAvg.id   FROM Predictions, Pod, PodUsagAvg" \
            "WHERE Pod.trained = Ture and PodUsagAvg.sampel_TS = Predictions.prdicted_date and " \
            "PodUsagAvg.id = Predictions.id" \
            "order by  TS DESC" \
            "LIMIT 12"
    db.cursor().execute(query)
    result_set = db.cursor().fatchall()
    result_set = [row for row in result_set]
    return result_set
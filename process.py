from PodObj.podNode import Pnode
from Plog.pylog import PlaceLog
def extract_json(json_file):
    if type(json_file) is not str:
        myjson = json.dumps(json_file)
    data = json.loads(myjson)
    return data

def get_dictionary():
    pass

def process(json_file):
    samples = extract_json(json_file)
    mydic = get_dictionary()
    for sample in samples.items():
        pod_id = sample[0]
        sample_data = sample[1]  # timestamp, cpu, memory
        timestamp, cpu, memory = sample_data[0], sample_data[1], sample_data[2]
        pod = None
        try:
            pod = mydic[pod_id]
        except:
            pass
        # in case the pod is a new pod do: 1. creat a pod obj. 2. insert obj into AVL. 3. update record in obj's DB.
        # 4. creat a pipeline obj for cpu and memory - don't fit it yet.
        if pod is None:
            request = sample_data[-1]
            pod = Pnode(id, 'user', 'host', 'dbname', 'password', request=request)
            mydic[pod_id] = pod
            pod.insert_db(cpu, memory, timestamp)
            pod.num_of_records += 1
            pod.update_pod(last_cpu=cpu,last_memory=memory)
            pod.log.info(f'New pod obj {pod.id} has created!')
            # pipe1 = TSP()
            # pipe2 = TSP()
            # pipe3 = TSP()
            # pipe1.process_pipline()
            # pipe2.process_pipline()
            # pod.cpu_pipe = pipe1
            # pod.memory_pip = pipe2


        # in case 75 records collected, set the "fit" filed to True so another processes will fit the best model.
        elif pod.num_of_recored > 75 and pod.pred_cpu == 0 and pod.pred_memory == 0:
            pod.insert_db(cpu, memory, timestamp)
            pod.update_pod(last_cpu=cpu,last_memory=memory)
            pod.num_of_records += 1
            pod.fit = True
            pod.log.warning(f'New pod obj {pod.id} need a model fit!')

        #  in case less than 75 record collected, only update
        elif pod.num_of_recored < 75:
            pod.insert_db(cpu, memory, timestamp)
            pod.update_pod(last_cpu=cpu,last_memory=memory)
            pod.num_of_records += 1
            pod.log.info(f'pod obj {pod.id} has tracked and updated!')

        # in case the obj already has a model do: 1. update pipeline. 2. predict for the next lag.
        # 3.update DB. 4. update obj fields
        elif pod.pred_cpu > 0 and pod.pred_memory > 0:
            # update pipeline
            pod.cpu_pipe.update(list(cpu))
            pod.memory_pipe.update(list(memory))
            # update DB
            pod.insert_db(cpu, memory, timestamp)
            pod.insert_db(cpu - pod.get_last_cpu(), memory - pod.get_last_memory(), timestamp, Usage=False)
            pod.num_of_records += 1
            # predict
            cpu_pred = pod.cpu_pipe.get_prediction()
            memory_pred = pod.memory_pipe.get_prediction()
            # update obj fields
            cpu_req, cpu_lim, mem_req, mem_lim = pod.get_reqlim(cpu_pred,memory_pred)
            pod.update_pod(pred_cpu=cpu_pred, pred_mem=memory_pred, last_cpu=cpu, last_memory=memory,
                           cpu_request=cpu_req, cpu_limit=cpu_lim, mem_request=mem_req, mem_limit=mem_lim)
            pod.log.info(f'pod obj {pod.id} has been updated and prediction for next lag giving')
        else:
            pod.log.warning(f'Pod obj {pod.id} did not match any criteria in the process')

def rolling_forcast_test(sampels, pipline):
    pred_list = []
    sse = 0
    for s in sampels:
        pred = pipline.predict(n_periods=1)
        pred_list.append(pred)
        pipline.update(s)
        sse += ((s-pred) ** 2)
    mse = sse/len(sampels)
    test_res = mse < sampels.std()
    return mse, test_res


def set_pipe(param, pod, pipeline):
    if param == 'cpu':
        pod.cpu_pipe = pipeline
    elif param == 'memory':
        pod.memory_pipe = pipeline

def fit_model(pod, param):
    try:
        data = pod.get_history(num_of_records=pod.num_of_records)[param]
        t_size = int(pod.num_of_records * 0.8)
        train, test = model_selection.train_test_split(data, train_size=t_size)
        arima_pipeline = TSP()
        arima_pipeline.fit_data(train)
        mse_arima, arima_test_res =  rolling_forcast_test(test, arima_pipeline)
        if arima_test_res:
            pred, conf_int = pipeline.get_prediction()
            pod.set_pred(pred, conf_int, param=param)
            set_pipe(param, pod, pipeline=arima_pipeline)
            pod.log.info(f'{pod.id} got fitted to an arima model')

        else:
            period = 12  # an hour back
            sarima_pipeline = TSP(seasonal=True, m=period)
            sarima_pipeline.fit_data(train)
            mse_sarima, sarima_test_res = rolling_forcast_test(test, arima_pipeline)
            if sarima_test_res:
                pred, conf_int = sarima_test_res.get_prediction()
                pod.set_pred(pred, conf_int, param=param)
                set_pipe(param, pod, pipeline=sarima_pipeline)
                pod.log.info(f'{pod.id} got fitted to an Sarima model')
            else:
                if mse_arima < mse_sarima:
                    set_pipe(param, pod, pipeline=arima_pipeline)
                else:
                    set_pipe(param, pod, pipeline=sarima_pipeline)
                pod.log.info(f'{pod.id} got fitted but both arima and Sarima tests did not passed')

    except Exception as message:
        pod.log.error(f'{pod.id} model fit failed')























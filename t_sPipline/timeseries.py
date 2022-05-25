import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta
from statsmodels.tsa.stattools import acf, pacf
from statsmodels.tsa.arima_model import ARMA,ARIMA
from time import time
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.seasonal import STL
from pmdarima.arima import auto_arima
from sklearn import MSE
from pmdarima import pipeline
from pmdarima import model_selection
from pmdarima import preprocessing as ppc
import copy
class TSP():
    def __init__(self, seasonal=False,seasonal_period=0):
        self.model_pipe = None
        self.residual_pipe = None
        self.seasonal = seasonal
        self.seasonal_period = seasonal_period
    def adf_test(self, data: list):
        """
        :param data: memory or cpu Series
        :return: bool -> True for stationary an False for not
        """
        adf = adfuller(data)
        p_val = adf[1]
        if p_val <= 0.05:
            return True
        else:
            return False

    def make_stationary(self,data):
        data = copy.deepcopy(data)
        diff_data = data.diff(1)[1:]
        num_of_diff = 1

        while not self.adf_test(diff_data) and num_of_diff < 4:
            diff_data = diff_data.diff(1)[1:]
            num_of_diff += 1
        return num_of_diff

    def process_pipline(self, data):
        stationary = self.adf_test(data)
        default_d = 1
        if stationary:
            default_d -= 1
        else:
             default_d = self.make_stationary(data)

        if self.seasonal:
            model_pipe = pipeline.Pipeline([
                ("arima", arima.AutoARIMA(d=default_d, seasonal=True, stepwise=True, m=self.seasonal_period,
                                          random_state=20, n_fits=20, error_action='ignore'))])
        else:
            model_pipe = pipeline.Pipeline([
                ("arima",  arima.AutoARIMA(d=default_d, seasonal=False, stepwise=True,
                                     random_state=20, n_fits=20, error_action='ignore'))])

        self.model_pipe = model_pipe


    def update_pipline(self, new_data, residual=False):
        if residual:
            self.residual_pipe.update(new_data)
        else:
            self.model_pipe.update(new_data)

    def fit_data(self, train_data, residual=False):
        if residual:
            self.residual_pipe.fit(train_data)
        else:
            self.model_pipe.fit(train_data)

    def get_prediction(self, model=True):
        """
        :return: the predictions and the confidence intervals
        """
        if model:
            return self.model_pipe.predict(n_periods=1, return_conf_int=True)
        else:
            return self.residual_pipe.predict(n_periods=1, return_conf_int=True)












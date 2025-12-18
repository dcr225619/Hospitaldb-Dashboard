# utils/predictions.py

import streamlit as st
import plotly.graph_objects as go
from .database import run_query
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime
from statsmodels.tsa.arima.model import ARIMA
import pmdarima as pm
from statsmodels.tsa.stattools import adfuller
from pmdarima.arima import ADFTest
from pmdarima import auto_arima
from sklearn.metrics import r2_score
from sklearn.linear_model import LinearRegression


from utils.queries import (
    get_hospital_revenue_history
)


def hospital_revenue_prediction():

    revenue = get_hospital_revenue_history()

    hospital_ids = revenue['hospital_id'].unique()

    predictions_dict = {}
    arima_predictions_dict = {}

    for hospital_id in hospital_ids:
        hospital_revenue = revenue[revenue['hospital_id'] == hospital_id].copy()
        hospital_revenue = hospital_revenue.sort_values('year_month')

        if len(hospital_revenue) < 4:
            print(f"No sufficient data for hospital {hospital_id} (4 data points required), skip")
            continue

        ts_data = hospital_revenue['amount'].values

        hospital_revenue['month_num'] = range(len(hospital_revenue))

        # extract feature
        X = hospital_revenue['month_num'].values.reshape(-1, 1)
        y = hospital_revenue['amount'].values


        try:
            # find best lr parameters
            model = LinearRegression()
            model.fit(X, y)

            future_months = np.array([[len(hospital_revenue)],
                                    [len(hospital_revenue) + 1],
                                    [len(hospital_revenue) + 2]])
            future_predictions = model.predict(future_months)

            # store the results
            predictions_dict[hospital_id] = {
                'historical_data': hospital_revenue,
                'model': model,
                'future_predictions': future_predictions,
                'r2_score': model.score(X, y)
            }

        except Exception as e:
            print(f"Linear Model training failed for hospital {hospital_id}: {str(e)}")
            continue

        try:
            # find best arima parameters
            model = auto_arima(
                ts_data,
                start_p=0,
                max_p=5,          # p: autoregressive
                start_d=0,
                max_d=2,          # d: integrated
                start_q=0,
                max_q=5,          # q: moving average
                seasonal=False,
                stepwise=True,
                suppress_warnings=True,
                error_action='ignore'
            )

            optimal_order = model.order

            # Use model.predict to get forecasts and confidence intervals
            forecast_values, forecast_ci = model.predict(n_periods=3, return_conf_int=True, alpha=0.05)

            arima_predictions_dict[hospital_id] = {
                'model': model,
                'optimal_order': optimal_order,
                'aic': model.aic(), # Corrected: Call aic as a method
                'forecast': forecast_values,
                'historical_data': hospital_revenue,
                'conf_int': forecast_ci
            }

        except Exception as e:
            print(f"Arima Model training failed for hospital {hospital_id}: {str(e)}")
            continue


    return arima_predictions_dict, predictions_dict
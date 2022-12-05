# %%
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import OneHotEncoder


# %%
def open_clean_file():
    url = "https://drive.google.com/file/d/1P9wUxzlFcXs_sC0jBGBlcdyP56OMvK7W/view?usp=sharing"
    path = 'https://drive.google.com/uc?export=download&id=' +\
           url.split('/')[-2]
    stops = pd.read_csv(path)
    stops.drop(columns=["GlobalID", "OBJECTID"], inplace=True)
    stops["Month_of_Stop"] = pd.to_datetime(stops.Month_of_Stop)
    stops_ob = stops.select_dtypes(["object"])
    stops[stops_ob.columns] = stops_ob.apply(lambda x: x.str.strip())
    stops_filt = stops[~ stops.Officer_Race.isin(["2 or More",
                       "Not Specified"])].copy()
    stops_filt.drop(stops_filt[stops_filt.Driver_Race ==
                               "Other/Unknown"].index, inplace=True)
    stops_filt.drop(stops_filt[stops_filt.Reason_for_Stop ==
                               "Other"].index, inplace=True)
    stops_filt.dropna(inplace=True)
    stops_filt["Driver_Age"] = pd.cut(stops_filt.Driver_Age,
                                      bins=[0, 25, 35, 55, 200],
                                      labels=["Under 25",
                                              "25 to 34",
                                              "35 to 54",
                                              "55 and older"])
    stops_filt["Officer_Years_of_Service"] =\
        pd.cut(stops_filt.Officer_Years_of_Service,
               bins=[0, 5, 10, 15, 100],
               labels=["Less than 5",
                       "5 to 9",
                       "10 to 15",
                       "Over 15"])
    return stops_filt


# %%
def build_model():
    min_stops = stops_filt[["CMPD_Division",
                            "Driver_Race",
                            "Reason_for_Stop"]].copy()
    min_stops["Target"] = stops_filt["Result_of_Stop"]
    min_stops["Target"] = np.where(min_stops.Target == "Arrest", 1, 0)
    count_class_0, _ = min_stops.Target.value_counts()
    stops_arrest = min_stops[min_stops.Target == 1]
    stops_arrest_over = stops_arrest.sample(int(np.round(count_class_0 * .5)),
                                            replace=True)
    min_stops = pd.concat([min_stops, stops_arrest_over], axis=0)
    dt_X = min_stops.drop(columns="Target")
    dt_y = min_stops["Target"]
    ohedt = OneHotEncoder(handle_unknown="ignore")
    ohedt.fit(dt_X)
    dt_enc_X = ohedt.transform(dt_X).toarray()
    model = DecisionTreeClassifier(criterion="gini", max_depth=14,
                                   random_state=42)
    model.fit(dt_enc_X, dt_y)
    conditions = [list(min_stops[col].unique()) for col in min_stops]
    return model, ohedt, conditions
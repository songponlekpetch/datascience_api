import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn import model_selection
from sklearn.externals import joblib
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix

ASSETS_PATH = 'assets/'

class Predicting:
    def __init__(self, experiment_name, dataframe, col, columns_filter, y_col, user_id):
        self.user_id = user_id
        self.experiment_name = experiment_name
        self.dataframe = dataframe
        self.col = col
        self.y_col = y_col
        self.X = dataframe.loc[:, ].values
        self.columns_filter = columns_filter
        self.filename = '{}{}_{}.sav'.format(ASSETS_PATH, self.user_id, self.experiment_name)

    def decorate_dataframe(self):
        dataframe = self.dataframe
        col = self.col
        y_col = self.y_col
        new_col = list(filter(lambda x : x not in ['id', y_col], col))
        new_col = list(filter(lambda x : x in self.columns_filter, new_col))
        new_dataframe = dataframe[new_col]
        self.dataframe = new_dataframe
        self.X = new_dataframe.loc[:, ].values
        return new_dataframe

    def load_model(self):
        self.fited_model = joblib.load(self.filename)

    def predict(self):
        self.y_pred = self.fited_model.predict(self.X)
        return self.y_pred

    def merge_predict_to_dataframe(self):
        dataframe = self.dataframe
        col = list(dataframe.columns)
        col.append(self.y_col)
        y = pd.Series(self.y_pred)
        dataset = pd.concat([dataframe , y], axis=1)
        dataset.columns = col
        return dataset

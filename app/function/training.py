import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPClassifier
import statsmodels.formula.api as smf

from sklearn import model_selection
from sklearn.externals import joblib

from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn import metrics

ASSETS_PATH = 'assets/'

class Training:
    def __init__(self, experiment_name, dataframe, model_name, model_parameter, columns_filter, y_col, user_id):
        self.user_id = user_id
        self.experiment_name = experiment_name
        self.dataframe = dataframe
        self.model_name = model_name
        self.model_parameter = model_parameter
        self.y_col = y_col
        x_col = tuple(filter(lambda x : x not in ['id', y_col] ,list(dataframe.columns)))
        x_col = tuple(filter(lambda x : x in columns_filter, x_col))
        self.X = dataframe.loc[:, x_col].values
        self.y = dataframe.loc[:, y_col].values
        # x_col = tuple(filter(lambda x : x != 'Class' ,list(dataset.columns)))
        # X = dataset.loc[:, x_col].values
        # y = dataset.loc[:, 'Class'].values

    def train_test(self, test_size = 0.2):
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y, test_size=test_size, random_state=0)

    def arrange_model_parameter(self):
        model_parameter = self.model_parameter
        parameter = {}
        for item in model_parameter:
            name = item['name']
            format_type = item['format']
            if(format_type == 'string'):
                value =  str(item['value']) if item['value'] else None
            elif(format_type == 'int'):
                value = int(item['value']) if item['value'] else None
            elif(format_type == 'boolean'):
                value =  True if item['value'] == 'True' else False
            elif(format_type == 'tuple'):
                value = (int(item['value']),)
            else:
                value = item['value']
            
            parameter[name] = value

        return parameter

    def create_and_fit_model(self):
        model_parameter = self.arrange_model_parameter()
        if self.model_name == 'Decision Tree':
            # self.fited_model = DecisionTreeClassifier(criterion = "gini", random_state = 100,max_depth=3, min_samples_leaf=5)
            self.fited_model = DecisionTreeClassifier(**model_parameter)
            self.fited_model.fit(self.X_train, self.y_train)
        elif self.model_name == 'Linear Regression':
            # self.fited_model = LinearRegression()
            self.fited_model = LinearRegression(**model_parameter)
            self.fited_model.fit(self.X_train, self.y_train)
        elif self.model_name == 'MLP':
            # hidden = 10
            # max_iter = 1000
            # self.fited_model = MLPClassifier(hidden_layer_sizes=(hidden, hidden, hidden), max_iter=max_iter)
            self.fited_model = MLPClassifier(**model_parameter)
            self.fited_model.fit(self.X_train, self.y_train)
        elif self.model_name == 'Multiple Regression':
            self.fited_model = smf.OLS(self.y_train, self.X_train).fit(**model_parameter)
        else:
            pass

    def save_model(self):
        self.filename = '{}{}_{}.sav'.format(ASSETS_PATH, self.user_id ,self.experiment_name)
        print(self.filename)
        joblib.dump(self.fited_model, self.filename)

    def load_model(self):
        self.fited_model = joblib.load(self.filename)

    def predict(self):
        self.y_pred = self.fited_model.predict(self.X_test)
        return self.y_pred

    def cal_score(self):
        if self.model_name == 'Decision Tree':
            return self.cal_score_decision_tree()
        elif self.model_name == 'Linear Regression':
            return self.cal_score_linear_regression()
        elif self.model_name == 'MLP':
            return self.cal_score_mlp()
        elif self.model_name == 'Multiple Regression':
            return self.cal_score_multiple_regression()
        else:
            pass

    def cal_score_decision_tree(self):
        confusion_matrix_df = pd.DataFrame(confusion_matrix(self.y_test, self.y_pred))
        columns = confusion_matrix_df.columns
        columns = [ str(col) for col in columns ]
        confusion_matrix_df.columns = columns
        index = confusion_matrix_df.index
        index = [ str(row) for row in index ]
        confusion_matrix_df.index = index
        confusion_matrix_result = confusion_matrix_df.to_dict()
        return {
            'accuracy_score': accuracy_score(self.y_test, self.y_pred),
            'confusion_matrix': confusion_matrix_result
        }
    def cal_score_linear_regression(self):
        return {
            'mean_absolute_error': metrics.mean_absolute_error(self.y_test, self.y_pred),
            'mean_squared_error': metrics.mean_squared_error(self.y_test, self.y_pred),
            'root_mean_squared_error': np.sqrt(metrics.mean_squared_error(self.y_test, self.y_pred))
        }
    def cal_score_mlp(self):
        confusion_matrix_df = pd.DataFrame(confusion_matrix(self.y_test, self.y_pred))
        print(confusion_matrix_df)
        columns = confusion_matrix_df.columns
        columns = [ str(col) for col in columns ]
        confusion_matrix_df.columns = columns
        index = confusion_matrix_df.index
        index = [ str(row) for row in index ]
        confusion_matrix_df.index = index
        confusion_matrix_result = confusion_matrix_df.to_dict()
        print(confusion_matrix_result)
        return {
            'accuracy_score': accuracy_score(self.y_test, self.y_pred),
            'confusion_matrix': confusion_matrix_result
        }
    def cal_score_multiple_regression(self):
        return {
            'mean_absolute_error': metrics.mean_absolute_error(self.y_test, self.y_pred),
            'mean_squared_error': metrics.mean_squared_error(self.y_test, self.y_pred),
            'root_mean_squared_error': np.sqrt(metrics.mean_squared_error(self.y_test, self.y_pred))
        }

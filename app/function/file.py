import os
import pandas as pd
import numpy as np
from bson.objectid import ObjectId
from models.upload import UploadModel

ASSETS_PATH = 'assets/'

class File:
    def __init__(self, file_id, file_extension):
        self.file_id = file_id
        self.extension = file_extension

    def get_json(self):
        dataset = self.dataset
        raw_dataset = dataset.to_dict()
        columns = dataset.columns.to_list()
        size = dataset.shape[0]
        dataset_json = []
        for row in range(0, size):
            dataset_dict = {}
            for col in columns:
                dataset_dict[col] = raw_dataset[col][row]
            dataset_json.append(dataset_dict)
        return dataset_json

    def get_dataframe(self):
        return self.dataset

    def get_header(self):
        columns = [ { 'name': col } for col in list(self.dataset.columns)]
        return columns

    @classmethod
    def read_json(cls, raw_data):
        dataset = pd.DataFrame(raw_data)
        return dataset

    def read_file_to_dataset(self):
        file = UploadModel.send_file_from_mongo(ObjectId(self.file_id))
        if self.extension in ['csv']:
            dataset = pd.read_csv(file)
        elif self.extension in ['xlsx', 'xls']:
            dataset = pd.read_excel(file)
        else:
            dataset = none
        self.dataset = dataset

    @classmethod
    def pre_read_file_to_dataset(self, file, file_extension):
        if file_extension in ['csv']:
            dataset = pd.read_csv(file)
        elif file_extension in ['xlsx', 'xls']:
            dataset = pd.read_excel(file)
        else:
            dataset = none
        self.dataset = dataset

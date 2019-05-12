class Dataset:
    def __init__(self, dataframe):
        self.dataframe = dataframe

    def get_json(self):
        dataset = self.dataframe
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

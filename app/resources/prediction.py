import werkzeug
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId

from function.file import File
from function.predicting import Predicting
from function.dataset import Dataset
from models.experiment import ExperimentModel
from models.datasource import DatasourceModel
from models.project import ProjectModel, ProjectUnstructureModel


ERROR_BLANK_FIELD = 'This {} field cannot be left blank.'
ERROR_CANNOT_INSERT_DB = 'An error is occur cannot insert data to database'
ERROR_DUPLICATE_NAME = 'An duplicated name error is occur cannot define ({}).'
ERROR_CANNOT_GET_COLUMNS_FILTER_ID = 'An error is occur cannot find COLUMNS FILTER ID({}).'
ERROR_CANNOT_GET_COLUMNS_FILTER = 'An error is occur cannot find COLUMNS FILTER ({}).'
ERROR_CANNOT_GET_PREDICT_WITH_DATA = 'An error is occur. The dataset is not compatible with prediction.'

class Prediction(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('data',
                        type=list,
                        required=True,
                        help=ERROR_BLANK_FIELD.format('data'),
                        location='json'
                        )

    @jwt_required
    def post(self, experiment_name):
        user_id = get_jwt_identity()
        data = Prediction.parser.parse_args()
        raw_data = data['data']
        dataset = File.read_json(raw_data)

        result = ExperimentModel.find_by_name(user_id, experiment_name)
        y_col = result.y_col
        datasource_id = result.datasource_id
        project_id = result.project_id

        result = DatasourceModel.find_one_by_id(user_id, datasource_id)
        user_schema_name = result.user_schema_name
        user_table_name = result.user_table_name
        columns = [col['column_name'] for col in DatasourceModel.get_columns(user_schema_name, user_table_name)]

        try:
            columns_filter_id = ProjectModel.find_one_by_id(project_id, user_id).columns_filter_id
        except Exception as e:
            return {'message': ERROR_CANNOT_GET_COLUMNS_FILTER_ID.format(project_id)}, 500
        
        try:
            columns_filter = ProjectUnstructureModel.find_by_object_id(ObjectId(columns_filter_id))['columns']
        except Exception as e:
            return {'message': ERROR_CANNOT_GET_COLUMNS_FILTER.format(project_id)}, 500
        try:
            predict = Predicting(experiment_name, dataset, columns, columns_filter, y_col, user_id)
            predict.decorate_dataframe()
            predict.load_model()
            predict.predict()
            dataset = predict.merge_predict_to_dataframe()
            json_data = Dataset(dataset).get_json()
        except Exception as e:
            print(e)
            return {'message': ERROR_CANNOT_GET_PREDICT_WITH_DATA.format(experiment_name)}, 500
        # try:
        #     DatasourceModel.append_datasource(dataset, user_schema_name, user_table_name)
        # except Exception as e:
        #     return {'message': ERROR_CANNOT_INSERT_DB}, 500

        return {'data': json_data}, 200

class PrePrediction(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('file_type',
                        type=str,
                        required=True,
                        help=ERROR_BLANK_FIELD.format('file_type'),
                        )
    parser.add_argument('upload_file',
                        type=werkzeug.datastructures.FileStorage,
                        required=True,
                        location='files',
                        )
    @jwt_required
    def post(self, experiment_name):
        user_id = get_jwt_identity()
        data = PrePrediction.parser.parse_args()
        upload_file = data['upload_file']
        file_extension = upload_file.filename.split('.')[1]
        file = File(user_id, file_extension)
        file.pre_read_file_to_dataset(upload_file, file_extension)
        dataset = file.get_json()
        header = file.get_header()
        return {'message': 'sucess' , 'header': header, 'dataset': dataset}, 200

class AddPrediction(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('predicted_data',
                        type=list,
                        required=True,
                        help=ERROR_BLANK_FIELD.format('predicted_data'),
                        location='json'
                        )
                        
    @jwt_required
    def post(self, datasource_name):
        data = AddPrediction.parser.parse_args()
        predicted_data = data['predicted_data']
        datasource = DatasourceModel.find_by_name(datasource_name)
        user_schema_name = datasource.user_schema_name
        user_table_name = datasource.user_table_name
        dataset = File.read_json(predicted_data)
        try:
            DatasourceModel.append_datasource(dataset, user_schema_name, user_table_name)
        except Exception as e:
            return {'message': ERROR_CANNOT_INSERT_DB}, 500
        return {'message': 'This Dataset has append to datasource ({})'.format(datasource_name)}, 200

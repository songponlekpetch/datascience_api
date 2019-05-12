from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId

from models.experiment import ExperimentModel, ExperimentUnstructureModel
from models.viz import VizUnstructureModel
from models.datasource import DatasourceModel
from models.model import ModelModel
from models.project import ProjectModel, ProjectUnstructureModel
from function.training import Training

SUCCESS_MESSAGE = "This {} request has succeed"
ERROR_BLANK_FIELD = 'This {} field cannot be left blank.'
ERROR_CANNOT_INSERT_DB = 'An error is occur. It cannot insert data to database'
ERROR_DUPLICATE_NAME = 'An duplicated name error is occur. It cannot define ({}).'
ERROR_CANNOT_FIND_DATASOURCE_ID = 'An error is occur. It cannot find DATASOURCE_ID ({}).'
ERROR_CANNOT_GET_DATASET = 'An error is occur. It cannot find DATASET ({}).'
ERROR_CANNOT_GET_COLUMNS_FILTER_ID = 'An error is occur. It cannot find COLUMNS FILTER ID({}).'
ERROR_CANNOT_GET_COLUMNS_FILTER = 'An error is occur. It cannot find COLUMNS FILTER ({}).'
ERROR_CANNOT_FIND_MODEL_ID = 'An error is occur. It cannot find MODEL ID ({}).'
ERROR_CANNOT_INSRET_MONGO = 'An error is occur. It cannot insert scoring to mongodb ({}).'
ERROR_CANNOT_INSRET_SCORE = 'An error is occur. It cannot insert scoring id to db ({}).'
ERROR_CANNOT_INSRET_VIZ_TO_MONGO = 'An error is occur. It cannot insert viz to mongodb ({}).'
ERROR_CANNOT_INSRET_VIZ = 'An error is occur. It cannot insert viz id to db ({}).'
ERROR_CANNOT_FIND_EXPERIMENT = 'An error is occur. It cannot find EXPERIMENT ({}).'
ERROR_CANNOT_GET_MODEL_PARAMETER = 'An error is occur. It cannot find MODEL PARAMETER ({}).'
ERROR_CANNOT_TRAIN_MODEL_WITH_DATA = 'An error is occur. The dataset is not compatible with model.'

class Experiment(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('experiment_description',
                        type=str,
                        required=True,
                        help=ERROR_BLANK_FIELD.format('experiment_description')
                        )
    parser.add_argument('datasoruce_id',
                        type=int,
                        required=True,
                        help=ERROR_BLANK_FIELD.format('datasoruce_id')
                        )
    parser.add_argument('model_id',
                        type=int,
                        required=True,
                        help=ERROR_BLANK_FIELD.format('model_id')
                        )
    parser.add_argument('model_parameter',
                        type=list,
                        required=True,
                        help=ERROR_BLANK_FIELD.format('model_parameter'),
                        location='json'
                        )
    parser.add_argument('y_col',
                        type=str,
                        required=True,
                        help=ERROR_BLANK_FIELD.format('y_col')
                        )

    @jwt_required
    def get(self, project_id, experiment_name):
        user_id = get_jwt_identity()
        experiment = ExperimentModel.find_by_experiment_name(user_id, experiment_name)
        datasource = DatasourceModel.find_one_by_id(user_id, experiment.datasource_id)
        data_columns = DatasourceModel.get_columns(datasource.user_schema_name, datasource.user_table_name)
        return  { 'datasource_name': datasource.datasource_name,'header': data_columns}, 200

    @jwt_required
    def post(self, project_id, experiment_name):
        user_id = get_jwt_identity()
        data = Experiment.parser.parse_args()
        experiment_description = data['experiment_description']
        datasource_id = data['datasoruce_id']
        model_id = data['model_id']
        model_parameter = data['model_parameter']
        y_col =data['y_col']

        # --START--Checking retrived data
        experiment = ExperimentModel(experiment_name, experiment_description, datasource_id, model_id, y_col, project_id, user_id)
        if experiment.find_by_name(user_id, experiment_name):
            return {'message': ERROR_DUPLICATE_NAME.format(experiment_name)}, 500

        try:
            result = DatasourceModel.find_one_by_id(user_id, datasource_id)
            datasource_data = {
                'datasource_name': result.datasource_name,
                'datasource_description': result.datasource_description,
                'user_schema_name': result.user_schema_name,
                'user_table_name': result.user_table_name,
                'user_id': str(result.created_at)
            }

        except Exception as e:
            return {'message': ERROR_CANNOT_FIND_DATASOURCE_ID.format(datasource_id)}, 500

        try:
            result = ModelModel.find_first_by_id(model_id)
            model_name = result.model_name

        except Exception as e:
            return {'message': ERROR_CANNOT_FIND_MODEL_ID.format(model_id)}, 500

        # --END--Checking retrived data

        try:
            dataframe = DatasourceModel(**datasource_data).get_datasource()
        except Exception as e:
            return {'message': ERROR_CANNOT_GET_DATASET.format(datasource_data['user_table_name'])}, 500

        try:
            columns_filter_id = ProjectModel.find_one_by_id(project_id, user_id).columns_filter_id
        except Exception as e:
            return {'message': ERROR_CANNOT_GET_COLUMNS_FILTER_ID.format(project_id)}, 500
        
        try:
            columns_filter = ProjectUnstructureModel.find_by_object_id(ObjectId(columns_filter_id))['columns']
        except Exception as e:
            return {'message': ERROR_CANNOT_GET_COLUMNS_FILTER.format(project_id)}, 500

        try:
            training = Training(experiment_name, dataframe, model_name, model_parameter, columns_filter, y_col, user_id)
            training.train_test()
            training.create_and_fit_model()
            training.save_model()
            training.load_model()
            y_pred = training.predict()
            cal_score = training.cal_score()
        except Exception as e:
            print(e)
            return {'message': ERROR_CANNOT_TRAIN_MODEL_WITH_DATA}, 500

        try:
            
            mongo = ExperimentUnstructureModel(cal_score, model_parameter)
            cal_score_id = str(mongo.save_cal_score_to_db())
            model_parameter_id = str(mongo.save_model_parameter_to_db())
        except Exception as e:
            return {'message': ERROR_CANNOT_INSRET_MONGO.format(experiment_name)}, 500

        try:
            experiment.save_to_db()
        except Exception as e:
            return {'message': ERROR_CANNOT_INSERT_DB}, 500

        try:
            result = ExperimentModel.find_by_name(user_id, experiment_name)
            if result:
                result.save_cal_score_to_db(cal_score_id)
                result.save_model_parameter_to_db(model_parameter_id)
        except Exception as e:
            return {'message': ERROR_CANNOT_INSRET_SCORE.format(e)}, 500

        return { 'message': '{} have already trained'.format(experiment_name) }, 200

    @jwt_required   
    def delete(self, project_id, experiment_name):
        user_id = get_jwt_identity()
        try:
            experiment = ExperimentModel.find_by_experiment_name(user_id, experiment_name)
            if experiment:
                experiment.delete_from_db()
                return { 'message': SUCCESS_MESSAGE.format(experiment_name)}, 200
            return { 'message': ERROR_CANNOT_FIND_EXPERIMENT.format(experiment_name)}, 500
        except Exception as e:
            return { 'message': ERROR_CANNOT_FIND_EXPERIMENT.format(experiment_name)}, 500
        
class Experiments(Resource):
    @jwt_required
    def get(self):
        user_id = get_jwt_identity()
        results = ExperimentModel.find_all()
        data = [{ 'experiment_id': row.experiment_id,
                'experiment_name': row.experiment_name,
                'experiment_description': row.experiment_description,
                'cal_score_id': row.cal_score_id,
                'datasource_id': row.datasource_id,
                'model_id': row.model_id,
                'y_col': row.y_col,
                'model_parameter_id': row.model_parameter_id,
                'viz_id': row.viz_id
                } for row in results]
        return {'message': 'list of all experiments', 'data': data}, 200

class ExperimentReLearning(Resource):
    @jwt_required
    def put(self, experiment_id):
        user_id = get_jwt_identity()
        experiment = ExperimentModel.find_by_id(experiment_id)
        try:
            result = DatasourceModel.find_one_by_id(user_id, experiment.datasource_id)
            datasource_data = {
                'datasource_name': result.datasource_name,
                'datasource_description': result.datasource_description,
                'user_schema_name': result.user_schema_name,
                'user_table_name': result.user_table_name,
                'user_id': str(result.created_at)
            }

        except Exception as e:
            return {'message': ERROR_CANNOT_FIND_DATASOURCE_ID.format(experiment.datasource_id)}, 500

        try:
            result = ModelModel.find_first_by_id(experiment.model_id)
            model_name = result.model_name

        except Exception as e:
            return {'message': ERROR_CANNOT_FIND_MODEL_ID.format(experiment.model_id)}, 500

        try:
            dataframe = DatasourceModel(**datasource_data).get_datasource()
        except Exception as e:
            return {'message': ERROR_CANNOT_GET_DATASET.format(datasource_data['user_table_name'])}, 500

        try:
            columns_filter_id = ProjectModel.find_one_by_id(experiment.project_id, user_id).columns_filter_id
        except Exception as e:
            return {'message': ERROR_CANNOT_GET_COLUMNS_FILTER_ID.format(experiment.project_id)}, 500
        
        try:
            columns_filter = ProjectUnstructureModel.find_by_object_id(ObjectId(columns_filter_id))['columns']
        except Exception as e:
            return {'message': ERROR_CANNOT_GET_COLUMNS_FILTER.format(project_id)}, 500

        try:
            model_parameter = ExperimentUnstructureModel.find_model_parameter_by_object_id(ObjectId(experiment.model_parameter_id))['model_parameter']
        except Exception as e:
            return {'message': ERROR_CANNOT_GET_MODEL_PARAMETER.format(experiment.model_parameter_id)}, 500
        
        training = Training(experiment.experiment_name, dataframe, model_name, model_parameter, columns_filter, experiment.y_col)
        training.train_test()
        training.create_and_fit_model()
        training.save_model()
        training.load_model()
        y_pred = training.predict()
        cal_score = training.cal_score()

        try: 
            mongo = ExperimentUnstructureModel(cal_score, model_parameter)
            cal_score_id = str(mongo.save_cal_score_to_db())
        except Exception as e:
            return {'message': ERROR_CANNOT_INSRET_MONGO.format(experiment.experiment_name)}, 500

        try:
            experiment.cal_score_id = cal_score_id
            experiment.save_to_db()
        except Exception as e:
            return {'message': ERROR_CANNOT_INSERT_DB}, 500

        return { 'message': SUCCESS_MESSAGE.format(experiment_id)}, 200

class ExperimentsById(Resource):
    @jwt_required
    def get(self, project_id):
        user_id = get_jwt_identity()
        results = ExperimentModel.find_all_by_id(project_id)
        data = [{ 'experiment_id': row.experiment_id,
                'experiment_name': row.experiment_name,
                'experiment_description': row.experiment_description,
                'cal_score_id': row.cal_score_id,
                'datasource_id': row.datasource_id,
                'datasource_name': DatasourceModel.find_one_by_id(user_id, row.datasource_id).datasource_name,
                'model': {
                    'model_id':row.model_id ,
                    'model_name': ModelModel.find_first_by_id(row.model_id).model_name,
                    'model_type':  ModelModel.find_first_by_id(row.model_id).model_type.model_type_name
                },
                'y_col': row.y_col,
                'model_parameter_id': row.model_parameter_id,
                'viz_id': row.viz_id
                } for row in results]
        return {'message': 'list of all experiments', 'data': data}, 200
    
class ExperimentCalScoreId(Resource):
    @jwt_required
    def get(self, cal_score_id):
        data = ExperimentUnstructureModel.find_by_object_id(ObjectId(cal_score_id))
        del data['_id']
        return {'message': 'list of cal scores', 'data': data}, 200

class ExperimentModelParameter(Resource):
    @jwt_required
    def get(self, model_parameter_id):
        data = ExperimentUnstructureModel.find_model_parameter_by_object_id(ObjectId(model_parameter_id))
        del data['_id']
        return {'message': 'list of model parameters', 'data': data}, 200

class ExperimentViz(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('viz',
                        type=dict,
                        required=True,
                        help=ERROR_BLANK_FIELD.format('viz'),
                        location='json'
                        )
    
    @jwt_required
    def get(self, experiment_name, viz_id):
        data = VizUnstructureModel.find_by_object_id(ObjectId(viz_id))
        del data['_id']
        return {'message': 'this is viz infomation', 'viz': data}, 200

    @jwt_required
    def post(self, experiment_name, viz_id):
        data = ExperimentViz.parser.parse_args()
        viz = data.viz
        try:
            mongo = VizUnstructureModel(viz)
            viz_id = str(mongo.save_viz_to_db())
        except Exception as e:
            return {'message': ERROR_CANNOT_INSRET_VIZ_TO_MONGO.format(experiment_name)}, 500
        try:
            result = ExperimentModel.find_by_name(experiment_name)
            if result:
                result.save_viz_to_db(viz_id)
        except Exception as e:
            return {'message': ERROR_CANNOT_INSRET_VIZ_.format(viz_id)}, 500


        return { 'message': 'This viz have already saved to {}'.format(experiment_name) }, 200

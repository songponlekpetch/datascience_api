from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId

from models.collection import CollectionModel
from models.project import ProjectModel, ProjectUnstructureModel
from models.datasource import DatasourceModel

SUCCESS_MESSAGE = "This {} request has succeed"
ERROR_BLANK_FIELD = 'This {} field cannot be left blank.'
ERROR_CANNOT_INSERT_DB = 'An error is occur cannot insert data to database'
ERROR_CANNOT_INSRET_MONGO = 'An error is occur cannot insert columns filter to mongodb ({}).'
ERROR_DUPLICATE_NAME = 'An duplicated name error is occur cannot define ({}).'
ERROR_CANNOT_INSRET_COLUMNS_FILTER = 'An error is occur cannot insert columns filter to db ({}).'

class Project(Resource):
    @jwt_required
    def get(self, project_id):
        user_id = get_jwt_identity()
        data = ProjectModel.find_one_by_id(project_id, user_id)
        collection = CollectionModel.find_one_by_id(data.collection_id, user_id)
        datasource = DatasourceModel.find_one_by_id(user_id, data.datasource_id)
        return {
            'project_id': data.project_id,
            'project_name': data.project_name,
            'project_description': data.project_description,
            'datasource': {
                'datasource_id': datasource.datasource_id,
                'datasource_name': datasource.datasource_name,
                'datasource_description': datasource.datasource_description
            },
            'collection': {
                'collection_id': collection.collection_id,
                'collection_name': collection.collection_name,
                'collection_description': collection.collection_description,
            }
        }
    
    @jwt_required
    def delete(self, project_id):
        user_id = get_jwt_identity()
        try:
            project = ProjectModel.find_one_by_id(project_id, user_id)
            project.delete_from_db()
            return { 'message': SUCCESS_MESSAGE.format(project_id)}, 200
        except Exception as e:
            return { 'message': 'This project has many experiments, please remove experiment first.'}, 500
        

class NewProject(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name',
                        type=str,
                        required=True,
                        help=ERROR_BLANK_FIELD.format('name')
                        )
    parser.add_argument('description',
                        type=str,
                        required=True,
                        help=ERROR_BLANK_FIELD.format('description')
                        )
    parser.add_argument('datasourceId',
                        type=str,
                        required=True,
                        help=ERROR_BLANK_FIELD.format('datasourceId')
                        )
    parser.add_argument('collectionId',
                        type=str,
                        required=True,
                        help=ERROR_BLANK_FIELD.format('collectionId')
                        )
    parser.add_argument('columns',
                        type=list,
                        required=True,
                        help=ERROR_BLANK_FIELD.format('columns'),
                        location='json'
                        )
    @jwt_required
    def post(self):
        user_id = get_jwt_identity()
        data = NewProject.parser.parse_args()
        name = data['name']
        description = data['description']
        datasource_id = data['datasourceId']
        collection_id = data['collectionId']
        columns = {'columns': data['columns']}
        project = ProjectModel(name, description, datasource_id, collection_id, user_id)
        if(project.find_one_by_name(name, user_id)):
            return { 'message': ERROR_DUPLICATE_NAME.format(name)}, 500
        else:
            mongo = ProjectUnstructureModel(columns)

            try:
                columns_filter_id = str(mongo.save_columns_filter_to_db())
            except Exception as e:
                return { 'message': ERROR_CANNOT_INSRET_MONGO.format(columns) }, 500

            try:
                project.save_to_db()
            except Exception as e:
                return { 'message': ERROR_CANNOT_INSERT_DB }, 500

            try:
                project = project.find_one_by_name(name, user_id)
                if project:
                    project.save_columns_filter_db(columns_filter_id)
            except Exception as e:
                return {'message': ERROR_CANNOT_INSRET_COLUMNS_FILTER.format(columns)}, 500

            return { 'message': '{} has already created'.format(name)}, 200

class ProjectColumnsFilter(Resource):
    @jwt_required
    def get(self, project_id):
        user_id = get_jwt_identity()
        result = ProjectModel.find_one_by_id(project_id, user_id)
        columns_filter_id= result.columns_filter_id
        columns_filter = ProjectUnstructureModel.find_by_object_id(ObjectId(columns_filter_id))
        return {'message': SUCCESS_MESSAGE.format('columns_filter'), 'columns_filter': columns_filter['columns'] }

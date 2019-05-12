from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity

from models.collection import CollectionModel
from models.project import ProjectModel
from models.datasource import DatasourceModel

SUCCESS_MESSAGE = "This {} request has succeed"
ERROR_BLANK_FIELD = 'This {} field cannot be left blank.'
ERROR_CANNOT_INSERT_DB = 'An error is occur cannot insert data to database'
ERROR_DUPLICATE_NAME = 'The system cannot make a new collection becuase this name ({}) has duplicated.'
ERROR_CANNOT_COLLECTION_META = 'An error is occur. It cannot delete collection (a foreign key constraint fails)'

class Collection(Resource):
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
    @jwt_required
    def post(self):
        user_id = get_jwt_identity()
        data = Collection.parser.parse_args()
        collection_name = data['name']
        collection_description = data['description']
        try:
            if(CollectionModel.find_one_by_name(collection_name, user_id)):
                return {'message': ERROR_DUPLICATE_NAME.format(collection_name)}, 500
            else:
                collection = CollectionModel(collection_name, collection_description, user_id)
                collection.save_to_db()
                return {'message': '{} collection has saved'.format(collection_name)}, 200
        except Exception as e:
            return {'message': ERROR_CANNOT_INSERT_DB}, 500

class CollectionId(Resource):
    @jwt_required
    def delete(self, collection_id):
        user_id = get_jwt_identity()
        try:
            collection = CollectionModel.find_one_by_id(collection_id, user_id)
            collection.delete_from_db()
        except Exception as e:
            return { 'message': ERROR_CANNOT_COLLECTION_META }, 500
        return {'message': SUCCESS_MESSAGE.format(collection_id)}, 200

class Collections(Resource):
    @jwt_required
    def get(self):
        user_id = get_jwt_identity()
        results = CollectionModel.find_all_by_id(user_id)
        if results :
            data = [
                {
                    'collection_id': row.collection_id,
                    'collection_name': row.collection_name,
                    'collection_description': row.collection_description,
                    'projects' : [
                        {
                            'project_id': project.project_id,
                            'project_name': project.project_name,
                            'project_description': project.project_description,
                            'datasource_id': project.datasource_id,
                        } for project in ProjectModel.find_all_by_id(row.collection_id, user_id)
                    ]
                } for row in results
            ]
            return { 'data': data }, 200
        return { 'message': 'No collection'}, 500

    def post(self):
        pass

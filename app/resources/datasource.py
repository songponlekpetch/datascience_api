from flask_restful import Resource, reqparse, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import werkzeug

from models.upload import UploadModel
from models.datasource import DatasourceModel
from function.file import File
from function.dataset import Dataset

SUCCESS_MESSAGE = "This {} request has succeed"
ERROR_BLANK_FIELD = 'This {} field cannot be left blank.'
ERROR_CANNOT_INSERT_DB = 'An error is occur cannot insert data to database'
ERROR_DUPLICATE_NAME = 'An duplicated name error is occur cannot define ({}).'
ERROR_CANNOT_UPLOAD_FILE = 'An error is occur cannot upload file to FileStorage'
ERROR_CANNOT_CONVERT_TO_DATAFRAME = 'An error is occur cannot convert data to dataframe'
ERROR_CANNOT_DELETE_DATASOURCE = 'An error is occur. It cannot delete datasource'
ERROR_CANNOT_DELETE_DATASOURCE_META = 'An error is occur. It cannot delete datasource (a foreign key constraint fails)'

class Datasources(Resource):
    @jwt_required
    def get(self):
        user_id = get_jwt_identity()
        results = DatasourceModel.find_all(user_id)
        data = [
                {
                    'datasource_id': row.datasource_id,
                    'datasource_name': row.datasource_name,
                    'datasource_description': row.datasource_description,
                    'user_schema_name': row.user_schema_name,
                    'user_table_name': row.user_table_name,
                    'created_at': str(row.created_at)
                }
                for row in results
                ]
        return {'message': 'list of all datasources', 'data': data}, 200

class Datasource(Resource):
    @jwt_required
    def get(self, datasource_id):
        user_id = get_jwt_identity()
        datasource = DatasourceModel.find_one_by_id(user_id, datasource_id)
        metadata = {
            'datasource_id': datasource.datasource_id,
            'datasource_name': datasource.datasource_name,
            'datasource_description': datasource.datasource_description,
            'user_schema_name': datasource.user_schema_name,
            'user_table_name': datasource.user_table_name,
            'created_at': str(datasource.created_at)
        }
        header = DatasourceModel.get_columns(datasource.user_schema_name, datasource.user_table_name)
        return {'header': header, 'metadata': metadata }

    @jwt_required
    def delete(self, datasource_id):
        user_id = get_jwt_identity()
        datasource = DatasourceModel.find_one_by_id(user_id, datasource_id)
        user_schema_name = datasource.user_schema_name
        user_table_name = datasource.user_table_name
        try:
            datasource.delete_from_db()
        except Exception as e:
            return { 'message': ERROR_CANNOT_DELETE_DATASOURCE_META }, 500

        try:
            datasource.delete_datasource(user_schema_name, user_table_name)
        except Exception as e:
            return { 'message': ERROR_CANNOT_DELETE_DATASOURCE }, 500
        
        return { 'message': SUCCESS_MESSAGE.format(datasource_id) }, 200

class NewDatasource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('datasource_description',
                        type=str,
                        required=True,
                        help=ERROR_BLANK_FIELD.format('datasource_description')
                        )

    parser.add_argument('upload_file',
                        type=werkzeug.datastructures.FileStorage,
                        required=True,
                        location='files',
                        )

    @jwt_required
    def get(self, datasource_name):
        user_id = get_jwt_identity()
        user_schema_name = 'u{}'.format(user_id)
        user_table_name = datasource_name
        datasource_description = ''
        datasource = DatasourceModel(datasource_name, datasource_description, user_schema_name, user_table_name, user_id)
        dataframe = datasource.get_datasource()
        dataset = Dataset(dataframe)
        header = DatasourceModel.get_columns(user_schema_name, user_table_name)
        return {'header': header,'data': dataset.get_json()}

    @jwt_required
    def post(self, datasource_name):
        # url /datasource/<string:user_schema_name>/<string:datasource_name> {
        # 	"file_name": "cassava.csv",
        # }
        user_id = get_jwt_identity()

        user_schema_name = 'u{}'.format(user_id)
        user_table_name = datasource_name

        data = NewDatasource.parser.parse_args()
        datasource_description = data['datasource_description']
        upload_file = data['upload_file']
        file_extension = upload_file.filename.split('.')[1]

        datasource = DatasourceModel(datasource_name, datasource_description, user_schema_name, user_table_name, user_id)

        if datasource.find_by_name(datasource_name, user_id):
            return {'message': ERROR_DUPLICATE_NAME.format(datasource_name)}, 500

        upload = UploadModel(upload_file)
        try:
            file_id = str(upload.save_file_to_db())
        except Exception as e:
            return {'message': ERROR_CANNOT_UPLOAD_FILE}, 500


        file = File(file_id, file_extension)
        file.read_file_to_dataset()
        dataset_dataframe = file.get_dataframe()
        dataset_json = file.get_json()
        datasource = DatasourceModel(datasource_name, datasource_description, user_schema_name, user_table_name, user_id)

        try:
            datasource.new_datasource(dataset_dataframe)
        except Exception as e:
            return {'message': ERROR_CANNOT_CONVERT_TO_DATAFRAME}, 500
        try:
            datasource.save_to_db(file_id)
        except Exception as e:
            return {'message': ERROR_CANNOT_INSERT_DB}, 500

        return {'message': 'sucess' , 'dataset': dataset_json}, 200

class DatasourceHeader(Resource):
    @jwt_required
    def get(self, datasource_name):
        user_id = get_jwt_identity()
        user_schema_name = 'u{}'.format(user_id)
        user_table_name = datasource_name
        header = DatasourceModel.get_columns(user_schema_name, user_table_name)
        return {'message': 'sucess' ,'header': header}, 200

class DatasourceColumns(Resource):
    @jwt_required
    def get(self, datasource_id):
        user_id = get_jwt_identity()
        datasource = DatasourceModel.find_one_by_id(user_id, datasource_id)
        if(datasource):
            datasource_name = datasource.datasource_name
            user_schema_name = 'u{}'.format(user_id)
            user_table_name = datasource_name
            header = DatasourceModel.get_columns(user_schema_name, user_table_name)
            return {'message': 'sucess' ,'header': header}, 200
        else:
            return {'message': 'Cannot fetch columns' }, 500

class DatasourcePages(Resource):
    @jwt_required
    def get(self, datasource_id, page_size):
        user_id = get_jwt_identity()
        datasource = DatasourceModel.find_one_by_id(user_id, datasource_id)
        pages, rows = datasource.get_datasource_pages(page_size)
        return {
            'message': SUCCESS_MESSAGE.format(datasource_id),
            'data': { 
                'datasource_id':  datasource_id,
                'datasource_name': datasource.datasource_name, 
                'pages': pages,
                'rows': rows,
                'page_size': page_size
            }
        }

class DatasourcePerPage(Resource):
    @jwt_required
    def get(self, datasource_id, page_size, page):
        user_id = get_jwt_identity()
        datasource = DatasourceModel.find_one_by_id(user_id, datasource_id)
        dataframe = datasource.get_datasource_per_page(page, page_size)
        dataset = Dataset(dataframe)
        header = DatasourceModel.get_columns(datasource.user_schema_name, datasource.user_table_name)
        return {'header': header,'data': dataset.get_json()}


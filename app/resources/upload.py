from flask_restful import Resource, reqparse
import werkzeug
from bson.objectid import ObjectId

from models.upload import UploadModel

ERROR_BLANK_FIELD = 'This {} field cannot be left blank.'
ERROR_CANNOT_INSERT_DB = 'An error is occur cannot insert data to database'
ERROR_DUPLICATE_NAME = 'An duplicated name error is occur cannot define ({}).'

class Upload(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('upload_file',
                        type=werkzeug.datastructures.FileStorage,
                        required=True,
                        location='files',
                        )
    def post(self):
        data = Upload.parser.parse_args()
        file = data['upload_file']
        print(file)

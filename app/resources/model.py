from flask_restful import Resource, reqparse
from bson.objectid import ObjectId

from models.model import ModelModel, ModelTypeModel, ModelUnstructureModel

SUCCESS_MESSAGE = "This ({}) request has succeed"
ERROR_CANNOT_GET_MODEL_PARAMETER_ID = 'An error is occur cannot find MODEL PARAMETER ID ({}).'
ERROR_CANNOT_GET_MODEL_PARAMETER = 'An error is occur cannot find MODEL PARAMETER ({}).'

class Models(Resource):
    def get(self):
        # results = ModelModel.find_all()
        # data = [{ 'model_id': row.model_id, 'model_name': row.model_name} for row in results]
        # return {'message': 'list of all models', 'data': data}, 200
        results = ModelTypeModel.find_all()
        data = [ 
            {
                'type': model_type.model_type_name,
                'models': [ 
                    {
                        'id': model.model_id,
                        'name': model.model_name,
                        'created_at': str(model.created_at)
                    } for model in model_type.model
                ]

            } for model_type in results 
        ]
        return { 'message': SUCCESS_MESSAGE.format('Models') , 'data': data }

class ModelParameter(Resource):
    def get(self, model_id):
        try:
            model = ModelModel.find_first_by_id(model_id)
            model_parameter_id = model.model_parameter_id
        except Exception as e:
            return { 'message': ERROR_CANNOT_GET_MODEL_PARAMETER_ID.format(model_id)}, 500
        try:
            model_parameter = ModelUnstructureModel.find_by_object_id(ObjectId(model_parameter_id))
        except Exception as e:
            print(e)
            return { 'message': ERROR_CANNOT_GET_MODEL_PARAMETER.format(model_parameter_id)}, 500
        
        return { 'message': SUCCESS_MESSAGE.format(model_id), 'data': model_parameter['parameter'] }
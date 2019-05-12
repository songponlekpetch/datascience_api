from flask_restful import Resource

class CheckAccessStatus(Resource):
    def get(self, name):
        return {'status': '200 OK for API Testing.'}

class CheckAccessStatus2(Resource):
    def get(self, task_id):
        return {'status': '200 OK for API Testing.'}

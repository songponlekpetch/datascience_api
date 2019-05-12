import os
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from flask_restful import Api
from flask_jwt_extended import JWTManager
import urllib
import datetime
from dotenv import load_dotenv

from db import db, mongo
from resources.check_access_status import CheckAccessStatus, CheckAccessStatus2
from resources.datasource import (
    Datasources, 
    Datasource, 
    NewDatasource, 
    DatasourceHeader, 
    DatasourceColumns, 
    DatasourcePages,
    DatasourcePerPage
)
from resources.experiment import (
    Experiment, 
    ExperimentReLearning, 
    Experiments, 
    ExperimentsById, 
    ExperimentCalScoreId,
    ExperimentModelParameter, 
    ExperimentViz
)
from resources.model import Models, ModelParameter
from resources.prediction import Prediction, PrePrediction, AddPrediction
from resources.collection import Collection, CollectionId, Collections
from resources.project import Project, NewProject, ProjectColumnsFilter
from resources.upload import Upload
from resources.user import UserRegister, UserConfirm, UserLogin, UserLogout, TokenCheck, ForgetPassword
from blacklist import BLACKLIST

app = Flask(__name__)

CORS(app)
load_dotenv('.env')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config['SQLALCHEMY_POOL_RECYCLE'] = 90
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True

app.config['MONGO_DATABASE'] = 'devdb'
app.config['MONGO_URI'] = "mongodb://root:{}@127.0.0.1:7003/devdb".format(urllib.parse.quote_plus('password'))

app.config['JWT_SECRET_KEY'] = 'secret'
app.config['JWT_BACKLIST_ENABLED'] = True
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days = 1 )
app.config['JWT_BACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

db.init_app(app)
mongo.init_app(app)


api = Api(app)

jwt = JWTManager(app)

@jwt.user_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1:
        return {'is_admin': True}
    return { 'is_admin': False}

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token['jti'] in BLACKLIST

api.add_resource(CheckAccessStatus, '/test/<string:name>')
api.add_resource(CheckAccessStatus2, '/test/2/<string:task_id>')
#get = get list of datasources info (json) by user_id
api.add_resource(Datasources, '/datascience/datasources')
api.add_resource(Datasource, '/datascience/datasource/<string:datasource_id>')
#post = create datasource and append
#get = get datasource (json) by datasource's name
api.add_resource(NewDatasource, '/datascience/datasource/<string:datasource_name>')
api.add_resource(DatasourcePages, '/datascience/datasource/<string:datasource_id>/<string:page_size>')
api.add_resource(DatasourcePerPage, '/datascience/datasource/<string:datasource_id>/<string:page_size>/page/<string:page>')
api.add_resource(DatasourceHeader, '/datascience/datasource/<string:datasource_name>/header')
api.add_resource(DatasourceColumns, '/datascience/datasource/columns/<string:datasource_id>')

api.add_resource(Experiment, '/datascience/experiment/<string:project_id>/<string:experiment_name>')
api.add_resource(ExperimentReLearning, '/datascience/experiment/relearning/<string:experiment_id>')

api.add_resource(Experiments, '/datascience/experiments')
api.add_resource(ExperimentsById, '/datascience/project/<string:project_id>/experiments')
api.add_resource(ExperimentModelParameter, '/datascience/experiment/model_parameter/<string:model_parameter_id>')
api.add_resource(ExperimentCalScoreId, '/datascience/experiment/cal_score/<string:cal_score_id>')
api.add_resource(ExperimentViz, '/datascience/experiment/<string:experiment_name>/viz/<string:viz_id>')

api.add_resource(Prediction, '/datascience/prediction/<string:experiment_name>')
api.add_resource(PrePrediction, '/datascience/preprediction/<string:experiment_name>')
api.add_resource(AddPrediction, '/datascience/prediction/add/<string:datasource_name>')

api.add_resource(Collection, '/datascience/collection')
api.add_resource(CollectionId, '/datascience/collection/<string:collection_id>')
api.add_resource(Collections, '/datascience/collections')

api.add_resource(Project, '/datascience/project/<string:project_id>')
api.add_resource(NewProject, '/datascience/project')
api.add_resource(ProjectColumnsFilter, '/datascience/project/columns_filter/<string:project_id>')

api.add_resource(Models, '/datascience/models')
api.add_resource(ModelParameter,'/datascience/model/<string:model_id>' )

api.add_resource(Upload, '/upload')
api.add_resource(UserRegister, '/register')
api.add_resource(UserConfirm, '/confirm/<string:user_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')
api.add_resource(TokenCheck, '/check')
api.add_resource(ForgetPassword, '/forgetpassword')

if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000, debug=True)
    app.run(host='0.0.0.0', port=80)

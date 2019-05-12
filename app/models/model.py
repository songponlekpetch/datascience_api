from db import db, mongo

class ModelModel(db.Model):
    __tablename__= 'model'

    model_id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(255))
    model_parameter_id = db.Column(db.String(255))
    model_type_id = db.Column(db.Integer, db.ForeignKey('model_type.model_type_id'))
    created_at = db.Column(db.TIMESTAMP)

    def __init__(self, model_name):
        self.model_name = model_name

    @classmethod
    def find_first_by_id(cls, model_id):
        db.engine.execute('USE {};'.format('data_science'))
        return cls.query.filter_by(model_id=model_id).first()

    @classmethod
    def find_all(cls):
        db.engine.execute('USE {};'.format('data_science'))
        return cls.query.all()

class ModelTypeModel(db.Model):
    __tablename__ = 'model_type'

    model_type_id = db.Column(db.Integer, primary_key = True)
    model_type_name = db.Column(db.String(255))
    created_at = db.Column(db.TIMESTAMP)

    model = db.relationship('ModelModel', backref='model_type')

    def __init__(self, model_type_name):
        self.model_type_name = model_type_name

    @classmethod
    def find_all(cls):
        return cls.query.all()

class ModelUnstructureModel:

    def __init__(self, parameter):
        self.parameter = parameter

    def save_paramter_to_db(self):
        parameter = self.parameter
        return mongo.db.model_parameter.insert_one(parameter).inserted_id

    @classmethod
    def find_by_object_id(cls, id):
        return mongo.db.model_parameter.find_one({'_id': id})
from db import db, mongo

class ExperimentModel(db.Model):
    __tablename__= 'experiment'

    experiment_id = db.Column(db.Integer, primary_key=True)
    experiment_name = db.Column(db.String(255))
    experiment_description = db.Column(db.String(255))
    cal_score_id = db.Column(db.String(255))
    datasource_id = db.Column(db.Integer)
    model_id = db.Column(db.Integer)
    y_col = db.Column(db.String(255))
    model_parameter_id = db.Column(db.String(255))
    project_id = db.Column(db.Integer)
    viz_id = db.Column(db.String(255))
    user_id = db.Column(db.Integer)
    created_at = db.Column(db.TIMESTAMP)

    def __init__(self, experiment_name, experiment_description, datasource_id, model_id, y_col, project_id, user_id):
        self.experiment_name = experiment_name
        self.experiment_description = experiment_description
        self.datasource_id = datasource_id
        self.model_id = model_id
        self.y_col = y_col
        self.project_id = project_id
        self.user_id = user_id

    def save_to_db(self):
        db.engine.execute('USE {};'.format('data_science'))
        db.session.add(self)
        db.session.commit()

    def save_cal_score_to_db(self, cal_score_id):
        self.cal_score_id = cal_score_id
        db.engine.execute('USE {};'.format('data_science'))
        db.session.add(self)
        db.session.commit()
    
    def save_model_parameter_to_db(self, model_parameter_id):
        self.model_parameter_id = model_parameter_id
        db.engine.execute('USE {};'.format('data_science'))
        db.session.add(self)
        db.session.commit()

    def save_viz_to_db(self, viz_id):
        self.viz_id = viz_id
        db.engine.execute('USE {};'.format('data_science'))
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_all(cls):
        db.engine.execute('USE {};'.format('data_science'))
        return cls.query.all()

    @classmethod
    def find_all_by_id(cls, project_id):
        db.engine.execute('USE {};'.format('data_science'))
        return cls.query.filter_by(project_id=project_id)

    def json(self):
        return {
            'experiment_name': self.experiment_name,
            'experiment_description': self.experiment_description,
            'cal_score_id': self.cal_score_id,
            'datasource_id': self.datasource_id,
            'model_id': self.model_id,
            'y_col': str(self.y_col)
        }

    @classmethod
    def find_by_name(cls, user_id, experiment_name):
        return cls.query.filter_by(experiment_name=experiment_name, user_id=user_id).first()
    
    @classmethod
    def find_by_id(cls, experiment_id):
        return cls.query.filter_by(experiment_id=experiment_id).first()

    @classmethod
    def find_by_experiment_name(cls, user_id, experiment_name):
        db.engine.execute('USE {};'.format('data_science'))
        return cls.query.filter_by(experiment_name=experiment_name, user_id=user_id).first()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

class ExperimentUnstructureModel:

    def __init__(self, cal_score, model_parameter):
        self.cal_score = cal_score
        self.model_parameter = {'model_parameter': model_parameter}

    def save_cal_score_to_db(self):
        cal_score = self.cal_score
        return mongo.db.experiment_cal_score.insert_one(cal_score).inserted_id
    
    def save_model_parameter_to_db(self):
        model_parameter = self.model_parameter
        return mongo.db.experiment_model_parameter.insert_one(model_parameter).inserted_id

    @classmethod
    def find_by_object_id(cls, id):
        return mongo.db.experiment_cal_score.find_one({'_id': id})

    @classmethod
    def find_model_parameter_by_object_id(cls, id):
        return mongo.db.experiment_model_parameter.find_one({'_id': id})

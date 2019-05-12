from db import db, mongo

class ProjectModel(db.Model):
    __tablename__ = 'project'

    project_id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(255))
    project_description = db.Column(db.String(255))
    datasource_id = db.Column(db.String(255))
    columns_filter_id = db.Column(db.String(255))
    collection_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    created_at = db.Column(db.TIMESTAMP)

    def __init__(self, project_name, project_description, datasource_id, collection_id, user_id):
        self.project_name = project_name
        self.project_description = project_description
        self.datasource_id = datasource_id
        self.collection_id = collection_id
        self.user_id = user_id

    def json(self):
        return {
            'project_name': self.project_name,
            'project_description': self.project_description,
            'datasource_id': self.datasource_id,
            'collection_id': self.collection_id,
            'created_at': str(self.created_at)
        }

    @classmethod
    def find_all_by_id(cls, collection_id, user_id):
        db.engine.execute('USE {};'.format('data_science'))
        return cls.query.filter_by(user_id = user_id, collection_id = collection_id).order_by(ProjectModel.created_at.desc())

    @classmethod
    def find_one_by_id(cls, project_id, user_id):
        db.engine.execute('USE {};'.format('data_science'))
        return cls.query.filter_by(project_id=project_id, user_id=user_id).first()

    @classmethod
    def find_one_by_name(cls, project_name, user_id):
        db.engine.execute('USE {};'.format('data_science'))
        return cls.query.filter_by(project_name=project_name, user_id=user_id).first()

    def save_to_db(self):
        db.engine.execute('USE {};'.format('data_science'))
        db.session.add(self)
        db.session.commit()

    def save_columns_filter_db(self, columns_filter_id):
        self.columns_filter_id = columns_filter_id
        db.engine.execute('USE {};'.format('data_science'))
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

class ProjectUnstructureModel:

    def __init__(self, columns):
        self.columns = columns

    def save_columns_filter_to_db(self):
        columns = self.columns
        return mongo.db.columns_filter.insert_one(columns).inserted_id

    @classmethod
    def find_by_object_id(cls, id):
        return mongo.db.columns_filter.find_one({'_id': id})
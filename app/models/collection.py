from db import db

class CollectionModel(db.Model):
    __tablename__ = 'collection'

    collection_id = db.Column(db.Integer, primary_key=True)
    collection_name = db.Column(db.String(255))
    collection_description = db.Column(db.String(255))
    user_id = db.Column(db.Integer)
    created_at = db.Column(db.TIMESTAMP)

    def __init__(self, collection_name, collection_description, user_id):
        self.collection_name = collection_name
        self.collection_description = collection_description
        self.user_id = user_id

    def save_to_db(self):
        db.engine.execute('USE {};'.format('data_science'))
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_all_by_id(cls, user_id):
        db.engine.execute('USE {};'.format('data_science'))
        return cls.query.filter_by(user_id = user_id).order_by(CollectionModel.created_at.desc())

    @classmethod
    def find_one_by_id(cls, collection_id, user_id):
        db.engine.execute('USE {};'.format('data_science'))
        return cls.query.filter_by(collection_id = collection_id, user_id = user_id).first()

    @classmethod
    def find_one_by_name(cls, collection_name, user_id):
        db.engine.execute('USE {};'.format('data_science'))
        return cls.query.filter_by(collection_name = collection_name, user_id = user_id).first()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
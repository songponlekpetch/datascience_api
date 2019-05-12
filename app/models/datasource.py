from db import db
import pandas as pd
import os
from math import ceil

class DatasourceModel(db.Model):
    __tablename__= 'datasource'

    datasource_id = db.Column(db.Integer, primary_key=True)
    datasource_name = db.Column(db.String(255))
    datasource_description = db.Column(db.String(255))
    file_id = db.Column(db.String(255))
    user_schema_name = db.Column(db.String(255))
    user_table_name = db.Column(db.String(255))
    user_id = db.Column(db.Integer)
    created_at = db.Column(db.TIMESTAMP)

    def __init__(self, datasource_name, datasource_description, user_schema_name, user_table_name, user_id):
        self.datasource_name = datasource_name
        self.datasource_description = datasource_description
        self.user_schema_name = user_schema_name
        self.user_table_name = user_table_name
        self.user_id = user_id

    @classmethod
    def find_all(cls, user_id):
        db.engine.execute('USE {};'.format('data_science'))
        return cls.query.filter_by(user_id=user_id).order_by(DatasourceModel.created_at.desc())

    @classmethod
    def find_one_by_id(cls, user_id, datasource_id):
        db.engine.execute('USE {};'.format('data_science'))
        return cls.query.filter_by(datasource_id=datasource_id, user_id=user_id).first()

    def json(self):
        return {
            'datasource_name': self.datasource_name,
            'datasource_description': self.datasource_description,
            'user_schema_name': self.user_schema_name,
            'user_table_name': self.user_table_name,
            'created_at': str(self.created_at)
        }

    @classmethod
    def find_by_name(cls, datasource_name, user_id):
        db.engine.execute('USE {};'.format('data_science'))
        return cls.query.filter_by(datasource_name=datasource_name, user_id=user_id).first()

    def save_to_db(self, file_id):
        self.file_id = file_id
        db.engine.execute('USE {};'.format('data_science'))
        db.session.add(self)
        db.session.commit()

    def new_datasource(self, dataset_dataframe):
        db.engine.execute('USE {};'.format('data_science'))
        db.engine.execute('CREATE SCHEMA IF NOT EXISTS {};'.format(self.user_schema_name))
        db.session.commit()
        engine = db.create_engine('{}/{}'.format(os.environ.get('DATABASE_URI_USER'), self.user_schema_name))
        connection = engine.connect()
        dataset_dataframe.to_sql(name=self.user_table_name, con=engine, index=False, if_exists='append')
        connection.execute('USE {};'.format(self.user_schema_name))
        result = connection.execute('''SELECT * FROM INFORMATION_SCHEMA.COLUMNS
            WHERE table_name = "{}"
            AND table_schema = "{}"
            AND column_name = "id";'''.format(self.user_table_name, self.user_schema_name))
        result_exists = [row for row in result]
        if result_exists == []:
            connection.execute('USE {};'.format(self.user_schema_name))
            connection.execute('ALTER TABLE {} ADD id INT PRIMARY KEY AUTO_INCREMENT FIRST;'.format(self.user_table_name))
        connection.close()
        db.engine.execute('USE {};'.format('data_science'))
        db.session.commit()

    @classmethod
    def append_datasource(cls, dataset, user_schema_name, user_table_name):
        engine = db.create_engine('{}/{}'.format(os.environ.get('DATABASE_URI_USER'), user_schema_name))
        dataset.to_sql(name=user_table_name, con=engine, index=False, if_exists='append')
    
    @classmethod
    def delete_datasource(cls, user_schema_name, user_table_name):
        engine = db.create_engine('{}/{}'.format(os.environ.get('DATABASE_URI_USER'), user_schema_name))
        connection = engine.connect()
        connection.execute('DROP TABLE {};'.format(user_table_name))
        connection.close()

    def get_datasource(self):
        engine = db.create_engine('{}/{}'.format(os.environ.get('DATABASE_URI_USER'), self.user_schema_name))
        dataset = pd.read_sql_table(self.user_table_name, engine)
        return dataset

    def get_datasource_pages(self, page_size):
        engine = db.create_engine('{}/{}'.format(os.environ.get('DATABASE_URI_USER'), self.user_schema_name))
        dataset = pd.read_sql_query(
        """
        SELECT TABLE_ROWS
            FROM information_schema.tables
            WHERE table_schema=DATABASE()
            AND table_name='{}';
        """.format(self.user_table_name), engine)
    
        return (ceil(int(dataset['TABLE_ROWS'][0]) / int(page_size)), int(dataset['TABLE_ROWS'][0]))


    def get_datasource_per_page(self, page, page_size):
        page = int(page) - 1
        page_size = int(page_size)
        engine = db.create_engine('{}/{}'.format(os.environ.get('DATABASE_URI_USER'), self.user_schema_name))
        dataset = pd.read_sql_query(
        """
            SELECT * 
            FROM {}
            WHERE id > {}
            ORDER BY id
            LIMIT {}
        """.format(self.user_table_name, str(page * page_size), str(page_size)), engine)
        return dataset

    @classmethod
    def get_columns(cls, user_schema_name, user_table_name):
        query = "select COLUMN_NAME, DATA_TYPE from INFORMATION_SCHEMA.COLUMNS where TABLE_SCHEMA='{}' AND TABLE_NAME='{}'".format(user_schema_name, user_table_name)
        engine = db.create_engine('{}/{}'.format(os.environ.get('DATABASE_URI_USER'), user_schema_name))
        result = db.engine.execute(query)
        col = [ { 'column_name': row[0], 'data_type': row[1] } for row in result ]
        return col
    
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

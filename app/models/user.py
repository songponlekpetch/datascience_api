from db import db

class UserModel(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key= True)
    email = db.Column(db.String(255))
    password = db.Column(db.String(255))
    firstname = db.Column(db.String(255))
    lastname = db.Column(db.String(255))
    gender = db.Column(db.String(10))
    birth_date = db.Column(db.Date)
    mobile_phone = db.Column(db.String(255))
    activated = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.TIMESTAMP)

    def __init__(self, email, password, firstname, lastname, gender, birth_date, mobile_phone):
        self.email = email
        self.password = password
        self.firstname = firstname
        self.lastname = lastname
        self.gender = gender
        self.birth_date = birth_date
        self.mobile_phone = mobile_phone

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email = email).first()
    
    @classmethod
    def find_by_id(cls, user_id):
        return cls.query.filter_by(user_id = user_id).first()

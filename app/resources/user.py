from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    jwt_required,
    create_access_token, 
    create_refresh_token,
    get_jwt_identity,
    jwt_refresh_token_required,
    get_raw_jwt
)

from blacklist import BLACKLIST
from models.user import UserModel
from function.email import Email

class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('email',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )
    parser.add_argument('password',
                        type=str,
                        required=True,
                        help="This field cannot be blank.")
    parser.add_argument('firstname',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )
    parser.add_argument('lastname',
                        type=str,
                        required=True,
                        help="This field cannot be blank.")
    parser.add_argument('gender',
                        type=str,
                        required=True,
                        help="This field cannot be blank.")
    parser.add_argument('birth_date',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )
    parser.add_argument('mobile_phone',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )
    
    @classmethod
    def post(cls):
        data = cls.parser.parse_args()
        if (UserModel.find_by_email(data['email'])):
            return { 'message': 'This email has already registed.'}, 500
        try:
            user = UserModel(**data)
            user.save_to_db()
            
        except Exception as e:
            return { 'message': 'Register cannot be done.'}, 500

        user_id = UserModel.find_by_email(data['email']).user_id
        email = Email(user_id, data['email'])
        checked = email.send_confirm_email()
        if(not checked):
            return { 'message': 'Email server has problems.'}, 500
        
        return { 'message': 'Rigster is suceed, please check your email.'}, 200

class UserConfirm(Resource):
    def put(self, user_id):
        user = UserModel.find_by_id(user_id)
        user.activated = 1
        user.save_to_db()
        return { 'message': 'Cofirm is suceed, please login with your email.'}, 200

class UserLogin(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('email',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )
    parser.add_argument('password',
                        type=str,
                        required=True,
                        help="This field cannot be blank.")
    
    @classmethod
    def post(cls):
        data = cls.parser.parse_args()
        try:
            user = UserModel.find_by_email(data['email'])
            if user and safe_str_cmp(user.password, data['password']):
                access_token = create_access_token(identity = user.user_id, fresh = True)
                refresh_token = create_refresh_token(user.user_id)
                return {
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }, 200
            
            return {
                'message': 'Invalid credentials.'
            }, 401
        except Exception as e:
            return {
                'message': 'System cannot connect database server.'
            }
class UserLogout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti'] # jwt is "JWT ID", a unique identifier for JWT.
        BLACKLIST.add(jti)
        return {'message': 'Successfully logged out.'}, 200

class TokenCheck(Resource):
    @jwt_required
    def get(self):
        return {'message': 'Token has validated.'}, 200

class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity
        new_token = create_access_token(identity= current_user, fresh=False)
        return {'access_token': new_token }, 200

class ForgetPassword(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('email',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )

    def post(self):
        data = self.parser.parse_args()
        try:
            user = UserModel.find_by_email(data['email'])
            if user:
                # send email
                user_id = user.user_id
                email = Email(user_id, data['email'])
                checked = email.send_reset_password_email()
                if(not checked):
                    return { 'message': 'Email server has problems.'}, 500
                
                return { 'message': 'Please check you email for reset password'}, 200
            else:
                return { 'message': 'Email is not registered, please click register at below.'}, 500
        except Exception as e:
            return { 'message': 'System cannot connect database server.'}, 500

class ResetPassword(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('password',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )

    def put(self, user_id):
        data = self.parser.parse_args()
        try:
            user = UserModel.find_by_email(user_id)
            if(user):
                user.password = data['password']
                user.save_to_db()
                return { 'message': 'Password has already reset'}, 200
            else:
                return { 'message': 'System cannot find user'}, 500
        except Exception as e:
            return { 'message': 'System cannot make operation with database server' }, 500

from leapi import db,app,api
from flask.ext.restplus import fields, Resource
from flask import request, g, jsonify
from flask.ext.security import Security, SQLAlchemyUserDatastore, login_required
from leapi.models import User, Role
from flask.ext.httpauth import HTTPBasicAuth
import base64
#auth = HTTPBasicAuth()

app.config['SECRET_KEY'] = 'how many chucks would a woodchuck chuck if a woodchuck could chuck wood?'

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

#@app.before_first_request
#def create_user():
#    user_datastore.create_user(email='dmaczka@vt.edu', password='password')
#    db.session.commit()

#@auth.verify_password
#def verify_password(username_or_token, password):
#    user = User.verify_auth_token(username_or_token)
#    if not user:
#     user = User.query.filter_by(email = username_or_token).first()
#     if not user or not user.verify_password(password):
#         return False
# g.user = user
# return True

@app.login_manager.request_loader
def load_user_from_request(request):
    # first, try to login using the api_key url arg
    api_key = request.args.get('api_key')
    if api_key:
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            g.user = user
            return user

    # next, try to login using Basic Auth
    api_key = request.headers.get('Authorization')
    if api_key:
        api_key = api_key.replace('Basic ', '', 1)
        try:
            api_key = base64.b64decode(api_key)
        except TypeError:
            pass
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            g.user = user
            return user

    # next, try to login using Basic username:password Auth
    print("load_user_from_request, trying user:password auth: {}".format(request))
    username, password = api_key.split(':')
    user = User.query.filter_by(email=username).first()
    if user.verify_password(password):
        g.user = user
        return user
    # finally, return None if both methods did not login the user
    return None

@app.route('/token')
@login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})

@api.route('/protected')
class ProtectedResource(Resource):
    
    @login_required
    def get(self):
        roles = Role.query.all()
        #return roles
        return {'message': 'you are approved!'}

#@app.route('/users', endpoint='users')
class UserResource(Resource):
    fields = api.model('User', {
        'email': fields.String(description='a valid email address', required=True),
        'password': fields.String(description='a password', required=True)
    })

    @api.expect(fields)
    def post(self):
        email = request.json.get('email')
        password = request.json.get('password')
        if email is None or password is None:
            api.abort(400, message='both email and password are required')    # missing arguments
        if User.query.filter_by(email=email).first() is not None:
            api.abort(400, message='user already exists')    # existing user
        user = User(email=email)
        user.hash_password(password)
        db.session.add(user)
        db.session.commit()
        return user
        #return (jsonify({'username': user.username}), 201,
        #        {'Location': url_for('get_user', id=user.id, _external=True)})

api.add_resource(UserResource, '/users')

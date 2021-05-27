import flask
from googleApis import addMailToNotion, getAccessFromRefresh, getToken, getUserEmails, getUserLabels
from flask import Flask, jsonify, session
from flask_session import Session
from flask_restful import request
from flask_cors import CORS
import os
from flask_sqlalchemy import SQLAlchemy
import redis

config = {
  'ORIGINS': [
    'http://localhost:3000',  # React
    'http://127.0.0.1:3000',  # React
    'https://gmail-to-notion-web.vercel.app',
  ],

  'SECRET_KEY': '...'
}


app = Flask(__name__)
env_config = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = 'BAD_SECRET_KEY'
# Configure Redis for storing the session data on the server-side
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_COOKIE_NAME'] = 'qid'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_REDIS'] = redis.from_url(app.config['REDIS_URL'])
print(app.config['SESSION_COOKIE_HTTPONLY'])
db = SQLAlchemy(app)
from models import User
server_session = Session(app)
CORS(app, resources={ r'/*': {'origins': config['ORIGINS']}}, supports_credentials=True)
# api = Api(app)

@app.route("/createUser", methods=["POST"])
def create():
    """POST in server"""
    gmail_client_id = app.config.get("GMAIL_CLIENT_ID")
    gmail_client_secret = app.config.get("GMAIL_CLIENT_SECRET")
    if(request.data): 
      data = request.get_json()
      print(app.config['REDIRECT_URL'])
      response = getToken(data["code"], gmail_client_id, gmail_client_secret, app.config['REDIRECT_URL'])
      print(response['refresh_token'])
      user = User(response['refresh_token'], "", "", "")
      try:
        print('here 1')
        db.session.add(user)
        print('here 2')
        db.session.commit()
        print('here 3')
      except:
        print('something went wrong while adding to db')
      # addMailToNotion(response, notion_key)
    print('id of the user is {}'.format(user.id))
    session['id'] = user.id
    # response = jsonify(user.to_dict)
    # response.headers.add("Access-Control-Allow-Origin", "*")
    return {"user": user.to_dict()}


@app.route("/me", methods=["GET"])
def me():
    """POST in server"""
    try:
      print(session['id'])
      session_id = session['id']
      user: User = User.query.filter_by(id=session_id).first()
      return {"user": user.to_dict()}
    except:
      return {"user": None}

@app.route("/updateUser", methods=["POST"])
def update():
    """POST in server"""
    print(session['id'])
    session_id = session['id']
    user: User = User.query.filter_by(id=session_id).first()
    if(request.data): 
      data = request.get_json()
      print(data["notion_key"])
      print(data["database_id"])
      user.notion_integration_key = data['notion_key']
      user.database_id = data['database_id']
      user.label = data['label']
      try:
        print('here 1')
        db.session.commit()
        print('here 3')
      except:
        print('something went wrong while updating user in db')
      # addMailToNotion(response, notion_key)
    # response = jsonify(user.to_dict())
    # response.headers.add("Access-Control-Allow-Origin", "*")
    return user.to_dict()

@app.route("/notion", methods=["POST"])
def post_to_notion():
    """POST in server"""
    user_id = session['id']
    print(user_id)
    user = User.query.filter_by(id=user_id).first()
    gmail_client_id = app.config.get("GMAIL_CLIENT_ID")
    gmail_client_secret = app.config.get("GMAIL_CLIENT_SECRET")
    response = getAccessFromRefresh(user.refresh_token, gmail_client_id, gmail_client_secret)
    # print(response)
    label_response = getUserLabels(response['access_token'])
    print(label_response)
    label_id = None
    for label in label_response['labels']:
      if label['name'] == user.label:
        label_id = label['id']
    emails = getUserEmails(response['access_token'], label_id)
    print(emails)
    addMailToNotion(response['access_token'], emails['messages'][0]['id'], user.notion_integration_key, user.database_id)
    return emails['messages'][0]['id']


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port="5000")

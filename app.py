from googleApis import addMailToNotion, getAccessFromRefresh, getToken
from flask import Flask, jsonify
from flask_restful import request
from flask_cors import CORS
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
env_config = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
from models import User
CORS(app)
# api = Api(app)

@app.route("/", methods=["POST"])
def post_example():
    """POST in server"""
    response = jsonify(message="POST request returned")
    response.headers.add("Access-Control-Allow-Origin", "*")
    notion_key = app.config.get("NOTION_SECRET_KEY")
    gmail_client_id = app.config.get("GMAIL_CLIENT_ID")
    gmail_client_secret = app.config.get("GMAIL_CLIENT_SECRET")
    if(request.data): 
      data = request.get_json()
      print(data["code"])
      response = getToken(data["code"], gmail_client_id, gmail_client_secret)
      print(response['refresh_token'])
      try:
        user = User(refresh_token = response['refresh_token'])
        print('here 1')
        db.session.add(user)
        print('here 2')
        db.session.commit()
        print('here 3')
      except:
        print('something went wrong while adding to db')
      # addMailToNotion(response, notion_key)
    return response
  
@app.route("/notion", methods=["POST"])
def post_to_notion():
    """POST in server"""
    user = User.query.filter_by(id=1).first()
    notion_key = app.config.get("NOTION_SECRET_KEY")
    gmail_client_id = app.config.get("GMAIL_CLIENT_ID")
    gmail_client_secret = app.config.get("GMAIL_CLIENT_SECRET")
    response = getAccessFromRefresh(user.refresh_token, gmail_client_id, gmail_client_secret)
    print(response)
    addMailToNotion(response['access_token'], notion_key)
    return user


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port="5000")

from googleApis import addMailToNotion, getAccessToken
import json
from flask import Flask, jsonify
from flask_restful import request
from flask_cors import CORS
import ast

app = Flask(__name__)
CORS(app)
# api = Api(app)

@app.route("/", methods=["POST"])
def post_example():
    """POST in server"""
    response = jsonify(message="POST request returned")
    response.headers.add("Access-Control-Allow-Origin", "*")
    if(request.data): 
      data = request.get_json()
      print(data["code"])
      response = getAccessToken(data["code"])
      print(response)
      addMailToNotion(response)
    return response


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port="5000")

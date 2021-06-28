import base64
from PIL import Image
from io import BytesIO
import base64
import mysql.connector
from flask import Flask, app, request, jsonify
from flask import render_template
from flask_restful import Resource, Api
from watermarking import embedWatermarking

app = Flask(__name__)
api = Api(app)
mydb = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="123456",
        database="attt"
    )
@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/home', methods=['POST', 'GET'])
def login():
    mycursor=mydb.cursor()
    if request.method=='POST':
        signup = request.form
        username = signup['user']
        password = signup['password']
        # print('username: ' + username + ' password: ' + password)
        query = "select * from users where gmail='{}' and password='{}'".format(username, password)
        print(query)
        mycursor.execute(query)
        r = mycursor.fetchall()
        count = mycursor.rowcount
        if count == 1:
            return render_template("main.html")
        else:
            return render_template("index.html")
    mydb.commit()
    mycursor.close()

# sign up for an account
@app.route('/signup')
def sign_up_page():
    return render_template('signup.html')

@app.route('/register', methods=['POST'])
def register():
    mycursor = mydb.cursor()
    if request.method=='POST':
        signup = request.form
        username = signup['name']
        account = signup['email']
        signature = signup['signature']
        password = signup['password']
        query = "select * from users where gmail='{}'".format(account)
        mycursor.execute(query)
        r = mycursor.fetchall()
        count = mycursor.rowcount
        print("count = " + str(count))
        # tài khoản có thể sử dụng, chưa có ai đăng ký gmail này
        if count == 0:
            insert_query = "insert into users (name, gmail, password, sign) values ('" + username + "', '" + account + "', '" + password + "', '" + signature + "')"
            print("insert_query: " + insert_query)
            mycursor.execute(insert_query)
            mydb.commit()
            mycursor.close()
            return render_template('index.html')
        else:
            print("error")
            mydb.commit()
            mycursor.close()
            return render_template('signup.html')

# API for water mark
class WaterMarkImage(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        base64_string = json_data['base64']
        signature = json_data['signature']
        print("base64_string: {} signature: {}".format(base64_string, signature))
        result = embedWatermarking(base64_string, signature)
        return jsonify(result=result)
api.add_resource(WaterMarkImage, '/watermark')

# main
if __name__ == '__main__':
    app.run(debug=True)
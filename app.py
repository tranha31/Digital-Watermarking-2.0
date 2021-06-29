import base64
from PIL import Image
from io import BytesIO
import base64
import mysql.connector
from flask import Flask, app, request, jsonify
from flask import render_template, session, redirect, g
from flask_restful import Resource, Api
from watermarking import embedWatermarking, checkImageWM

app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'

api = Api(app)
mydb = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="123456",
        database="attt"
    )


@app.before_request
def before_request():
    if 'user_id' in session:
        g.user_id = session['user_id']
        g.name = session['name']
        g.signature = session['signature']


@app.route('/')
def hello_world():
    return render_template('main.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    mycursor=mydb.cursor()
    if request.method=='POST':
        session.pop('user_id', None)   # !!!
        signup = request.form
        username = signup['user']
        password = signup['password']
        query = "select * from users where gmail='{}' and password='{}'".format(username, password)
        print(query)
        mycursor.execute(query)
        r = mycursor.fetchall()
        count = mycursor.rowcount
        print('r: {}'.format(r))
        if count == 1:
            mydb.commit()
            mycursor.close()
            user_infor = r[0]
            session['user_id'] = user_infor[0]
            session['name'] = user_infor[2]
            session['signature'] = user_infor[4]
            # return render_template("main.html")
            return redirect('/main')
        else:
            mydb.commit()
            mycursor.close()
            return render_template("index.html")
    else:
        return render_template('index.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return render_template('index.html')


@app.route('/main')
def main_page():
    return render_template('main.html')


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
        print('result: {}'.format(result))
        return jsonify(result=result)


api.add_resource(WaterMarkImage, '/watermark')


class GetSignature(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        base64_string = json_data['base64']
        print('base 64 string image: {}'.format(base64_string))
        result = checkImageWM(base64_string)
        if result == "The image doesn't have any sign":
            return "Signature not found", 404
        else:
            return jsonify(result=result)


api.add_resource(GetSignature, '/signature')
# main
if __name__ == '__main__':
    app.run(debug=True)
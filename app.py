import mysql.connector
from flask import Flask, app, request
from flask import render_template

app = Flask(__name__)
mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
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
        mycursor.execute("select * from users where gmail=" + username + "' and password='" + password + "'")
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
        username = signup['user']
        password = signup['password']
        # print('username: ' + username + ' password: ' + password)
        mycursor.execute("select * from users where gmail=" + username + "' and password='" + password + "'")
        r = mycursor.fetchall()
        count = mycursor.rowcount
        # tài khoản có thể sử dụng, chưa có ai đăng ký gmail này
        if count == 0:
            mycursor.execute("insert into users (gmail, password) values (" + username + ", " + password + ")")
            render_template('index.html')
        else:
            render_template('signup.html')
    mydb.commit()
    mycursor.close()

if __name__ == '__main__':
    app.run(debug=True)
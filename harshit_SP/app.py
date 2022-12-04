import hashlib
import os
import pickle
import random
import ssl
import sys
import time

import pandas as pd
import pyodbc
import redis
import rsa
# from cryptography.fernet import Fernet
from flask import Flask, render_template, request, session

# from redis.connection import NONBLOCKING_EXCEPTION_ERROR_NUMBERS, ssl_available

app = Flask(__name__)

# Set the secret key to some random bytes. Keep this really secret!
# app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# connections

# hostname = "chaitanya1001879470.database.windows.net"
# database = "chaitanya1001879470"
# username = "cdc9470"
# password ="Xperi@x!0s"
# driver= '{ODBC Driver 17 for SQL Server}'
# driver= '{SQL Server}'
# connection = pyodbc.connect('DRIVER='+driver+';PORT=1433;SERVER='+hostname+';
# PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
# cursor = connection.cursor()

hostname = "harshitsingh.database.windows.net"
database = "testdb"
username = "hxs7593"
password ="Inspicious@27"
driver= '{ODBC Driver 17 for SQL Server}'
# driver= '{SQL Server}'
connection = pyodbc.connect('DRIVER='+driver+';PORT=1433;SERVER='+hostname+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = connection.cursor()


@app.route("/")
def index():
    return render_template("login.html")


@app.route("/register", methods=['GET','POST'])
def register():
    fname = str(request.form['fname'])
    lname = str(request.form['lname'])
    uname = str(request.form['uname'])
    pwd = str(request.form['psw'])
    email = str(request.form['email'])
    cpwd= str(request.form['cpsw'])
    role=str(request.form['role'])
    encodepwd=encode(pwd)
    if pwd==cpwd:
        sql = ("Insert into Users ( fname, lname, uname, pwd, email,role,groups) values (\'" + str(fname) + "\',\'" + str(lname) + "\',\'" + str(uname) + "\',\'" + str(encodepwd) + "\',\'" + str(email) + "\',\'" + str(role) + "\','Null');")
        cursor.execute(sql)
        cursor.commit()
        message= "REGISTRATION SUCCESSFUL."
        return render_template("login.html", output= message)

    else:
        message= "Passwords must be same"
          
    return render_template("register.html", output= message)

@app.route("/registeradmin", methods=['GET','POST'])
def registeradmin():
    fname = str(request.form['fname'])
    lname = str(request.form['lname'])
    uname = str(request.form['uname'])
    pwd = str(request.form['psw'])
    email = str(request.form['email'])
    cpwd= str(request.form['cpsw'])
    role=str(request.form['role'])
    encodepwd=encode(pwd)
    currentuser=session['username']
    sql = ("select role from Users where uname =  \'" + str(currentuser) + "\';")
    print(sql)
    cursor.execute(sql)
    roleusr = cursor.fetchall()
    print(roleusr[0][0])
    if roleusr[0][0]=='Admin':
        if pwd==cpwd:
            sql = ("Insert into Users ( fname, lname, uname, pwd, email,role,groups) values (\'" + str(fname) + "\',\'" + str(lname) + "\',\'" + str(uname) + "\',\'" + str(encodepwd) + "\',\'" + str(email) + "\',\'" + str(role) + "\','Null');")
            cursor.execute(sql)
            cursor.commit()
            message= "REGISTRATION SUCCESSFUL."
            sql = ("select * from Users;")
            cursor.execute(sql)
            myOutput = cursor.fetchall()
            sql = ("select * from Users where uname not like \'" + str(currentuser) + "\' ;")
            cursor.execute(sql)
            myOutput1 = cursor.fetchall()
            return render_template("userspage.html", message= message,myOutput = myOutput,myOutput1 = myOutput1)
        else:
            message= "Passwords must be same"
            sql = ("select * from Users;")
            cursor.execute(sql)
            myOutput = cursor.fetchall()
            sql = ("select * from Users where uname not like \'" + str(currentuser) + "\' ;")
            cursor.execute(sql)
            myOutput1 = cursor.fetchall()
            return render_template("userspage.html", message= message,myOutput = myOutput,myOutput1 = myOutput1)
    else:
        message= "You are not Authorized to add user"
        sql = ("select * from Users;")
        cursor.execute(sql)
        myOutput = cursor.fetchall()
        return render_template("userspage.html", message= message,myOutput = myOutput)
          
    return render_template("userspage.html", message= message)

@app.route("/login", methods=['GET','POST'])
def login():
    session['username'] = str(request.form['uname'])
    print(session['username'])
    uname = str(request.form['uname'])
    pwd = str(request.form['psw'])
    role=str(request.form['role'])
    encodepwd=encode(pwd)
    cursor.execute("Select * from Users where uname= \'" + str(uname) + "\' and pwd=\'" + str(encodepwd) + "\' and role=\'" + str(role) + "\' ")
    count=cursor.fetchone()
    if count==None:
        return render_template("login.html", output= "Login unsucessful. Please check credentials")
    else:
        sql = ("select Comment,files,fileby from Files ORDER BY ID Desc;")
        cursor.execute(sql)
        myOutput = cursor.fetchall()
        myOutput1=[]
        for n,p,q in myOutput:
            p = ("\static\\" + str(p))
            myOutput1.append((n,p,q))
    return render_template("homepage.html", myOutput1 = myOutput1, uname=uname)


@app.route("/uploading", methods=['GET','POST'])
def addFile():
    uname= request.form['uname']
    comment = request.form['comment']
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    app.config["UPLOAD_DIR"] = os.path.join("static")
    send_dir = os.path.join(BASE_DIR, "static/")
    userFileName = ""
    for file in request.files.getlist("fileUpload"):
        fileName = file.filename
        targetFolder = "/".join([send_dir, fileName])
        file.save(targetFolder)
    sql = ("INSERT INTO Files Values (\'" + str(comment) + "\',\'" + str(fileName) + "\',\'" + str(uname) + "\')")
    print(sql)
    cursor.execute(sql)
    cursor.commit()
    sql = ("select Comment,files,fileby from Files ORDER BY ID Desc;")
    cursor.execute(sql)
    myOutput = cursor.fetchall()
    myOutput1=[]
    for n,p,q in myOutput:
        p = ("\static\\" + str(p))
        myOutput1.append((n,p,q))
    return render_template("homepage.html", message="File upload sucessful", myOutput1 = myOutput1,uname=uname)

@app.route("/homepage", methods=['GET','POST'])
def loadPage():
    sql = ("select Comment,files,fileby from Files ORDER BY ID Desc;")
    cursor.execute(sql)
    myOutput = cursor.fetchall()
    myOutput1=[]
    for n,p,q in myOutput:
        p = ("\static\\" + str(p))
        myOutput1.append((n,p,q))
    return render_template("homepage.html", myOutput1 = myOutput1)

@app.route("/loginpage", methods=['GET','POST'])
def loginPage():
    return render_template("login.html")

@app.route("/registerpage", methods=['GET','POST'])
def registerPage():
    return render_template("register.html")

@app.route("/userpage", methods=['GET','POST'])
def loadusers():
    currentuser=session['username']
    sql = ("select * from Users;")
    cursor.execute(sql)
    myOutput = cursor.fetchall()
    sql = ("select * from Users where uname not like \'" + str(currentuser) + "\' ;")
    cursor.execute(sql)
    myOutput1 = cursor.fetchall()
    return render_template("userspage.html", myOutput = myOutput, myOutput1 = myOutput1)

@app.route("/grouppage", methods=['GET','POST'])
def loadgroup():
    sql = ("select Name from Groups;")
    cursor.execute(sql)
    myOutput = cursor.fetchall()
    return render_template("grouppage.html", myOutput = myOutput)

@app.route("/addgroup", methods=['GET','POST'])
def addgroup():
    name=request.form['name']
    sql = ("Insert into Groups Values(\'" + str(name) + "\');")
    cursor.execute(sql)
    cursor.commit()
    sql = ("select Name from Groups;")
    cursor.execute(sql)
    myOutput = cursor.fetchall()
    return render_template("grouppage.html", myOutput = myOutput)

@app.route("/groupusers", methods=['GET','POST'])
def groupuser():
    grps=request.form['group']
    sql = ("select * from Users where groups like \'" + str(grps) + "\' ;")
    cursor.execute(sql)
    myOutput = cursor.fetchall()
    sql = ("select * from Users where groups not like \'" + str(grps) + "\' ;")
    cursor.execute(sql)
    myOutput1 = cursor.fetchall()
    sql = ("select * from Users where groups like \'" + str(grps) + "\' ;")
    cursor.execute(sql)
    myOutput2 = cursor.fetchall()
    return render_template("groupusers.html", myOutput = myOutput, grps=grps , myOutput1=myOutput1, myOutput2=myOutput2 )

@app.route("/logout", methods=['GET','POST'])
def logout():
    session.pop('username', None)
    return render_template("login.html")


@app.route("/addgroupuser", methods=['GET','POST'])
def addgroupuser():
    grp=request.form['grp']
    users=request.form['users']
    sql = ("Update Users SET groups = \'" + str(grp) + "\' where uname= \'" + str(users) + "\' ;")
    cursor.execute(sql)
    cursor.commit()
    sql = ("select * from Users where groups like \'" + str(grp) + "\' ;")
    cursor.execute(sql)
    myOutput = cursor.fetchall()
    sql = ("select * from Users ;")
    cursor.execute(sql)
    myOutput1 = cursor.fetchall()
    sql = ("select * from Users where groups like \'" + str(grp) + "\' ;")
    cursor.execute(sql)
    myOutput2 = cursor.fetchall()
    return render_template("groupusers.html", myOutput = myOutput, grps=grp, myOutput1=myOutput1, myOutput2=myOutput2 )

@app.route("/deletegroupuser", methods=['GET','POST'])
def delgroupuser():
    grp=request.form['grp']
    users=request.form['users']
    sql = ("Update Users SET groups = 'Null' where uname= \'" + str(users) + "\' ;")
    cursor.execute(sql)
    cursor.commit()
    sql = ("select * from Users where groups like \'" + str(grp) + "\' ;")
    cursor.execute(sql)
    myOutput = cursor.fetchall()
    sql = ("select * from Users ;")
    cursor.execute(sql)
    myOutput1 = cursor.fetchall()
    sql = ("select * from Users where groups like \'" + str(grp) + "\' ;")
    cursor.execute(sql)
    myOutput2 = cursor.fetchall()
    return render_template("groupusers.html", myOutput = myOutput, grps=grp, myOutput1=myOutput1,myOutput2=myOutput2 )

@app.route("/deleteuser", methods=['GET','POST'])
def deluser():
    currentuser=session['username']
    sql = ("select role from Users where uname =  \'" + str(currentuser) + "\';")
    print(sql)
    cursor.execute(sql)
    roleusr = cursor.fetchall()
    print(roleusr[0][0])
    if roleusr[0][0]=='Admin':
        user=request.form['users']
        sql = ("Delete from Users where uname= \'" + str(user) + "\' ;")
        print(sql)
        cursor.execute(sql)
        cursor.commit()
        sql = ("Delete from Files where fileby= \'" + str(user) + "\' ;")
        print(sql)
        cursor.execute(sql)
        cursor.commit()
        sql = ("select * from Users;")
        cursor.execute(sql)
        myOutput = cursor.fetchall()
        sql = ("select * from Users where uname not like \'" + str(currentuser) + "\'  ;")
        cursor.execute(sql)
        myOutput1 = cursor.fetchall()
        message="User deleted successfully"
    else:
        message="You are not authorized to delete the user"
        sql = ("select * from Users;")
        cursor.execute(sql)
        myOutput = cursor.fetchall()
        sql = ("select * from Users ;")
        cursor.execute(sql)
        myOutput1 = cursor.fetchall()

    return render_template("userspage.html", myOutput = myOutput, message=message, myOutput1=myOutput1 )

def encode(str):
    newstr=[]
    for i in str:       
        newstr.append(chr(ord(i)+2))
    newstr1=''.join(newstr)
    return newstr1

def decode(str):
    newstr=[]
    for i in str:        
        newstr.append(chr(ord(i)-2))
    newstr1=''.join(newstr)
    return newstr1

if __name__ == "__main__":
    app.debug=True
    app.run(host="0.0.0.0")


"""Routes for parent Flask app."""
from flask import render_template
from flask import current_app as app
from flask import Flask, flash, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
import pymongo
import bcrypt
import pandas as pd
import json
from datetime import timedelta
import sqlite3

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
conn = sqlite3.connect("./users.db")

def mongoimport17(xlsx_path, coll_name):
    """ Imports a csv file at path csv_name to a mongo colection
    returns: count of the documants in the new collection
    """
    coll = db[coll_name]
    data = pd.read_excel(xlsx_path)
    data['updated_time'] = pd.to_datetime(data['time'], format="%m/%d/%Y %H:%M:%S %p") - timedelta(hours=7)
    data.rename(columns={'temp_location1': 't', 'hum_location1': 'h', 'pm25_location1': 'pm2_5', 'aqi_location1': 'aqi'}, inplace = True)
    payload = json.loads(data.to_json(orient='records'))
    coll.insert(payload)
    return coll.count()

def grimm03(dat_path, coll_name):
    """ Imports a -M.dat file to a mongo colection
    returns: count of the documants in the new collection
    """

    coll = db[coll_name]
    data = pd.read_csv(dat_path, sep='\t', header=None, skipinitialspace=True)
    data['updated_time'] = pd.to_datetime(data['Datetime'], format="%d/%m/%Y %H:%M:%S %p") - timedelta(hours=7)
    data.rename(columns={'PM10': 'pm10', 'PM2.5': 'pm2_5','PM1': 'pm1'}, inplace=True)
    payload = json.loads(data.to_json(orient='records'))
    coll.insert(payload)
    return coll.count()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def home():
    return redirect('/dashapp/')

@app.route('/upload/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            try:
                # mongoimport17(os.path.join(app.config['UPLOAD_FOLDER'], filename), request.form['devices'])
                mongoimport17(os.path.join(app.config['UPLOAD_FOLDER'], filename), "test")
                flash('Uploaded file {} successfully'.format(filename), 'success')
                print("daa")
            except:
                flash('Uploaded file {} failed'.format(filename), 'error')
            return redirect(request.url)
        else:
            flash ('This file extension is not allowed', 'error')
            return redirect(request.url)
    else:
        if 'username' in session:
            return render_template('upload.html')
        else:
            return redirect('/login/')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect("./users.db")
        c = conn.cursor()
        c.execute("SELECT  * FROM users  WHERE email=\'"+ username+"\'" +" AND password=\'"+password+"\'")
        result = c.fetchone()
        if result is not None:
            session['username'] = request.form['username']
            return redirect('/upload/')
        else:
            flash ("Invalid username or password")
            return redirect(request.url)
    return render_template('login.html')

@app.route('/logout/')
def logout():
    del session['username']
    return redirect('/dashapp/')

@app.errorhandler(404)
def page_not_found(e):
    return redirect("/")

@app.errorhandler(500)
def interal_server(e):
    return redirect("/")
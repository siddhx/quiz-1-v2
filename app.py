# Siddharth Agarwal
# 1001577570
# CSE 6331
# Assignment 2
# references:


import os
import sqlite3
from pprint import pprint
import pandas
from flask import Flask, jsonify, request, render_template, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
# from flask_restful import Api, Resource
# from flask_uploads import UploadSet, configure_uploads, IMAGES
app = Flask(__name__,  template_folder='templates')
app.secret_key = "7570"

uploadFolder = 'static/images'
allowedExtensions = set(['png', 'jpg', 'jpeg', 'gif'])

app.config['uploadFolder'] = uploadFolder
# photos = UploadSet('photos', IMAGES)
# api = Api(app)
db = "earthquake.db"
def allowed_file(fname):
    return '.' in fname and \
    fname.rsplit('.', 1)[1].lower() in allowedExtensions

# Search for and count all earthquakes that occurred with a magnitude greater than 5.0
@app.route('/search/earthquake/bymagnitude', methods=['GET', 'POST'])
def searchByMag():
    if request.method == 'GET':
        return render_template('magnitude.html')
    if request.method == 'POST' :
        if 'lower' not in request.form or 'upper' not in request.form:
            flash('No range given')
            return redirect(request.url)
            # result = ["no photo found, please upload again"]
            # return jsonify(results=result)
        else:
            connection = sqlite3.connect(db)
            cursor = connection.cursor()
            lower = request.form['lower']
            upper = request.form['upper']
            # print (instructor)
            # query = "select course,section,room from student where instructor='Kashefi'"
            query = "SELECT * from  earthquake_data where mag between ? and ?"
            # query = "SELECT * from  earthquake_data where mag between{} and {}".format(lower,upper)
            print(query)
            # query2 = "SELECT name,picture FROM student where grade=98"
            cursor.execute(query, (lower, upper))
            results = cursor.fetchall()
            connection.close()
            return render_template('magnitude.html',results=results, size=len(results))
            # return jsonify(results=results)


@app.route('/search/range', methods=['GET', 'POST'])
def searchRange():
    if request.method == 'GET':
        return render_template('range.html')
    if request.method == 'POST' :
        if 'instructor' not in request.form:
            flash('No range given')
            return redirect(request.url)
            # result = ["no photo found, please upload again"]
            # return jsonify(results=result)
        else:
            connection = sqlite3.connect("people.db")
            cursor = connection.cursor()
            lower = request.form['lower']
            upper = request.form['upper']
            # print (instructor)
            # query = "select course,section,room from student where instructor='Kashefi'"
            query = "select * from student where course >"+lower  + "and course < " +upper
            # query2 = "SELECT name,picture FROM student where grade=98"
            cursor.execute(query)
            results = cursor.fetchall()
            connection.close()
            return render_template('detail.html',results=results)
            # return jsonify(results=results)

@app.route('/search/detail', methods=['GET', 'POST'])
def searchDetail():
    if request.method == 'GET':
        return render_template('detail.html')
    if request.method == 'POST' :
        if 'instructor' not in request.form:
            flash('No course given')
            return redirect(request.url)
            # result = ["no photo found, please upload again"]
            # return jsonify(results=result)
        else:
            connection = sqlite3.connect("people.db")
            cursor = connection.cursor()
            instructor = request.form['instructor']
            # print (instructor)
            # query = "select course,section,room from student where instructor='Kashefi'"
            query = "select course,section,room from student where instructor="+"'"+request.form['instructor'] +"'"
            # query2 = "SELECT name,picture FROM student where grade=98"
            cursor.execute(query)
            results = cursor.fetchall()
            connection.close()
            return render_template('detail.html',results=results)
            # return jsonify(results=results)

@app.route('/search/instructor', methods=['GET', 'POST'])
def searchInstructor():
    if request.method == 'GET':
        return render_template('searchinstructor.html')
    if request.method == 'POST' :
        if 'course' not in request.form:
            flash('No course given')
            return redirect(request.url)
            # result = ["no photo found, please upload again"]
            # return jsonify(results=result)
        else:
            connection = sqlite3.connect("people.db")
            cursor = connection.cursor()

            query = "select instructor from student where Course = {0} distinct".format(int(request.form['course']))
            # query2 = "SELECT name,picture FROM student where grade=98"
            cursor.execute(query)
            results = cursor.fetchall()
            connection.close()

            return jsonify(results=results)

@app.route('/greeting')
def greeting():
    return render_template('greeting.html')

# @app.route('/')
# def home():
#     return render_template('uploadcsv.html')

@app.route('/uploadpicbyname', methods=['GET', 'POST'])
def uploadpic():
    if request.method == 'GET':
        connection = sqlite3.connect("people.db")
        cursor = connection.cursor()
        query = "SELECT name FROM student"
        # query2 = "SELECT name,picture FROM student where grade=98"
        cursor.execute(query)
        results = cursor.fetchall()
        connection.close()

        return render_template('uploadpic.html', names = results)

    if request.method == 'POST' :
        if 'photo' not in request.files:
            flash('No photo found')
            return redirect(request.url)
            # result = ["no photo found, please upload again"]
            # return jsonify(results=result)
        photo = request.files['photo']
        if photo.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['uploadFolder'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['uploadFolder'],
                               filename)

@app.route('/api/createcsv', methods=['GET', 'POST'])
def csv():
    db = "earthquake.db"
    connection = sqlite3.connect(db)
    cursor = connection.cursor()

    table_name = "earthquake_data"
    if request.method == 'POST':
        if 'csv' not in request.files:
            result = ["no file found, please upload again"]
            return jsonify(results=result)
        else:
            file = request.files['csv']
            df = pandas.read_csv(file.stream)
            df.to_sql(table_name, connection, if_exists='append', index=False)

            query = "SELECT * FROM " + table_name
            # # query2 = "SELECT name,picture FROM student where grade=98"
            cursor.execute(query)
            results = cursor.fetchall()
            connection.close()
            return render_template('displaydbdata.html', data = results, size=len(results))
            # return jsonify(results=df.to_json())

    if request.method == 'GET':
        queryTable = "SELECT name FROM sqlite_master WHERE type='table' AND name="+"'"+table_name+"'"
        cursor.execute(queryTable)
        results = cursor.fetchall()
        # print(results)
        for item in results:
            if table_name in item:
                # return jsonify(table=results)
                query = "SELECT * FROM " + table_name
                # # query2 = "SELECT name,picture FROM student where grade=98"
                cursor.execute(query)
                results = cursor.fetchall()
                connection.close()
                return render_template('displaydbdata.html', data = results, size=len(results))
        return render_template('displaydbdata.html')
port = os.getenv('PORT', '5000')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))

# Siddharth Agarwal
# 1001577570
# CSE 6331
# Assignment 2

# Design considerations:

# using sqlite3 for storing the data from the csv file, and using flask framework to
# build a small CRUD application whith machine learning capabilities with scipy, scikit-learn and data manupulation with pandas and numpy.

# references:

# -https://github.com/abrookins/siren/blob/master/siren/crime_tracker.py
# -https://stackoverflow.com/questions/32424604/find-all-nearest-neighbors-within-a-specific-distance
# -https://github.com/gboeing/data-visualization/blob/master/location-history/google-location-history-cluster.ipynb
# -https://github.com/gboeing/2014-summer-travels/blob/master/clustering-scikitlearn.ipynb
# -https://mubaris.com/2017/10/01/kmeans-clustering-in-python/

import os
import sqlite3
from pprint import pprint
import pandas as pd
from scipy.spatial import cKDTree
from scipy import inf
# import matplotlib.pyplot as plt
import numpy as np
from pandas import DataFrame
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial import cKDTree
from flask import Flask, jsonify, request, render_template, redirect, url_for,  flash, send_from_directory, send_file
from werkzeug.utils import secure_filename

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

def findDayOrNight(row):
    if row['hours'] < 6 and row['hours'] >= 0:
        return 'night'
    if row['hours'] <= 24 and row['hours'] >= 22:
        return 'night'
    else:
        return 'day'

@app.route('/search/earthquake/bydayornight', methods=['GET', 'POST'])
def searchByDayOrNight():
    if request.method == 'GET':
        return render_template('dayornight.html')

    if request.method == 'POST' :
        df = pd.read_csv('./edata.csv')
        magnitude = float(request.form['magnitude'])
        df['time'] = pd.to_datetime(df['time'])
        df = df.set_index('time')
        df['hours'] = df.index.hour
        df['dayOrNight'] = df.apply(findDayOrNight, axis=1)
        df_mag = df.loc[df['mag'] >= magnitude]
        results = [df_mag['dayOrNight'].value_counts().to_dict()]
        print(results)

        return render_template('dayornight.html',results=results)

@app.route('/search/earthquake/bycluster', methods=['GET', 'POST'])
def searchByCluster():
    if request.method == 'GET':
        data = pd.read_csv('./edata.csv')

        f1 = data['latitude'].values
        f2 = data['longitude'].values
        f3 = data['depth'].values
        X = np.array(list(zip(f1, f2, f3)))
        fig = plt.figure()
        ax = Axes3D(fig)
        ax.scatter(X[:, 0], X[:, 1], X[:, 2])
        fig.savefig('./cluster.jpg')
        filename = 'cluster.jpg'

        return send_file(filename, mimetype='image/gif')
        # return render_template('cluster.html')
    if request.method == 'POST' :
        return "nothing to post, its a get page only!"


@app.route('/search/earthquake/withindistance', methods=['GET', 'POST'])
def searchByDistance():
    if request.method == 'GET':
        return render_template('distance.html')
    if request.method == 'POST' :

        df = pd.read_csv('./edata.csv')
        latitude = float(request.form['latitude'])
        longitude = float(request.form['longitude'])
        distance = float(request.form['distance'])
        miles = 6.21371*(distance)
        distance = 0.01*miles
        point = [latitude,longitude]
        points = {}
        for row in df.itertuples():
        # for index, row in df.iterrows():
            points.update({(row.latitude, row.longitude): [row.time, row.mag, row.place ] })

        quakes_kdtree = cKDTree([*points.keys()])

        distances, indices = quakes_kdtree.query(point,k=5000, distance_upper_bound=distance)

        nearby_earthquakes_coordinates = []
        for index, max_points in zip(indices.tolist(),distances):
            if max_points == inf:
                break
            nearby_earthquakes_coordinates.append([*points.keys()][index])
        results = [points[x] for x in nearby_earthquakes_coordinates]
        results_list = pd.DataFrame(results)
        header = ['timestamp','mag','place']
        results_list.rename(columns = header)
        print(results_list.dtypes)
        results = results_list.sort_values(by='mag', ascending=True)
        # print(results_list)
        return render_template('distance.html',results=results, size=len(results))
        # else:

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
            # query = "select course,section,room from student where instructor='Kashefi'"
            if request.form != '' and request.form !='':
                lowerDate = request.form['lowerDate']
                upperDate = request.form['upperDate']
                query = "SELECT * FROM earthquake_data WHERE time between ? and ? and mag between ? and ?";
                cursor.execute(query, (lowerDate, upperDate, lower, upper))
                results = cursor.fetchall()
                connection.close()
                return render_template('magnitude.html',results=results, size=len(results))
            connection = sqlite3.connect(db)
            cursor = connection.cursor()
            print ("here1989")

            query = "SELECT * from  earthquake_data where mag between ? and ?"
            # query = "SELECT * from  earthquake_data where mag between{} and {}".format(lower,upper)
            print(query)
            # query2 = "SELECT name,picture FROM student where grade=98"
            cursor.execute(query, (lower, upper))
            results = cursor.fetchall()
            connection.close()
            return render_template('magnitude.html',results=results, size=len(results))
            # return jsonify(results=results)


# @app.route('/search/range', methods=['GET', 'POST'])
# def searchRange():
#     if request.method == 'GET':
#         return render_template('range.html')
#     if request.method == 'POST' :
#         if 'instructor' not in request.form:
#             flash('No range given')
#             return redirect(request.url)
#             # result = ["no photo found, please upload again"]
#             # return jsonify(results=result)
#         else:
#             connection = sqlite3.connect("people.db")
#             cursor = connection.cursor()
#             lower = request.form['lower']
#             upper = request.form['upper']
#             # print (instructor)
#             # query = "select course,section,room from student where instructor='Kashefi'"
#             query = "select * from student where course >"+lower  + "and course < " +upper
#             # query2 = "SELECT name,picture FROM student where grade=98"
#             cursor.execute(query)
#             results = cursor.fetchall()
#             connection.close()
#             return render_template('detail.html',results=results)
#             # return jsonify(results=results)

# @app.route('/search/detail', methods=['GET', 'POST'])
# def searchDetail():
#     if request.method == 'GET':
#         return render_template('detail.html')
#     if request.method == 'POST' :
#         if 'instructor' not in request.form:
#             flash('No course given')
#             return redirect(request.url)
#             # result = ["no photo found, please upload again"]
#             # return jsonify(results=result)
#         else:
#             connection = sqlite3.connect("people.db")
#             cursor = connection.cursor()
#             instructor = request.form['instructor']
#             # print (instructor)
#             # query = "select course,section,room from student where instructor='Kashefi'"
#             query = "select course,section,room from student where instructor="+"'"+request.form['instructor'] +"'"
#             # query2 = "SELECT name,picture FROM student where grade=98"
#             cursor.execute(query)
#             results = cursor.fetchall()
#             connection.close()
#             return render_template('detail.html',results=results)
#             # return jsonify(results=results)

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
            df = pd.read_csv(file.stream)
            df.to_sql(table_name, connection, if_exists='replace', index=False)

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

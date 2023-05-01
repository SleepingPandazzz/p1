from flask import Flask, jsonify
import pandas as pd
import mysql.connector

rest_app = Flask(__name__)

connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='HelloWorld123!',
    database='academicworld'
)

@rest_app.route('/favorite_faculties')
def get_favorite_faculties():
    query = ("SELECT f.name AS faculty_name, ff.comment AS comment, f.id AS id FROM favorite_faculty ff "
            "INNER JOIN faculty f ON f.id = ff.faculty_id "
            "WHERE deleted = 0")
    cursor = connection.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    result = []
    for row in data:
      d = dict(zip(cursor.column_names, row))
      result.append(d)
    cursor.close()
    return jsonify(result)

@rest_app.route('/university_ids/<keyword>/<int:page>')
def get_university_ids(keyword, page):
    query = ("SELECT SUM(fk.score) AS total_score, u.id, u.name FROM university u "
             "LEFT JOIN faculty f ON f.university_id = u.id "
             "LEFT JOIN faculty_keyword fk ON fk.faculty_id = f.id "
             "LEFT JOIN keyword k ON k.id = fk.keyword_id "
             "WHERE k.name = %s "
             "GROUP BY f.id "
             "ORDER BY total_score DESC LIMIT 15 OFFSET %s")
    offset = (page - 1) * 15
    cursor = connection.cursor()
    cursor.execute(query, (keyword, offset))
    du = cursor.fetchall()
    university_ids = []
    for (total_score, id, name) in du:
      university_ids.append("i" + str(id))
    cursor.close()
    return jsonify(university_ids)


@rest_app.route('/universities/<keyword>/<int:page>')
def get_universities_filtered_by_keyword(keyword, page):
    query = ("SELECT SUM(fk.score) AS total_score, u.id, u.name FROM university u "
             "LEFT JOIN faculty f ON f.university_id = u.id "
             "LEFT JOIN faculty_keyword fk ON fk.faculty_id = f.id "
             "LEFT JOIN keyword k ON k.id = fk.keyword_id "
             "WHERE k.name = %s "
             "GROUP BY f.id "
             "ORDER BY total_score DESC LIMIT 15 OFFSET %s")
    cursor = connection.cursor()
    offset = (page - 1) * 15
    cursor.execute(query, (keyword, offset))
    data = cursor.fetchall()
    result = []
    for row in data:
      d = dict(zip(cursor.column_names, row))
      result.append(d)
    cursor.close()
    return jsonify(result)


@rest_app.route('/publications/<keyword>/<int:page>')
def get_paged_publications_filtered_by_keyword(keyword, page):
  query = ("SELECT SUM(pk.score) AS total_score, p.title, p.venue, p.year, p.num_citations, p.id FROM publication p "
           "LEFT JOIN publication_keyword pk ON pk.publication_id = p.id "
           "LEFT JOIN keyword k ON k.id = pk.keyword_id "
           "WHERE k.name = %s "
           "GROUP BY p.id "
           "ORDER BY total_score DESC limit 15 OFFSET %s")
  cursor = connection.cursor()
  offset = (page - 1) * 15
  cursor.execute(query, (keyword, offset))
  data = cursor.fetchall()
  result = []
  for row in data:
     d = dict(zip(cursor.column_names, row))
     result.append(d)
  cursor.close()
  return jsonify(result)


@rest_app.route('/faculties/<keyword>/<int:page>')
def get_paged_faculties_filterd_by_keyword(keyword, page):
  query = ("SELECT SUM(fk.score) AS total_score, f.name AS faculty_name, f.position, u.name AS university_name, f.research_interest, f.email, f.phone, f.photo_url, f.id, ff.deleted FROM faculty f "
           "LEFT JOIN faculty_keyword fk ON fk.faculty_id = f.id "
           "LEFT JOIN keyword k ON k.id = fk.keyword_id "
           "LEFT JOIN university u ON u.id = f.university_id "
           "LEFT JOIN favorite_faculty ff ON f.id = ff.faculty_id "
           "WHERE k.name = %s "
           "GROUP BY f.id "
           "ORDER BY total_score DESC LIMIT 15 OFFSET %s")
  offset = (page - 1) * 15
  cursor = connection.cursor()
  cursor.execute(query, (keyword, offset))
  data = cursor.fetchall()
  result = []
  for row in data:
     d = dict(zip(cursor.column_names, row))
     result.append(d)
  cursor.close()
  return jsonify(result)


@rest_app.route('/')
def gjoeigre():
  return 'wefaofjewof'


if __name__ == '__main__':
    rest_app.run(debug=False, port=9003)

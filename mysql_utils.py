import mysql.connector
import pandas as pd
import secret_keys


class MysqlUtils:
  def __init__(self):
    self.connection = mysql.connector.connect(
        host=secret_keys.MYSQL_DB_HOST,
        user=secret_keys.MYSQL_DB_USER,
        password=secret_keys.MYSQL_DB_PASSWORD,
        database=secret_keys.MYSQL_DB_DATABASE
    )

  def get_faculty_table_data(self, value):
    query = ("SELECT SUM(fk.score) AS total_score, f.name AS faculty_name, f.position, u.name AS university_name, f.research_interest, f.email, f.phone, f.photo_url, f.id, ff.deleted FROM faculty f "
             "LEFT JOIN faculty_keyword fk ON fk.faculty_id = f.id "
             "LEFT JOIN keyword k ON k.id = fk.keyword_id "
             "LEFT JOIN university u ON u.id = f.university_id "
             "LEFT JOIN favorite_faculty ff ON f.id = ff.faculty_id "
             "WHERE k.name = %s "
             "GROUP BY f.id "
             "ORDER BY total_score DESC limit 15")
    cursor = self.connection.cursor()
    cursor.execute(query, (value, ))
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=cursor.column_names)
    df['rank'] = df['total_score'].rank(method='min', ascending=False)
    cursor.close()
    return df

  def set_faculty_as_favorite(self, faculty_id):
    query = ("INSERT INTO favorite_faculty(faculty_id, comment, deleted) "
             "VALUES (%s, %s, %s) "
             "ON DUPLICATE KEY UPDATE deleted=False")
    val = (faculty_id, "", False)
    cursor = self.connection.cursor()
    cursor.execute(query, val)
    self.connection.commit()
    cursor.close()

  def update_favorite_faculty(self, comment, id):
    query = 'UPDATE favorite_faculty SET comment = %s WHERE faculty_id = %s'
    val = (comment, id)
    cursor = self.connection.cursor()
    cursor.execute(query, val)
    self.connection.commit()
    cursor.close()

  def delete_faculty(self, faculty_id):
    query = 'DELETE faculty WHERE id = %s'
    val = (faculty_id, )
    cursor = self.connection.cursor()
    cursor.execute(query, val)
    self.connection.commit()
    cursor.close()

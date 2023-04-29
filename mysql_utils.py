import mysql.connector
import pandas as pd

class MysqlUtils:
  def __init__(self):
    self.connection = mysql.connector.connect(
                        host = 'localhost',
                        user = 'root',
                        password = 'HelloWorld123!',
                        database = 'academicworld'
                      )
  
  def execute_query(self, query):
    cursor = self.connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    return result
  
  def execute_query_with_value(self, query, value):
    cursor = self.connection.cursor()
    cursor.execute(query, (value, ))
    result = cursor.fetchall()
    cursor.close()
    return result

  def execute_query_for_table_without_value(self, query):
    cursor = self.connection.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    table = pd.DataFrame(data, columns=cursor.column_names)
    cursor.close()
    return table

  def execute_query_for_table(self, query, value):
    cursor = self.connection.cursor()
    cursor.execute(query, (value, ))
    data = cursor.fetchall()
    table = pd.DataFrame(data, columns=cursor.column_names)
    cursor.close()
    return table
  
  def insert(self, query, value):
    cursor = self.connection.cursor()
    cursor.execute(query, value)
    self.connection.commit()
    cursor.close()
  
  def update(self, query, value):
    cursor = self.connection.cursor()
    cursor.execute(query, value)
    self.connection.commit()
    cursor.close()
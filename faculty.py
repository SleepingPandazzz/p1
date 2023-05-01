import requests
import json
import pandas as pd

class Faculty:
  def get_paged_faculty_by_keyword(self, keyword, page):
    url = "http://localhost:9003/faculties/" + keyword.replace(' ', '%20') + "/" + str(page)
    response = requests.get(url)
    if response.status_code == 200:
      data = json.loads(response.content)
      df = pd.DataFrame(data)
      df = pd.DataFrame(data, columns=['total_score', 'faculty_name', 'position', 'university_name', 'research_interest', 'email', 'photo', 'photo_url', 'id', 'deleted'])
      df['rank'] = df['total_score'].rank(method='min', ascending=False)
      return df
    else:
      print('Error: ', response.status_code)

  def get_favorite_faculties(self):
    url = "http://localhost:9003/favorite_faculties"
    response = requests.get(url)
    if response.status_code == 200:
      data = json.loads(response.content)
      df = pd.DataFrame(data)
      df = pd.DataFrame(data, columns=['faculty_name', 'comment', 'id'])
      return df
    else:
      print('Error: ', response.status_code)
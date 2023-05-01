import requests
import json
import pandas as pd


class University:
    def get_unievrsities_by_keyword(self, keyword, page):
      url = "http://localhost:9003/universities/" + \
          keyword.replace(' ', '%20') + "/" + str(page)
      response = requests.get(url)
      if response.status_code == 200:
        data = json.loads(response.content)
        df = pd.DataFrame(data)
        df = pd.DataFrame(data, columns=['total_score', 'id', 'name'])
        df['rank'] = df['total_score'].rank(method='min', ascending=False)
        return df
      else:
        print('Error: ', response.status_code)

    def get_university_ids_by_keyword(self, keyword, page):
      url = "http://localhost:9003/university_ids/" + \
      keyword.replace(' ', '%20') + "/" + str(page)
      response = requests.get(url)
      if response.status_code == 200:
        data = json.loads(response.content)
        return data
      else:
        print('Error: ', response.status_code) 
import requests
import json
import pandas as pd


class Publication:
    def get_publications_by_keyword(self, keyword, page):
      url = "http://localhost:9003/publications/" + \
          keyword.replace(' ', '%20') + "/" + str(page)
      response = requests.get(url)
      if response.status_code == 200:
        data = json.loads(response.content)
        df = pd.DataFrame(data)
        df = pd.DataFrame(data, columns=['total_score', 'title', 'vernue',
                          'year', 'num_citations', 'id'])
        df['rank'] = df['total_score'].rank(method='min', ascending=False)
        return df
      else:
        print('Error: ', response.status_code)

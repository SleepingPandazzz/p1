from dash import Dash, html, dcc, callback, Output, Input
import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import mysql_utils
import mongodb_utils
import neo4j_utils
import dash_table
import plotly.graph_objects as go
import geopandas as gpd
import csv
import numpy as np

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
custom_stylesheets = ['assets/style.css']
app = Dash(__name__, external_stylesheets=[
           dbc.themes.BOOTSTRAP, dbc_css, custom_stylesheets])
mysql = mysql_utils.MysqlUtils()
mapbox_access_token = 'your-mapbox-access-token'
mongosql = mongodb_utils.MyMongoDbUtils()
neo4jsql = neo4j_utils.Neo4jDbUtils()


def get_keywords():
  with neo4jsql.driver.session() as session:
    results = session.run(
        "MATCH (k:KEYWORD) RETURN k.name AS name ORDER BY k.name")
    data = results.data()
    keywords = []
    for (keyword) in data:
      keywords.append(keyword.get('name').title())

  # result = mysql.execute_query(f"SELECT * FROM keyword ORDER BY name")
  # keywords = []
  # for (_id, name) in result:
  #   keywords.append(name.title())
  return keywords


header_layout = html.Div([
    html.H1(children='Explore Keywords', style={
            'textAlign': 'center', 'margin': '50px'}),
    html.Div([
        html.Div([
            html.H5(children='Select a Keyword:'),
            dcc.Dropdown(get_keywords(), 'Computer Science',
                         id='keyword-dropdown-selection'),
        ], style={'width': '55vw', 'margin': '0 auto'}, className='container'),
    ], style={'margin-top': '30px'}, className='center')
], style={'display': 'flex'})

tab_layout = html.Div(
    [
        dbc.Tabs(
            [
                dbc.Tab(html.Table(id='university-output'), label="Top Universities", tab_id="university-tab",
                        tab_style={'margin': '0 auto', 'width': '300px', 'text-align': 'center'}),
                dbc.Tab(html.Table(id='faculty-output'), label="Top Faculties", tab_id="faculty-tab",
                        tab_style={'margin': '0 auto', 'width': '300px', 'text-align': 'center'}),
                dbc.Tab(html.Table(id='publication-output'), label="Top Publications", tab_id="publication-tab",
                        tab_style={'margin': '0 auto', 'width': '300px', 'text-align': 'center'}),
            ],
            id="tabs",
            active_tab="university-tab",
            style={'font-size': '18px', 'margin': '30px 60px'}
        ),
        html.Div(id="content"),
    ]
)

app.layout = html.Div([
    html.Div(children=header_layout),
    html.Div(children=tab_layout),
])


def get_faculty_table_data(value):
  query = ("SELECT SUM(fk.score) AS total_score, f.name AS faculty_name, f.position, u.name AS university_name, f.research_interest, f.email, f.phone, f.photo_url, f.id, ff.deleted FROM faculty f "
           "LEFT JOIN faculty_keyword fk ON fk.faculty_id = f.id "
           "LEFT JOIN keyword k ON k.id = fk.keyword_id "
           "LEFT JOIN university u ON u.id = f.university_id "
           "LEFT JOIN favorite_faculty ff ON f.id = ff.faculty_id "
           "WHERE k.name = %s "
           "GROUP BY f.id "
           "ORDER BY total_score DESC LIMIT 10")
  df = mysql.execute_query_for_table(query, value)
  df['rank'] = df['total_score'].rank(method='min', ascending=False)
  return df


def get_publication_table_data(value):
  query = ("SELECT SUM(pk.score) AS total_score, p.title, p.venue, p.year, p.num_citations FROM publication p "
           "LEFT JOIN publication_keyword pk ON pk.publication_id = p.id "
           "LEFT JOIN keyword k ON k.id = pk.keyword_id "
           "WHERE k.name = %s "
           "GROUP BY p.id "
           "ORDER BY total_score DESC limit 10")
  dp = mysql.execute_query_for_table(query, value)
  dp['rank'] = dp['total_score'].rank(method='min', ascending=False)
  return dp


def get_favorite_faculty_table_data():
  query = ("SELECT f.name AS faculty_name, ff.comment AS comment, f.id AS id FROM favorite_faculty ff "
           "INNER JOIN faculty f ON f.id = ff.faculty_id "
           "WHERE deleted = 0")
  dp = mysql.execute_query_for_table_without_value(query)
  return dp


def get_university_ids(value):
  query = ("SELECT SUM(fk.score) AS total_score, u.id, u.name FROM university u "
           "LEFT JOIN faculty f ON f.university_id = u.id "
           "LEFT JOIN faculty_keyword fk ON fk.faculty_id = f.id "
           "LEFT JOIN keyword k ON k.id = fk.keyword_id "
           "WHERE k.name = %s "
           "GROUP BY f.id "
           "ORDER BY total_score DESC limit 10")
  du = mysql.execute_query_with_value(query, value)

  university_ids = []
  for (total_score, id, name) in du:
    university_ids.append(id)
  return university_ids


def get_universities_table_data(value):
  query = ("SELECT SUM(fk.score) AS total_score, u.id, u.name FROM university u "
           "LEFT JOIN faculty f ON f.university_id = u.id "
           "LEFT JOIN faculty_keyword fk ON fk.faculty_id = f.id "
           "LEFT JOIN keyword k ON k.id = fk.keyword_id "
           "WHERE k.name = %s "
           "GROUP BY f.id "
           "ORDER BY total_score DESC limit 10")
  dut = mysql.execute_query_for_table(query, value)
  dut['rank'] = dut['total_score'].rank(method='min', ascending=False)
  return dut


def set_faculty_as_favorite(faculty_id):
  query = ("INSERT INTO favorite_faculty(faculty_id, comment, deleted) "
           "VALUES (%s, %s, %s) "
           "ON DUPLICATE KEY UPDATE deleted=False")
  val = (faculty_id, "", False)
  mysql.insert(query, val)


@callback(
    [Output('university-output', 'children'), Output('faculty-output',
                                                     'children'), Output('publication-output', 'children')],
    Input('keyword-dropdown-selection', 'value')
)
def update_output_div(value):
  df = get_faculty_table_data(value)
  dp = get_publication_table_data(value)
  dut = get_universities_table_data(value)
  ff = get_favorite_faculty_table_data()

  du_plot_tmp = pd.read_csv('universities.csv')
  du_plot_tmp.head()

  university_ids = get_university_ids(value)
  filtered_du = du_plot_tmp[np.isin(
      du_plot_tmp['university_id'], np.array(university_ids))]

  return html.Div(
      children=[
          dcc.Graph(
              id='map',
              figure=px.scatter_mapbox(filtered_du,
                                       lat="latitude",
                                       lon="longitude",
                                       hover_name='name',
                                       zoom=3,
                                       mapbox_style='open-street-map'),
              style={'width': '70vw'}
          ),
          dash_table.DataTable(
              id='university-table',
              columns=[
                  {'name': 'RANK', 'id': 'rank'},
                  {'name': 'NAME', 'id': 'name'},
              ],
              data=dut.to_dict('records'),
              editable=False,
              style_as_list_view=True,
              style_cell={'padding': '5px',
                          'text-align': 'center',
                          'white-space': 'initial'},
              style_header={
                  'backgroundColor': 'white',
                  'fontWeight': 'bold'
              },
              style_table={
                  'width': '27vw',
                  'margin-left': '1vw'
              },
              style_data_conditional=[
                  {
                      'if': {'row_index': 'odd'},
                      'backgroundColor': 'rgb(248, 248, 248)'
                  },
                  {
                      'if': {'row_index': 'even'},
                      'backgroundColor': 'white'
                  }
              ]
          )
      ], style={'margin': '0 1vw', 'display': 'flex', 'minHeight': '500px'}
  ), html.Div([
      html.Div([
          html.H5(children='Top Faculties Based on the Selected Keyword',
              className='text-center'),
          html.Div([
              html.Div(id='save-faculty-output'),
              html.P(
                  '* Click the corresponding radio button to view details about each professor.'),
              dash_table.DataTable(
                  id='faculty-table',
                  columns=[
                      {'name': 'SCORE', 'id': 'total_score'},
                      {'name': 'NAME', 'id': 'faculty_name'},
                      {'name': 'UNIVERSITY', 'id': 'university_name'},
                  ],
                  data=df.to_dict('records'),
                  editable=False,
                  cell_selectable=False,
                  row_selectable="single",
                  style_as_list_view=True,
                  selected_rows=[0],
                  style_cell={'padding': '5px',
                              'text-align': 'center',
                              'width': '100px',
                              'minWidth': '100px',
                              'maxWidth': '100px',
                              'white-space': 'initial'},
                  style_header={
                      'backgroundColor': 'white',
                      'fontWeight': 'bold'
                  },
                  style_table={
                      'width': '70vw',
                      'margin': '0 1vw',
                      'display': 'flex',
                      'float': 'left',
                  },
                  style_data_conditional=[
                      {
                          'if': {'row_index': 'odd'},
                          'backgroundColor': 'rgb(248, 248, 248)'
                      },
                      {
                          'if': {'row_index': 'even'},
                          'backgroundColor': 'white'
                      }
                  ]
              ),
              html.Div(id='test-output'),
          ]),
      ], style={'width': '100vw'}
      ), html.Div([
          html.H5(children='View Your Favorite Faculties',
                  className='text-center', style={'margin-top': '30px'}),
          html.P('* Support inline saving', style={'text-align': 'center'}),
          dash_table.DataTable(
              id='favorite-faculty-table',
              columns=[
                  {'name': 'id', 'id': 'id', 'editable': False},
                  {'name': 'FACULTY NAME',
                   'id': 'faculty_name', 'editable': False},
                  {'name': 'COMMENT', 'id': 'comment', 'editable': True}
              ],
              data=ff.to_dict('records'),
              editable=True,
              style_as_list_view=True,
              style_cell={'padding': '5px',
                          'text-align': 'center',
                          'minWidth': '100px',
                          'white-space': 'initial'},
              style_header={
                  'backgroundColor': 'white',
                  'fontWeight': 'bold'
              },
              style_table={
                  'width': '70vw',
                  'margin': '0 1vw',
                  'display': 'flex',
                  'margin': '0 auto',
              },
              style_data_conditional=[
                  {
                      'if': {'row_index': 'odd'},
                      'backgroundColor': 'rgb(248, 248, 248)'
                  },
                  {
                      'if': {'row_index': 'even'},
                      'backgroundColor': 'white'
                  },
              ]
          )
      ])
  ]), html.Div([
      html.H5(children='Top Publications Based on the Selected Keyword',
              className='text-center'),
      dash_table.DataTable(
          id='publication-table',
          columns=[
              {'name': 'RANK', 'id': 'rank'},
              {'name': 'TITLE', 'id': 'title'},
              {'name': 'VENUE', 'id': 'venue'},
              {'name': 'YEAR', 'id': 'year'},
              {'name': 'NUM CITATIONS', 'id': 'num_citations'},
          ],
          data=dp.to_dict('records'),
          editable=False,
          style_as_list_view=True,
          style_cell={'padding': '5px',
                      'text-align': 'center',
                      'width': '100px',
                      'minWidth': '100px',
                      'maxWidth': '100px',
                      'white-space': 'initial'},
          style_header={
              'backgroundColor': 'white',
              'fontWeight': 'bold'
          },
          style_table={
              'width': '70%',
              'margin': '0 auto'
          },
          style_data_conditional=[
              {
                  'if': {'row_index': 'odd'},
                  'backgroundColor': 'rgb(248, 248, 248)'
              },
              {
                  'if': {'row_index': 'even'},
                  'backgroundColor': 'white'
              }
          ]
      )
  ], style={'width': '100vw'})


@callback(
    dash.dependencies.Output('favorite-faculty-table', 'output'),
    # [dash.dependencies.Input('favorite-faculty-table', 'data')],
    Input('favorite-faculty-table', 'data')
)
def update_data(data):
    for row in data:
       if all([cell != '' for cell in row.values()]):
          query = 'UPDATE favorite_faculty SET comment = %s WHERE faculty_id = %s'
          val = (row.get('comment'), row.get('id'))
          mysql.update(query, val)

    ff = get_favorite_faculty_table_data()
    return ff.to_dict('records')


@callback(
    Output('test-output', 'children'),
    Input('faculty-table', 'selected_rows'),
    Input('faculty-table', 'data'))
def display_data(selected_rows, data):
    if selected_rows is None:
        return ''
    else:
        df = data[selected_rows[0]]
        return html.Div([
            dbc.Card(
                [
                    dbc.CardImg(src=df.get('photo_url'), top=True) if df.get(
                        'photo_url') else '',
                    dbc.CardBody(
                        [
                            html.H4(df.get('faculty_name'),
                                    className="card-title"),
                            html.Div([
                                html.P(df.get('position') + " at " +
                                     df.get('university_name'), style={'margin-bottom': 0}),
                                html.Br(),
                                html.P("Research Interest: " +
                                     df.get('research_interest'), style={'margin-bottom': 0}),
                                html.Br(),
                                html.P(df.get('email'), style={
                                    'margin-bottom': 0}),
                                html.P(df.get('phone'), style={
                                    'margin-bottom': 0}),
                                html.Br(),
                            ], className='card-text'),
                            html.Div(dbc.Button("Save As My Favorite", color="primary", id='save-faculty-btn', n_clicks=0), id='save-btn-container') if df.get(
                                'deleted') != 0 else dbc.Badge("Favorited", color="white", text_color="danger", className="border me-1")
                        ]
                    ),
                ], style={"width": "20rem", 'margin': '0 auto'}, id='faculty-card'
            )
        ])


@callback(
    dash.dependencies.Output('faculty-table', 'data'),
    [Output('save-faculty-output', 'children'),
     Output('save-btn-container', 'children')],
    [Input('save-faculty-btn', 'n_clicks'), Input('faculty-table', 'selected_rows'),
     Input('faculty-table', 'data'), Input('keyword-dropdown-selection', 'value')],
)
def save_faculty(n_clicks, selected_rows, data, value):
  if n_clicks > 0:
    df = data[selected_rows[0]]
    faculty_id = df.get('id')
    set_faculty_as_favorite(faculty_id)

    faculties = get_faculty_table_data(value)
    data = faculties.to_dict('records')
    return data, html.Div(
        [
            dbc.Alert(
                "Sucessfully saved the professor as favorite",
                id="alert-fade",
                dismissable=True,
                is_open=True,
            ),
        ]
    ), dbc.Badge("Favorited", color="white", text_color="danger", className="border me-1")


if __name__ == '__main__':
    app.run_server(debug=True, port=3000)

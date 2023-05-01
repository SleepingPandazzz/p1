import dash
from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import mysql_utils
import mongodb_utils
import neo4j_utils
import quote
import dash_table
import plotly.graph_objects as go
import geopandas as gpd
import numpy as np
import dash_core_components as dcc
import faculty
import publication
import university

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
custom_stylesheets = ['assets/style.css']
app = Dash(__name__, external_stylesheets=[
           dbc.themes.BOOTSTRAP, dbc_css, custom_stylesheets])
mysql = mysql_utils.MysqlUtils()
mapbox_access_token = 'your-mapbox-access-token'
mongosql = mongodb_utils.MyMongoDbUtils()
neo4jsql = neo4j_utils.Neo4jDbUtils()
myquote = quote.MyQuote()
faculty = faculty.Faculty()
publication = publication.Publication()
university = university.University()


header_layout = html.Div([
    html.Div([
        html.H1(children='Explore Keywords', style={'margin-top': '50px'}),
        dcc.Interval(id='interval-component', interval=60000, n_intervals=0),
        html.P(myquote.content + "                --- " + myquote.author,
               style={'margin': '20px 0 20px 0'}, id='quote-output')
    ], style={'text-align': 'center', 'width': '50vw'}),
    html.Div([
        html.Div([
            html.H5(children='Select a Keyword:'),
            dcc.Dropdown(neo4jsql.get_keywords(), 'Computer Science',
                         id='keyword-dropdown-selection'),
        ], style={'width': '40vw', 'margin': '0 auto'}, className='container'),
    ], style={'margin-top': '40px'}, className='center')
], style={'display': 'flex', 'background': 'white'})

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


@callback(
    Output('quote-output', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_quote(n):
  myquote = quote.MyQuote()
  return html.P(myquote.content + "                --- " + myquote.author, style={'margin': '20px 0 20px 0'})


@callback(
    [Output('university-output', 'children'), Output('faculty-output',
                                                     'children'), Output('publication-output', 'children')],
    Input('keyword-dropdown-selection', 'value')
)
def update_output_div(value):
  df = faculty.get_paged_faculty_by_keyword(value, 1)
  dp = publication.get_publications_by_keyword(value, 1)
  dut = university.get_unievrsities_by_keyword(value, 1)
  ff = faculty.get_favorite_faculties()
  filtered_du = neo4jsql.filter_university_map(value)

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
              className='text-center', style={'padding-top': '30px'}),
          html.Div([
              html.Div(id='save-faculty-output'),
              html.Div(id='delete-faculty-output'),
              html.P('* Click the corresponding radio button to view details about each professor.',
                     style={'margin': '10px'}, className='text-center'),
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
                      'max-height': '600px',
                      'overflowX': 'scroll',
                      'border': '1px solid black'
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
              html.Div(id='faculty-card'),
          ]),
      ], style={'width': '100vw', 'display': 'flex-root', 'background': 'white', 'min-height': '700px'}
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
                  'border': '1px solid black'
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
              className='text-center', style={'padding': '30px 0 30px 0'}),
      html.Div([
          dash_table.DataTable(
              id='publication-table',
              columns=[
                  {'name': 'SCORE', 'id': 'total_score'},
                  {'name': 'TITLE', 'id': 'title'},
              ],
              data=dp.to_dict('records'),
              row_selectable="single",
              editable=False,
              selected_rows=[0],
              style_as_list_view=True,
              style_cell={'padding': '5px',
                          'text-align': 'center',
                          'maxWidth': '100px',
                          'white-space': 'initial'},
              style_header={
                  'backgroundColor': 'white',
                  'fontWeight': 'bold'
              },
              style_table={
                  'width': '65vw',
                  'margin': '0 30px',
                  'display': 'flex',
                  'float': 'left',
                  'border': '1px solid black'
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
          html.Div(id='publication-faculty-card'),
      ], style={'min-height': '600px'}),
  ], style={'width': '98vw'})


@callback(
    Output('publication-faculty-card', 'children'),
    Input('publication-table', 'selected_rows'),
    Input('publication-table', 'data')
)
def display_publication_faculty_detail(selected_row, data):
   if selected_row is None:
      return ''
   else:
      publication_id = data[selected_row[0]].get('id')
      df = mongosql.get_publication_info(publication_id)
      keywords = []
      for keyword in df.get('keywords'):
         keywords.append(keyword.get('name').title())
      keywords_str = ", ".join(keywords)
      return html.Div([
          dbc.Card(
              [
                  dbc.CardBody(
                      [
                          html.H5(df.get('title'),
                                  className="card-title"),
                          html.Div([
                              html.P("Venue: " + (df.get('venue') if df.get('venue') is not None else 'N/A'),
                                     style={'margin-bottom': 0}),
                              html.Br(),
                              html.P("Year: " + str(df.get('year')),
                                     style={'margin-bottom': 0}),
                              html.Br(),
                              html.P("Number of Citations: " + str(df.get('numCitations')),
                                     style={'margin-bottom': 0}),
                              html.Br(),
                              html.P("Keywords: " + keywords_str,
                                     style={'margin-bottom': 0}),
                              html.Br(),
                          ], className='card-text'),
                      ]
                  ),
              ], style={"width": "25vw", 'margin': '0 auto'}
          )
      ])


@callback(
    dash.dependencies.Output('favorite-faculty-table', 'output'),
    Input('favorite-faculty-table', 'data')
)
def update_data(data):
    for row in data:
       if all([cell != '' for cell in row.values()]):
          mysql.update_favorite_faculty(row.get('comment'), row.get('id'))

    ff = faculty.get_favorite_faculties()
    return ff.to_dict('records')


@callback(
    Output('faculty-card', 'children'),
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
                                'deleted') != 0 else dbc.Badge("Favorited", color="white", text_color="danger", className="border me-1"),
                        ]
                    ),
                ], style={"width": "20rem", 'margin': '0 auto'}
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
    mysql.set_faculty_as_favorite(faculty_id)

    faculties = mysql.get_faculty_table_data(value)
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
    app.run_server(debug=False, port=2001)

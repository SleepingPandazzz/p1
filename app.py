from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import mysql_utils
import dash_table

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
custom_stylesheets = ['assets/style.css']
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css, custom_stylesheets])
mysql = mysql_utils.MysqlUtils()

def get_keywords():
  result = mysql.execute_query(f"SELECT * FROM keyword ORDER BY name")
  keywords = []
  for (_id, name) in result:
    keywords.append(name.title())
  return keywords

def render_image(url):
  if url is None:
    return ''
  else:
    return html.Img(src=url, style={'height': '50px'})
  
tab_layout = html.Div(
  [
    dbc.Tabs(
      [
        dbc.Tab(html.Table(id='faculty-output'), label="Top Faculties", tab_id="faculty-tab", tab_style={'margin': '0 auto', 'width': '300px', 'text-align': 'center'}),
        dbc.Tab(html.Table(id='publication-output'),label="Top Universities", tab_id="publication-tab", tab_style={'margin': '0 auto', 'width': '300px', 'text-align': 'center'}),
      ],
      id="tabs",
      active_tab="faculty-tab",
      style={'font-size': '18px', 'margin': '30px 100px'}
    ),
    html.Div(id="content"),
  ]
)

# @app.callback(Output("content", "children"), [Input("tabs", "active_tab")])
# def switch_tab(at):
#     if at == "faculty-tab":
#         return "tab1_content"
#     elif at == "publication-tab":
#         return "tab2_content"
#     return html.P("This shouldn't ever be displayed...")

faculties_layout = html.Div([
  html.H2(children='Top Faculties Based on the Selected Keyword'),
  # html.Table(id='faculty-output'),
])

publications_layout = html.Div([
  html.H2(children='Top Publications Based on the Selected Keyword'),
  # html.Table(id='publication-output')
])

app.layout = html.Div([
  # html.Link(
  #   rel='stylesheet',
  #   href='https://cdnjs.cloudflare.com/ajax/libs/bulma/0.9.3/css/bulma.min.css'
  # ),
  html.Div([
    html.H1(children='Explore Keywords', style={'textAlign':'center', 'margin': '50px'}),
    html.Div([
      html.Div([
        html.H5(children='Select a Keyword:'),
        dcc.Dropdown(get_keywords(), 'Computer Science', id='keyword-dropdown-selection'),
      ], style={'width': '55vw', 'margin': '0 auto'}, className='container'),
    ], style={'margin-top': '30px'}, className='center')
  ], style={'display': 'flex'}),
  html.Div(children=tab_layout),
])

@callback(
    [Output('faculty-output', 'children'), Output('publication-output', 'children')],
    Input('keyword-dropdown-selection', 'value')
)
def update_output_div(value):
  query = ("SELECT SUM(fk.score) AS total_score, f.name, f.position, f.research_interest, f.email, f.phone FROM faculty f "
            "LEFT JOIN faculty_keyword fk ON fk.faculty_id = f.id "
            "LEFT JOIN keyword k ON k.id = fk.keyword_id "
            "WHERE k.name = %s "
            "GROUP BY f.id "
            "ORDER BY total_score DESC LIMIT 10")
  df = mysql.execute_query_for_table(query, value)
  df['rank'] = df['total_score'].rank(method='min', ascending=False)

  query = ("SELECT SUM(pk.score) AS total_score, p.title, p.venue, p.year, p.num_citations FROM publication p "
           "LEFT JOIN publication_keyword pk ON pk.publication_id = p.id "
           "LEFT JOIN keyword k ON k.id = pk.keyword_id "
           "WHERE k.name = %s "
           "GROUP BY p.id "
           "ORDER BY total_score DESC limit 10")
  dp = mysql.execute_query_for_table(query, value)
  dp['rank'] = dp['total_score'].rank(method='min', ascending=False)

  return html.Div([
    html.H5(children='Top Faculties Based on the Selected Keyword', className='text-center'),
    dash_table.DataTable(
      id='table',
      # columns = [{"name": i, "id": i} for i in df.columns],
      columns = [
        # {'name': 'photo_url', 'id': 'photo_url', 'type': 'text', 'presentation': 'markdown', 'render': render_image},
        {'name': 'RANK', 'id': 'rank'},
        {'name': 'NAME', 'id': 'name'},
        {'name': 'POSITION', 'id': 'position'},
        {'name': 'RESEARCH INTEREST', 'id': 'research_interest'},
        {'name': 'EMAIL', 'id': 'email'},
        {'name': 'PHONE', 'id': 'phone'}
      ],
      data=df.to_dict('records'),
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
    ], style={'width': '100vw'}), html.Div([
      html.H5(children='Top Publications Based on the Selected Keyword', className='text-center'),
      dash_table.DataTable(
        id='table',
        # columns = [{"name": i, "id": i} for i in df.columns],
        columns = [
          # {'name': 'photo_url', 'id': 'photo_url', 'type': 'text', 'presentation': 'markdown', 'render': render_image},
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


if __name__ == '__main__':
    app.run_server(debug=True)

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
from sqlalchemy import create_engine
import dash_table

# Database connection setup
DATABASE_URL = 'postgresql+psycopg2://admin:admin@localhost:5432/hn'
engine = create_engine(DATABASE_URL)

# Fetch data from the database
def fetch_data():
    query = "SELECT * FROM public.hacker_news_stories"
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Hacker News Stories Visualization"

# Layout of the Dash app
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Hacker News Stories Visualization", className="text-center text-primary mb-4"), width=12)
    ]),
    dbc.Row([
        dbc.Col(dcc.Dropdown(
            id='dropdown',
            options=[
                {'label': 'Show All', 'value': 'ALL'},
                {'label': 'Show Only A.I Stories', 'value': 'AI'},
            ],
            value='ALL',
            className='mb-4'
        ), width=6)
    ], justify='center'),
    dbc.Row([
        dbc.Col(dcc.Graph(id='line_chart'), width=12)
    ]),
    dbc.Row([
        dbc.Col(dash_table.DataTable(
            id='data_table',
            columns=[
                {"name": "ID", "id": "id"},
                {"name": "Story ID", "id": "story_id"},
                {"name": "Title", "id": "title"},
                {"name": "Created At", "id": "created_at"},
                {"name": "Contains AI", "id": "contains_ai"},
            ],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '5px'},
            style_header={
                'backgroundColor': 'rgb(30, 30, 30)',
                'color': 'white',
                'fontWeight': 'bold'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                },
                {
                    'if': {'column_id': 'contains_ai', 'filter_query': '{contains_ai} eq "True"'},
                    'backgroundColor': 'rgb(220, 255, 220)',
                },
            ],
        ), width=12)
    ])
], fluid=True)

# Callback to update the graph and table based on the dropdown selection
@app.callback(
    [Output('line_chart', 'figure'),
     Output('data_table', 'data')],
    [Input('dropdown', 'value')]
)
def update_dashboard(selected_value):
    df = fetch_data()
    df['contains_ai'] = df['title'].str.contains(r'\bA\.I\b|\bAI\b', regex=True, na=False)
    
    if selected_value == 'AI':
        df = df[df['contains_ai']]

    # Prepare data for the line chart
    df['created_at'] = pd.to_datetime(df['created_at'])
    df_line_chart = df.resample('D', on='created_at').size().reset_index(name='count')
    
    line_chart_figure = {
        'data': [{
            'x': df_line_chart['created_at'],
            'y': df_line_chart['count'],
            'type': 'line',
            'name': 'Submissions',
            'line': {'color': 'blue'}
        }],
        'layout': {
            'title': 'Total Submissions Over Time',
            'xaxis': {'title': 'Date'},
            'yaxis': {'title': 'Count'},
            'plot_bgcolor': 'rgb(230, 230, 230)',
            'paper_bgcolor': 'rgb(248, 248, 248)',
        }
    }

    # Prepare data for the table
    table_data = df.to_dict('records')
    
    return line_chart_figure, table_data

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)

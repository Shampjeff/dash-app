import dash

app = dash.Dash('my app')

server = app.server

from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np

data_url = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
        '$select=spc_common,count(tree_id)' +\
        '&$group=spc_common').replace(' ', '%20')
data_trees = pd.read_json(data_url)
trees_list = data_trees['spc_common'].dropna().to_list()
trees_list = [tree.title() for tree in trees_list]

app.layout = html.Div([

    html.H1('NYC Tree Health App'),

    dcc.Dropdown(id='borough_selection',
                 options=[
                 {'label': 'Brooklyn', 'value': 'Brooklyn'},
                 {'label': 'Bronx', 'value': 'Bronx'},
                 {'label': 'Manhattan', 'value': 'Manhattan'},
                 {'label': 'Queens', 'value': 'Queens'},
                 {'label': 'Staten Island', 'value': 'Staten Island'},
                 ], value = 'Manhattan'),


    dcc.Dropdown(id='species_selection',
                 options=[
                 {'label': i, 'value': i} for i in trees_list
                 ], value = trees_list[0]),

    dcc.Graph(id = 'all'),
    dcc.Graph(id = 'health'),
    dcc.Graph(id = 'stewards')

])

@app.callback(
    Output('all', 'figure'),
    Input('borough_selection', 'value'))
def update_graphs(borough):
    
    data_url = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
        '$select=spc_common,health,count(tree_id)' +\
        '&$where=boroname=\'{}\'' +\
        '&$group=spc_common,health').format(borough).replace(' ', '%20')
    df = pd.read_json(data_url).dropna()
    tree_df = df.copy()
    tree_df['spc_common'] = tree_df.spc_common.apply(lambda x:x.title())
    
    tree_df['prop'] = tree_df.loc[:,'count_tree_id']/ \
         tree_df.groupby('spc_common')['count_tree_id'].transform(sum)

    trace1 = go.Bar(
        x=tree_df.loc[tree_df['health'] == 'Good',
                  ['spc_common', 'prop']].sort_values(by='prop')['spc_common'],
        y=tree_df.loc[tree_df['health'] == 'Good',
                  ['spc_common', 'prop']].sort_values(by='prop')['prop'], 
        name='Good', 
        marker_color=px.colors.sequential.Viridis[6],
        hovertemplate = 'Good: %{y:.2f}<extra></extra>'
    )
    trace2 = go.Bar(
        x=tree_df.loc[tree_df['health'] == 'Fair',
                  ['spc_common', 'prop']].sort_values(by='prop')['spc_common'],
        y=tree_df.loc[tree_df['health'] == 'Fair',
                  ['spc_common', 'prop']].sort_values(by='prop')['prop'], 
        name='Fair',
        marker_color=px.colors.sequential.Viridis[4],
        hovertemplate = 'Fair: %{y:.2f}<extra></extra>'

    )
    trace3 = go.Bar(
        x=tree_df.loc[tree_df['health'] == 'Poor',
                  ['spc_common', 'prop']].sort_values(by='prop')['spc_common'],
        y=tree_df.loc[tree_df['health'] == 'Poor',
                  ['spc_common', 'prop']].sort_values(by='prop')['prop'], 
        name='Poor', 
        marker_color=px.colors.sequential.Viridis[0],
        hovertemplate = 'Poor: %{y:.2f}<extra></extra>'
    )

    return {
    'data': [trace1, trace2, trace3],
    'layout':
    go.Layout(
        title=f'Tree Health by Proportion in {borough}',
        barmode = 'stack', 
        hovermode= 'x')
    }

@app.callback(
    Output('health', 'figure'),
    [Input('borough_selection', 'value'), Input('species_selection', 'value')])

def update_graphs(borough, species):
    data_url = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
        '$select=spc_common,health,count(tree_id)' +\
        '&$where=boroname=\'{}\'' +\
        '&$group=spc_common,health').format(borough).replace(' ', '%20')
    df = pd.read_json(data_url).dropna()
    tree_df = df.copy()
    tree_df['spc_common'] = tree_df.spc_common.apply(lambda x:x.title())

    tree_df = tree_df[tree_df['spc_common'] == species]
    tree_df['prop'] = tree_df.loc[:,'count_tree_id']/ \
        sum(tree_df.loc[:,'count_tree_id'])
    
    trace1 = go.Bar(
        x=tree_df.loc[tree_df['health'] == 'Good',
                  ['health','prop']].sort_values(by='prop')['prop'], 
        name='Good', 
        marker_color=px.colors.sequential.Viridis[6],
        orientation='h',
        hovertemplate = 'Good: %{x:.2f}<extra></extra>'
    )
    trace2 = go.Bar(
        x=tree_df.loc[tree_df['health'] == 'Fair',
                  ['health', 'prop']].sort_values(by='prop')['prop'], 
        name='Fair',
        marker_color=px.colors.sequential.Viridis[4],
        orientation='h',
        hovertemplate = 'Fair: %{x:.2f}<extra></extra>'
    )
    trace3 = go.Bar(
        x=tree_df.loc[tree_df['health'] == 'Poor',
                  ['health', 'prop']].sort_values(by='prop')['prop'], 
        name='Poor', 
        marker_color=px.colors.sequential.Viridis[0], 
        orientation='h',
        hovertemplate = 'Poor: %{x:.2f}<extra></extra>'
    )


    return {
    'data': [trace1, trace2, trace3],
    'layout':
    go.Layout(
        title=f'{species} Health in {borough} by Proportion',
        barmode='stack', 
        yaxis= {'visible':False, 'showticklabels':False}, 
        hovermode='x'
        )
    }


@app.callback(
    Output('stewards', 'figure'),
    [Input('borough_selection', 'value'), Input('species_selection', 'value')])

def update_graph2(borough, species):
    data_url = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
        '$select=spc_common,health,steward,count(tree_id)' +\
        '&$where=boroname=\'{}\'' +\
        '&$group=spc_common,health,steward').format(borough).replace(' ', '%20')
    df = pd.read_json(data_url).dropna()
    tree_df = df.copy()
    tree_df['spc_common'] = tree_df.spc_common.apply(lambda x:x.title())

    tree_df = tree_df[tree_df['spc_common'] == species]
    tree_df.steward = tree_df.steward.replace('None', 'No acts') \
        .replace('1or2', '1-2 acts') \
        .replace('3or4', '3-4 acts') \
        .replace('4orMore', '4+ acts')    
    
    trace1 = go.Bar(
        x= tree_df.loc[tree_df['health'] == 'Good',
          ['steward', 'count_tree_id']].sort_values(by='count_tree_id')['steward'],
        y= tree_df.loc[tree_df['health'] == 'Good',
          ['steward', 'count_tree_id']].sort_values(by='count_tree_id')['count_tree_id'],
        name = 'Good', 
        marker_color=px.colors.sequential.Viridis[6]
    )
    trace2 = go.Bar(
        x= tree_df.loc[tree_df['health'] == 'Fair',
          ['steward', 'count_tree_id']].sort_values(by='count_tree_id')['steward'],
        y= tree_df.loc[tree_df['health'] == 'Fair',
          ['steward', 'count_tree_id']].sort_values(by='count_tree_id')['count_tree_id'],
        name= 'Fair', 
        marker_color=px.colors.sequential.Viridis[4]
    )
    trace3 = go.Bar(
        x= tree_df.loc[tree_df['health'] == 'Poor',
          ['steward', 'count_tree_id']].sort_values(by='count_tree_id')['steward'],
        y= tree_df.loc[tree_df['health'] == 'Poor',
          ['steward', 'count_tree_id']].sort_values(by='count_tree_id')['count_tree_id'],
        name = 'Poor',
        marker_color=px.colors.sequential.Viridis[0]
    )

    return {
    'data': [trace1, trace2, trace3],
    'layout':
    go.Layout(
        title=f'{species} Tree Health in {borough} by Stewardship Actions', 
        barmode = 'stack', 
        xaxis = {'categoryarray': ['No acts','1-2 acts', '3-4 acts', '4+ acts'], 
                 'categoryorder': "array"})
    }

if __name__ == '__main__':
    app.run_server(debug = True)
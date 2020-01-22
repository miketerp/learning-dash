import dash
import dash_core_components as dcc
import dash_html_components as html
import json
import os
import pandas as pd
import numpy as np
import requests

from pandas_datareader import data as web
from dash.dependencies import Input, Output
from plotly import graph_objs as go
from plotly.graph_objs import *
from datetime import datetime as dt

mapbox_access_token = os.environ['MB_AUTH_TOKEN']
filename = "./datasets/600.json"

app = dash.Dash(__name__, external_stylesheets=[
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    './assets/custom-css.css'
])

df = None
counter = 0

with open(filename) as f:
    content = f.readlines()

for line in content:
    j = json.loads(line)

    # why \n newline doesnt help with formatting?
    # newStr = j["name"] + ", \n" + j["address"] + ", \n" + str(j["stars"]) + " stars"
    if df is None:
        df = pd.DataFrame(data=j, index=[counter])
        df["markerText"] = df["name"] + ", " + df["address"]
    else:
        df2 = pd.DataFrame(data=j, index=[counter])
        df2["markerText"] = df2["name"] + ", " + df2["address"]
        df = pd.concat([df, df2], sort=False)

    counter = counter + 1


def renderMapFigure(smolDF):
    # This seems unnecessary (renders twice)
    smolDF = smolDF[(smolDF['stars'] >= float(3.5)) & (df['city'] == "Toronto") & (df['state'] == "ON")]

    return go.Figure(go.Scattermapbox(
        lat=smolDF["latitude"].tolist(),
        lon=smolDF["longitude"].tolist(),
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=6
        ),
        text=smolDF["markerText"].tolist()
    ))

fig = renderMapFigure(df)
fig.update_layout(
    hovermode='closest',
    mapbox=go.layout.Mapbox(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=go.layout.mapbox.Center(
            lat=43.69,
            lon=-79.41
        ),
        pitch=0,
        zoom=10
    ),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

app.layout = html.Div([
    html.Div([
        html.Form(
            html.Div([
                html.Br(), html.Br(), html.Br(), html.Br(),
                html.Img(src=app.get_asset_url("dash-logo-new.png"), style={'height': '2em'}),
                html.H3("DASHly - YELP LOCATION APP"),
                html.P("Search for all the restaurants located nearby you."),
                html.Fieldset([
                    html.Legend("Search for", style={
                        'padding': '0.5em'
                    }),
                    html.Div([
                        html.Div([
                            html.P("Find: ", style={'margin': '0.15em'}),
                            html.P("Near: ", style={'margin': '0.15em', 'marginTop': '0.55em'}),
                            html.P("Ratings: ", style={'margin': '0.15em', 'marginTop': '0.55em'}),
                            # html.P("Cuisine: ", style={'margin': '0.15em', 'marginTop': '0.55em'}),
                        ], style={'fontSize': '1.5em', 'padding': '0.5em', 'width': '25%', 'order': 1}),
                        html.Div([
                            dcc.Input(id='my-id', type='text', placeholder="burgers, sushi ...", style={'margin': '0.5em', 'width': '100%'}),
                            dcc.Input(id='my-addr', type='text', value='Toronto, ON', placeholder="city, prov. ...", style={'margin': '0.5em', 'width': '100%'}),
                            dcc.Dropdown(id="ratings", value="3.5", clearable=False,
                                options=[{
                                    'label': '1.5', 'value': 1.5
                                }, {
                                    'label': '2.5', 'value': 2.5
                                }, {
                                    'label': '3.5', 'value': 3.5
                                }, {
                                    'label': '4.5', 'value': 4.5
                                }],
                                style={
                                    # double css applied, why?
                                    # 'width': '50%',
                                    'margin': '0.5em',
                                    'marginTop': '0.4em'
                                }
                            ),
                            # dcc.Dropdown(id="cuisine", value="Italian", clearable=False,
                            #     options=[{
                            #         'label': 'American', 'value': 'American'
                            #     }, {
                            #         'label': 'French', 'value': 'French'
                            #     }, {
                            #         'label': 'Italian', 'value': 'Italian'
                            #     }],
                            #     style={
                            #         # double css applied, why?
                            #         # 'width': '50%',
                            #         'margin': '0.5em',
                            #         'marginTop': '0.7em'
                            #     }
                            # ),
                            # html.Button('Submit', id='button')
                        ], style={
                            'padding': '0.5em',
                            'width': '50%',
                            'order': 2
                        })
                    ], style={
                        'display': "flex",
                        'flexDirection': 'row',
                        'flexWrap': 'wrap'
                    }),
                ], style={
                    'borderWidth': '1px',
                    'padding': '1em',
                    'height': '225px'
                })
            ], style={
                'padding': '2em',
                'margin': '2em',
                'color': '#D8D8D8'
            })
        )
    ], style={
        'backgroundColor': '#1E1E1E',
        'width': '30%',
        'order': 1
    }),
    html.Div([
        dcc.Graph(
            id='my-graph2',
            figure=fig,
            style={
                'height': '900px',
                'width': '100%'
            }
        )
    ], style={
        'backgroundColor': '#323130',
        'width': '70%',
        'order': 2
    })
], style={
    'display': "flex",
    'flexDirection': 'row',
    'flexWrap': 'wrap'
})

def formatSearchResults(res):
    markerText = res["markerText"].tolist()
    return res["latitude"].tolist(), res["longitude"].tolist(), markerText, res["stars"].tolist()

@app.callback(
    Output(component_id='my-graph2', component_property='figure'),
    [Input(component_id='ratings', component_property='value'),
     Input(component_id='my-id', component_property='value'),
     Input(component_id='my-addr', component_property='value')]
     # Input(component_id='cuisine', component_property='value')]
)
def update_maps(yelpratings, searchTerm, location):
    print("Updating ...")
    # print(searchTerm)
    # print(cuisine)
    # print(yelpratings)

    city, state = location.split(", ")
    print("filtering...")
    tmp = df[(df['stars'] >= float(yelpratings)) & (df['city'] == city) & (df['state'] == state)]
    # print(tmp)
    # filtered = tmp[cuisine in tmp['categories']]
    # print(filtered)

    a1, a2, a3, a4 = formatSearchResults(tmp)

    # there's gotta be a different way to updating markers, not sure atm
    newFig = go.Figure(go.Scattermapbox(
        lat=a1,
        lon=a2,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=6
        ),
        text=a3
    ))

    newFig.update_layout(
        hovermode='closest',
        mapbox=go.layout.Mapbox(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=43.69,
                lon=-79.41
            ),
            pitch=0,
            zoom=10
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    print("rendering...")
    return newFig

# hot loading
if __name__ == '__main__':
    app.run_server(debug=True)
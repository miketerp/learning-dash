import dash
import dash_core_components as dcc
import dash_html_components as html
import json
import pandas as pd
import numpy as np
import requests

from pandas_datareader import data as web
from dash.dependencies import Input, Output
from plotly import graph_objs as go
from plotly.graph_objs import *
from datetime import datetime as dt

# can use os.environ['MBATOKEN'] = '...' to hide passwords
mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNqdnBvNDMyaTAxYzkzeW5ubWdpZ2VjbmMifQ.TXcBE-xg9BFdV2ocecc_7g"
# filename = "./datasets/test.json"
filename = "./datasets/ont-food.json"

app = dash.Dash(__name__, external_stylesheets=[
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    # why cant i load local?
    './assets/custom-css.css'
])

latArray, longArray, nameArray, stars, city = [[], [], [], [], []]
# citySet = set()

with open(filename) as f:
    content = f.readlines()

for line in content:
    j = json.loads(line)
    # why \n newline doesnt help with formatiing?
    newStr = j["name"] + ", \n" + j["address"] + ", \n" + str(j["stars"]) + " stars"
    latArray.append(j["latitude"])
    longArray.append(j["longitude"])
    stars.append(j["stars"])
    city.append(j["city"])
    nameArray.append(newStr)

fig = go.Figure(go.Scattermapbox(
    lat=latArray,
    lon=longArray,
    mode='markers',
    marker=go.scattermapbox.Marker(
        size=6
    ),
    text=nameArray
))

fig.update_layout(
    hovermode='closest',
    mapbox=go.layout.Mapbox(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=go.layout.mapbox.Center(
            lat=43.74,
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
                html.Img(src=app.get_asset_url("dash-logo-new.png"), style={'height': '2em'}),
                html.H3("DASHly - YELP LOCATION APP"),
                html.P("Search for all the restaurants located nearby you."),
                html.Fieldset([
                    html.Legend("Search for", style={
                        'padding': '0.5em'
                    }),
                    html.Div([
                        html.Div([
                            html.P("Find: ",
                            style={
                                'margin': '0.15em'
                            }),
                            html.P("Near: ",
                            style={
                                'margin': '0.15em',
                                'marginTop': '0.55em'
                            }),
                            html.P("Ratings: ",
                            style={
                                'margin': '0.15em',
                                'marginTop': '0.55em'
                            }),
                        ], style={
                            'fontSize': '1.5em',
                            'padding': '0.5em',
                            'width': '25%',
                            'order': 1
                        }),
                        html.Div([
                            dcc.Input(
                                id='my-id',
                                type='text',
                                value='thai',
                                placeholder="burgers, sushi ...",
                                style={
                                    'margin': '0.5em'
                                }),
                            dcc.Input(
                                id='my-addr',
                                value='Toronto, ON',
                                type='text',
                                placeholder="city, prov. ...",
                                style={
                                    'margin': '0.5em'
                                }
                            ),
                            dcc.Dropdown(
                                id="ratings",
                                options=[{
                                    'label': '1.5', 'value': 1.5
                                }, {
                                    'label': '2.5', 'value': 2.5
                                }, {
                                    'label': '3.5', 'value': 3.5
                                }, {
                                    'label': '4.5', 'value': 4.5
                                }],
                                value="3.5",
                                clearable=False,
                                style={
                                    # double css applied, why?
                                    # 'width': '50%',
                                    'margin': '0.5em'
                                }
                            )
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
                    'height': '250px'
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
                'height': '875px',
                'width': '75%'
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


def getFromElasticSearch(term, location, rating):
    if (term == None):
        term=""

    url = 'http://localhost:1337/elastic?query=' + term + '&location=' + location + '&stars=' + str(rating)
    resp = requests.get(url)
    if (resp.status_code != 200):
        raise Exception('GET /tasks/ {}'.format(resp.status_code))
        return []
    else:
        return resp.json()

def formatSearchResults(res):
    # filter markers based on yelp ratings
    filteredLatArray = []
    filteredLongArray = []
    filteredNameArray = []
    filteredStars = []

    for ind, val in enumerate(res):
        # print(ind)
        obj = val["_source"]
        filteredLatArray.append(obj["latitude"])
        filteredLongArray.append(obj["longitude"])
        filteredNameArray.append(obj["name"])
        filteredStars.append(obj["stars"])

    return filteredLatArray, filteredLongArray, filteredNameArray, filteredStars


def filter_arrays(selectedRatings):
    # filter markers based on yelp ratings
    filteredLatArray = []
    filteredLongArray = []
    filteredNameArray = []
    filteredStars = []

    for ind, val in enumerate(stars):
        if (stars[ind] >= float(selectedRatings)):
            filteredLatArray.append(latArray[ind])
            filteredLongArray.append(longArray[ind])
            filteredNameArray.append(nameArray[ind])
            filteredStars.append(stars[ind])

    return filteredLatArray, filteredLongArray, filteredNameArray, filteredStars

@app.callback(
    Output(component_id='my-graph2', component_property='figure'),
    [Input(component_id='ratings', component_property='value'),
     Input(component_id='my-id', component_property='value'),
     Input(component_id='my-addr', component_property='value')]
)
def update_maps(yelpratings, term, location):
    # a1, a2, a3, a4 = filter_arrays(yelpratings)

    searchResults = getFromElasticSearch(term, location, yelpratings)
    a1, a2, a3, a4 = formatSearchResults(searchResults)
    print(a1)
    print(a2)
    print(a3)

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
                lat=43.74,
                lon=-79.41
            ),
            pitch=0,
            zoom=10
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return newFig

# hot loading
if __name__ == '__main__':
    app.run_server(debug=True)

# historic stock ticker
# @app.callback(Output('my-graph', 'figure'), [Input('my-id', 'value')])
# def update_graph(selected_dropdown_value):
#     try:
#         df = web.DataReader(selected_dropdown_value, 'av-daily', start=dt(2015, 5, 1), end=dt.now(), api_key='9L7IQ8UFUWOSX726')
#     except:
#         print("Try again")
#
#     return {
#         'data': [{'x': df.index,'y': df.close}],
#         'layout': {
#             'margin': {'l': 40, 'r': 0, 't': 20, 'b': 30}
#         }
#     }

# Test decorator with multiple inputs bound
# @app.callback(
#     Output(component_id='my-div', component_property='children'),
#     [Input(component_id='my-id', component_property='value'),
#      Input(component_id='my-addr', component_property='value')]
# )
# def update_output_div(input_val1, input_val2):
#     return 'You\'ve entered "{input_val1}, {input_val2}"'.format(input_val1=input_val1, input_val2=input_val2)
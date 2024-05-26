import dash
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import pandas as pd

# Load PAS data with preprocessing
df = pd.read_pickle(r"crime_data\PAS.pkl")
df = df.loc[0:9311, ['Date', 'Borough', 'Measure', 'Proportion', 'MPS']]
df['Date'] = pd.to_datetime(df['Date']).dt.date
df = df.loc[(df['Year-Month'] <= '2020-01-01') & (df['Year-Month'] >= '2015-03-31')].copy()

# Load detailed PAS data for ward-level analysis and questions
df_ward = pd.read_pickle(r"crime_data\PAS_ward.pkl")
df_ward['Year-Month'] = pd.to_datetime(df_ward['Year-Month']).dt.date
df_ward.rename(columns={'Year-Month': 'Date'}, inplace=True)

# Load GeoJSON data for boroughs with preprocessing
geojson = gpd.read_file(r'crime_data\merged_boroughs.geojson')
geojson['name'] = geojson['name'].replace({"Westminster": "City of Westminster"})
geojson = geojson[geojson['name'] != "City of London"]

# Load GeoJSON data for wards
geojson_wards = gpd.read_file(r'crime_data\wards.geojson')

# PROOF THAT WE NEED A DIFFERENT GEOJSON WARDS FILE
# list1 = geojson_wards["name"].tolist()
# list2 = df_ward["ward_n"].unique().tolist()
#
# set1 = set(list1)
# set2 = set(list2)
#
# # Find elements in list1 but not in list2
# difference1 = set1 - set2
# # Find elements in list2 but not in list1
# difference2 = set2 - set1
#
# # Convert the sets back to lists if needed
# difference1_list = list(difference1)
# difference2_list = list(difference2)
#
# # Output the results
# print("Elements in list1 but not in list2:", difference1_list)
# print("Elements in list2 but not in list1:", difference2_list)

# THE DASH APP
# Change df to fit heatmap formatting
heatmap_df = df.pivot_table(index='Date', columns='Borough', values='Proportion', aggfunc='mean')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([

    # Headers
    dbc.Row([
        html.H1("EDA for Data Challenge 2")
    ]),

    # Two interactive maps next to each other
    dbc.Row([
        dbc.Col([
            # MAP for PAS data
            html.H3("London Boroughs PAS"),
            dcc.Dropdown(
                id='measure-dropdown2',
                options=[{'label': m, 'value': m} for m in df["Measure"].unique().tolist()],
                value=df["Measure"].unique()[0],
                clearable=False,
                style={'width': '100%'}
            ),
            dcc.Graph(id="choropleth_map", style={'height': '450px', 'width': '100%'}),
        ], width=5),

        dbc.Col([
            # MAP for ward data
            html.H3("London Wards PAS"),
            dcc.Dropdown(
                id='measure-dropdown3',
                options=[{'label': m, 'value': m} for m in df_ward["Measure"].unique().tolist()],
                value=df_ward["Measure"].unique()[0],
                clearable=False,
                style={'width': '100%'}
            ),
            dcc.Graph(id="choropleth_map2", style={'height': '450px', 'width': '100%'}),
        ], width=5),
    ], justify="between"),

    # Plots for each Measure's proportion by borough
    dbc.Row([
        html.H3("Each Measure by Borough"),
        dcc.Dropdown(
            id='measure-dropdown',
            options=[{'label': m, 'value': m} for m in df["Measure"].unique().tolist()],
            value=df["Measure"].unique()[0],
            clearable=False,
            style={'width': '40%'}
        ),
    ]),
    dbc.Row([
        html.Button("Select All", id="select-all-boroughs", n_clicks=0, style={'width': '50%'}),
        html.Button("Deselect All", id="deselect-all-boroughs", n_clicks=0, style={'width': '50%'}),
        dcc.Checklist(
            id='borough-checklist',
            options=[{'label': " " + b + "   ", 'value': b} for b in df["Borough"].unique().tolist()],
            value=df["Borough"].unique().tolist(),
            inline=True,
            style={'margin': '10px'}
        ),
        dcc.Graph(id='main-plot'),
    ]),

    # Heatmap
    dbc.Row([
        dcc.Dropdown(
            id='heatmap-dropdown',
            options=[{'label': m, 'value': m} for m in df["Measure"].unique().tolist()],
            value=df["Measure"].unique()[0],
            clearable=False,
            style={'width': '40%'}
        ),
        dcc.Graph(id='heatmap-plot')
    ]),

    # Plots for each borough's measures
    dbc.Row([
        html.H3("Each Borough by Measure"),
        dcc.Dropdown(
            id='borough-dropdown',
            options=[{'label': b, 'value': b} for b in df["Borough"].unique().tolist()],
            value=df["Borough"].unique()[0],
            clearable=False,
            style={'width': '40%'}
        ),
    ]),

    dbc.Row([
        html.Button("Select All", id="select-all-measures", n_clicks=0, style={'width': '50%'}),
        html.Button("Deselect All", id="deselect-all-measures", n_clicks=0, style={'width': '50%'}),
        dcc.Checklist(
            id='measure-checklist',
            options=[{'label': " " + m + "   ", 'value': m} for m in df["Measure"].unique().tolist()],
            value=df["Measure"].unique().tolist(),
            inline=True,
            style={'margin': '10px'}
        ),
        dcc.Graph(id='main-plot2'),
    ]),

], fluid=True)


# Callback for the PAS borough map
@app.callback(
    Output('choropleth_map', 'figure'),
    Input('measure-dropdown2', 'value')
)
def measure_at_time_map(selected_measure):
    borough_data = df[(df["Measure"] == selected_measure)]

    # Choropleth map with the boroughs
    choropleth_map = px.choropleth(
        borough_data,
        geojson=geojson,
        locations="Borough",
        featureidkey="properties.name",
        animation_frame='Date',
        color="Proportion",
        color_continuous_scale="RdBu"
    )

    choropleth_map.update_layout(geo={"projection": {"type": "natural earth"}})
    choropleth_map.update_geos(fitbounds="locations", visible=False)
    return choropleth_map


# Callback for the PAS ward map
@app.callback(
    Output('choropleth_map2', 'figure'),
    Input('measure-dropdown3', 'value')
)
def measure_at_time_ward(selected_measure1):
    print(df_ward["Measure"].head())
    ward_data = df_ward[(df_ward["Measure"] == selected_measure1)]
    print(ward_data)

    # Choropleth map with the wards
    choropleth_map = px.choropleth(
        ward_data,
        geojson=geojson_wards,
        locations="ward_n",
        featureidkey="features.properties.name",
        animation_frame='Date',
        color="Proportion",
        color_continuous_scale="RdBu"
    )

    choropleth_map.update_layout(geo={"projection": {"type": "natural earth"}})
    choropleth_map.update_geos(fitbounds="locations", visible=False)
    return choropleth_map


# Callback for the select/deselect buttons
@app.callback(
    Output('borough-checklist', 'value'),
    [Input('select-all-boroughs', 'n_clicks'),
     Input('deselect-all-boroughs', 'n_clicks')],
    [State('borough-checklist', 'value')]
)
def toggle_borough_checklist(select_all, deselect_all, current_value):
    ctx = dash.callback_context
    if not ctx.triggered:
        return current_value

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if trigger_id == 'select-all-boroughs':
        return df["Borough"].unique().tolist()
    elif trigger_id == 'deselect-all-boroughs':
        return []

    return current_value


# Callback for the select/deselect buttons
@app.callback(
    Output('measure-checklist', 'value'),
    [Input('select-all-measures', 'n_clicks'),
     Input('deselect-all-measures', 'n_clicks')],
    [State('measure-checklist', 'value')]
)
def toggle_measure_checklist(select_all, deselect_all, current_value):
    ctx = dash.callback_context
    if not ctx.triggered:
        return current_value

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if trigger_id == 'select-all-measures':
        return df["Measure"].unique().tolist()
    elif trigger_id == 'deselect-all-measures':
        return []

    return current_value


# Callbacks for the plots
@app.callback(
    Output('main-plot', 'figure'),
    [Input('measure-dropdown', 'value'),
     Input('borough-checklist', 'value')]
)
def update_plot(selected_measure, selected_boroughs):
    # Filter based on selected measure and boroughs
    filtered_df = df[(df["Measure"] == selected_measure) & (df["Borough"].isin(selected_boroughs))]

    fig = go.Figure()

    for borough in filtered_df["Borough"].unique():
        borough_data = filtered_df[filtered_df["Borough"] == borough]
        fig.add_trace(
            go.Scatter(
                x=borough_data["Date"],
                y=borough_data["Proportion"],
                mode='lines+markers',
                name=borough
            )
        )

    fig.update_layout(
        title=f"Proportion of '{selected_measure}' by Borough by Quarter",
        xaxis_title="Date",
        yaxis_title="Proportion",
        hovermode='x unified',
        template="plotly_white"
    )

    fig.update_yaxes(range=[0, 1])
    # fig.add_vline(x="2023-03-21", line_dash="dash")  # Line for release of  the "Casey Review"

    return fig


@app.callback(
    Output('main-plot2', 'figure'),
    [Input('borough-dropdown', 'value'),
     Input('measure-checklist', 'value')]
)
def update_plot(selected_borough, selected_measures):
    # Filter based on selected measure and boroughs
    filtered_df = df[(df["Borough"] == selected_borough) & (df["Measure"].isin(selected_measures))]

    fig = go.Figure()

    for measure in filtered_df["Measure"].unique():
        measure_data = filtered_df[filtered_df["Measure"] == measure]
        fig.add_trace(
            go.Scatter(
                x=measure_data["Date"],
                y=measure_data["Proportion"],
                mode='lines+markers',
                name=measure
            )
        )

    fig.update_layout(
        title=f"Proportion of '{selected_borough}' by Measure by Quarter",
        xaxis_title="Date",
        yaxis_title="Proportion",
        hovermode='x unified',
        template="plotly_white"
    )

    fig.update_yaxes(range=[0, 1])

    return fig


@app.callback(
    Output('heatmap-plot', 'figure'),
    [Input('heatmap-dropdown', 'value')]
)
def update_heatmap(selected_measure):
    # Filter the dataframe for the selected measure
    df_new = df[df["Measure"] == selected_measure]

    fig = px.density_heatmap(
        df_new,
        x='Date',
        y='Borough',
        z='Proportion',
        histfunc="avg",
        color_continuous_scale='Viridis',
        title=f"Proportion of '{selected_measure}' by Borough over Time"
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Borough",
        coloraxis_colorbar_title="Proportion",
        template="plotly_white"
    )

    return fig


# if __name__ == '__main__':
#     app.run_server(debug=False)

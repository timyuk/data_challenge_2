import dash
from dash import Dash, dcc, html, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

app = Dash(__name__)

# Load data with preprocessing
df = pd.read_csv("PAS_2324.csv", low_memory=False)
df = df.loc[0:9311, ['Date', 'Borough', 'Measure', 'Proportion', 'MPS']]
df['Date'] = pd.to_datetime(df['Date'])

heatmap_df = df.pivot_table(index='Date', columns='Borough', values='Proportion', aggfunc='mean')

# Create interactive plot
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("EDA for Data Challenge 2"),
    html.H2("PAS Data"),

    # Plots for each Measure's proportion by borough
    html.H3("Each Measure by Borough"),
    dcc.Dropdown(
        id='measure-dropdown',
        options=[{'label': m, 'value': m} for m in df["Measure"].unique().tolist()],
        value=df["Measure"].unique()[0],
        clearable=False,
        style={'width': '40%'}
    ),
    html.Button("Select All", id="select-all-boroughs", n_clicks=0),
    html.Button("Deselect All", id="deselect-all-boroughs", n_clicks=0),
    dcc.Checklist(
        id='borough-checklist',
        options=[{'label': b, 'value': b} for b in df["Borough"].unique().tolist()],
        value=df["Borough"].unique().tolist(),
        inline=True,
        style={'margin': '10px'}
    ),
    dcc.Graph(id='main-plot'),

    # Plots for each borough's measures
    html.H3("Each Borough by Measure"),
    dcc.Dropdown(
        id='borough-dropdown',
        options=[{'label': b, 'value': b} for b in df["Borough"].unique().tolist()],
        value=df["Borough"].unique()[0],
        clearable=False,
        style={'width': '40%'}
    ),
    html.Button("Select All", id="select-all-measures", n_clicks=0),
    html.Button("Deselect All", id="deselect-all-measures", n_clicks=0),
    dcc.Checklist(
        id='measure-checklist',
        options=[{'label': m, 'value': m} for m in df["Measure"].unique().tolist()],
        value=df["Measure"].unique().tolist(),
        inline=True,
        style={'margin': '10px'}
    ),
    dcc.Graph(id='main-plot2'),

    # Heatmaps
    dcc.Dropdown(
        id='heatmap-dropdown',
        options=[{'label': m, 'value': m} for m in df["Measure"].unique().tolist()],
        value=df["Measure"].unique()[0],
        clearable=False,
        style={'width': '40%'}
    ),
    dcc.Graph(id='heatmap-plot')

])


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


if __name__ == '__main__':
    app.run_server(debug=True)

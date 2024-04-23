#!/usr/bin/env python
# coding: utf-8

# In[2]:


get_ipython().system('pip install dash')


# In[5]:


import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go

# Load and prepare the data
data = pd.read_csv('C:/Users/50266/Downloads/normalization_dataset_management/fatalities_age_group.csv', delimiter=';', quotechar='"')
data['Report_Date'] = pd.to_datetime(data['Report_Date'])
age_group_labels = {
    1: "0 to 9", 2: "10 to 19", 3: "20 to 29", 4: "30 to 39", 5: "40 to 49",
    6: "50 to 59", 7: "60 to 69", 8: "70 to 79", 9: "80 to 89", 10: "90 & Over",
    11: "Statewide Total", 12: "Unknown"
}
data['Age_Group'] = data['Age_Group'].map(age_group_labels)
data = data[data['Age_Group'] != "Statewide Total"]

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1("Fatality Data Viewer"),
    dcc.DatePickerRange(
        id='date-picker-range',
        min_date_allowed=data['Report_Date'].min(),
        max_date_allowed=data['Report_Date'].max(),
        start_date=data['Report_Date'].min(),
        end_date=data['Report_Date'].max()
    ),
    html.Button('Submit', id='submit-val', n_clicks=0),
    dcc.Graph(id='fatality-chart')
])

# Define callback to update graph based on date input
@app.callback(
    Output('fatality-chart', 'figure'),
    [Input('submit-val', 'n_clicks')],
    [dash.dependencies.State('date-picker-range', 'start_date'),
     dash.dependencies.State('date-picker-range', 'end_date')]
)
def update_output(n_clicks, start_date, end_date):
    if n_clicks > 0:
        filtered_data = data[(data['Report_Date'] >= start_date) & (data['Report_Date'] <= end_date)]
        total = filtered_data['Fatality_Count'].sum()
        fig = go.Figure()
        for group in filtered_data['Age_Group'].unique():
            group_data = filtered_data[filtered_data['Age_Group'] == group]
            group_total = group_data['Fatality_Count'].sum()
            fig.add_trace(go.Bar(
                x=[group],
                y=[group_total],
                name=group,  # Setting the name for each trace
                text=f"{(group_total/total)*100:.2f}%",
                hoverinfo='text+name'
            ))
        fig.update_layout(title="Fatality Counts by Age Group",
                          xaxis_title="Age Group",
                          yaxis_title="Fatality Count",
                          legend_title="Age Group")
        return fig
    return go.Figure()  # Return empty figure for initial load or no clicks

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)


# In[ ]:





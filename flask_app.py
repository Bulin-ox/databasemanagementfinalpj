#with both facility and test flask
from flask import Flask, render_template, request
import pandas as pd
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import json

app = Flask(__name__)

# Load and prepare the fatalities data
fatalities_data = pd.read_csv('/home/bulinli/mysite/fatalities_age_group.csv', delimiter=';', quotechar='"')
fatalities_data['Report_Date'] = pd.to_datetime(fatalities_data['Report_Date'])
fatalities_age_group_labels = {
    1: "0 to 9", 2: "10 to 19", 3: "20 to 29", 4: "30 to 39", 5: "40 to 49",
    6: "50 to 59", 7: "60 to 69", 8: "70 to 79", 9: "80 to 89", 10: "90 & Over",
    11: "Statewide Total", 12: "Unknown"
}
fatalities_data['Age_Group'] = fatalities_data['Age_Group'].map(fatalities_age_group_labels)
fatalities_data = fatalities_data[fatalities_data['Age_Group'] != "Statewide Total"]

# Load and prepare the testing data
testing_data = pd.read_csv('/home/bulinli/mysite/testing_age_group.csv', delimiter=';', quotechar='"')
testing_data['Test_Date'] = pd.to_datetime(testing_data['Test_Date'])
testing_age_group_labels = {
    1: "<1", 2: "1 to 4", 3: "5 to 19", 4: "20 to 44", 5: "45 to 54",
    6: "55 to 64", 7: "65 to 74", 8: "75 to 84", 9: "85+"
}

# Load and prepare the vaccination data
vaccination_data = pd.read_csv('/home/bulinli/mysite/vaccination_age_group.csv', delimiter=';', quotechar='"')
vaccination_data['Report_Date'] = pd.to_datetime(vaccination_data['Report_Date'])
vaccination_age_group_labels = {
    1: "05-11", 2: "12-17", 3: "18-25", 4: "26-34", 5: "35-44",
    6: "45-54", 7: "55-64", 8: "65-74", 9: "75+", 10: "Unknown"
}

# Define a function to create monthly plots
def create_monthly_plot(data, date_column, value_column, title, yaxis_title):
    monthly_data = data.groupby([data[date_column].dt.strftime('%b %Y'), 'Age_Group']).sum().reset_index()
    total_monthly = monthly_data.groupby(date_column)[value_column].sum()
    fig = go.Figure()
    for group in monthly_data['Age_Group'].unique():
        group_data = monthly_data[monthly_data['Age_Group'] == group]
        fig.add_trace(go.Bar(
            x=group_data[date_column],
            y=group_data[value_column],
            name=group,
            text=group_data.apply(lambda x: f"{(x[value_column]/total_monthly[x[date_column]])*100:.2f}%", axis=1),
            hoverinfo='text+name'
        ))
    fig.update_layout(
        barmode='stack',
        title=title,
        xaxis_title="Month",
        yaxis_title=yaxis_title,
        legend_title="Age Group"
    )
    return json.dumps(fig, cls=PlotlyJSONEncoder)
def range_chart(data, date_column, value_column, title, yaxis_title):
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        filtered_data = data[(data[date_column] >= start_date) & (data[date_column] <= end_date)]
        total = filtered_data[value_column].sum()
        fig = go.Figure()
        for group in filtered_data['Age_Group'].unique():
            group_data = filtered_data[filtered_data['Age_Group'] == group]
            group_total = group_data[value_column].sum()
            fig.add_trace(go.Bar(
                x=[group],
                y=[group_total],
                name=group,
                text=f"{(group_total/total)*100:.2f}%",
                hoverinfo='text+name'
            ))
        fig.update_layout(title=title,
                          xaxis_title="Age Group",
                          yaxis_title=yaxis_title,
                          legend_title="Age Group")
        graphJSON = json.dumps(fig, cls=PlotlyJSONEncoder)
        return render_template('plot.html', plot=graphJSON)
    return render_template('date_range_picker.html')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/monthly_fatalities')
def monthly_fatalities_chart():
    plot = create_monthly_plot(fatalities_data, 'Report_Date', 'Fatality_Count',
                               'Stacked Fatality Counts by Age Group Across All Months with Percentages',
                               'Fatality Count')
    return render_template('plot.html', plot=plot)

@app.route('/monthly_testing')
def monthly_testing_chart():
    plot = create_monthly_plot(testing_data, 'Test_Date', 'Total_Positive_Cases',
                               'Stacked Positive COVID Cases by Age Group Across All Months with Percentages',
                               'Positive Case Count')
    return render_template('plot.html', plot=plot)
@app.route('/monthly_vaccination')
def monthly_vaccination_chart():
    plot = create_monthly_plot(vaccination_data, 'Report_Date', 'Series_Complete_Cnt',
                               'Stacked Vaccination Condition by Age Group Across All Months with Percentages',
                               'Vaccination Count')
    return render_template('plot.html', plot=plot)

@app.route('/range_fatalities', methods=['GET', 'POST'])
def range_fatalities_chart():
    return range_chart(fatalities_data, 'Report_Date', 'Fatality_Count',
                       'Fatality Counts by Age Group', 'Fatality Count')

@app.route('/range_testing', methods=['GET', 'POST'])
def range_testing_chart():
    return range_chart(testing_data, 'Test_Date', 'Total_Positive_Cases',
                       'Positive COVID Cases by Age Group', 'Positive Case Count')

@app.route('/range_vaccination', methods=['GET', 'POST'])
def range_vaccination_chart():
    return range_chart(vaccination_data, 'Report_Date', 'Series_Complete_Cnt',
                       'Vaccinations by Age Group', 'Vaccinations Count')

if __name__ == '__main__':
    app.run(debug=True, port=5100, use_reloader=False)

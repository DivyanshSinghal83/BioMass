import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np
from flask import Flask, render_template, request
from Functions import shapefile_generator, graph_plotter_cropland, graph_plotter_marginal
import io
import base64
import pandas as pd
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():

    # Read the country and province data from the Excel file
    
    # Read the country and province data from the CSV file
    df = pd.read_csv("Countries&Provinces.csv")
    countries = df["NAME_0"].unique().tolist()

# Convert the provinces dictionary values from ndarray to list
    provinces = df.groupby("NAME_0")["NAME_1"].unique().to_dict()
    provinces = {country: provinces[country].tolist() for country in provinces}

    if request.method == 'POST':
        country = request.form['country']
        province = request.form['province']
        water_supply_future = request.form['water_supply_future']
        climate_model = request.form['climate_model']
        input_level = request.form['input_level']

        gdf = shapefile_generator(country, province)
        if gdf is None:
            return "Invalid country or province"

        plot_type = request.form.get('plot_type')  # Retrieve the selected plot type

        if plot_type == 'cropland':
            fig = graph_plotter_cropland(gdf, climate_model, water_supply_future, input_level)
        elif plot_type == 'marginal':
            fig = graph_plotter_marginal(gdf, climate_model, water_supply_future, input_level)
        else:
            return "Invalid plot type"

        # Convert the matplotlib figure to an image for embedding in HTML
        fig_data = io.BytesIO()
        plt.savefig(fig_data, format='png')
        plt.close(fig)
        fig_data.seek(0)
        fig_base64 = base64.b64encode(fig_data.getvalue()).decode('utf-8')

        return render_template('calculator.html', graph_image=fig_base64 , countries=countries, provinces=provinces)

    return render_template('calculator.html', countries=countries, provinces=provinces, graph_image=None)


@app.route('/submit', methods=['POST'])
def submit():
    return home()


if __name__ == '__main__':
    app.run(debug=False , host='0.0.0.0')

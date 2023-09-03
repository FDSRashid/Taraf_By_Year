import numpy as np
import gradio as gr
import os
import pandas as pd
from datasets import load_dataset
import geopandas
import plotly.express as px

Secret_token = os.getenv('token')
dataset = load_dataset("FDSRashid/taraf_geo", token = Secret_token,split="train")
dataset_s = load_dataset("FDSRashid/taraf_by_year", token = Secret_token,split="train")

taraf_s = dataset_s.to_pandas()
merged_geo = dataset.to_pandas()
merged_geo = merged_geo.drop(['Unnamed: 0'], axis = 1)
merged_geo["Coordinates"] = geopandas.GeoSeries.from_wkt(merged_geo["geometry"])
geodf = geopandas.GeoDataFrame(merged_geo, geometry= 'Coordinates').drop(['geometry'], axis = 1)


taraf_s = taraf_s.sort_values(['City', 'Year'], ascending=True)
cities = taraf_s['City'].unique().tolist()
min_year = int(taraf_s['Year'].min())
max_year = int(taraf_s['Year'].max())


def plot_taraf_map(min_year = 0, max_year = 400):
  filtered = geodf[(geodf['Year'] >= min_year) & (geodf['Year'] <= max_year)]
  temp = filtered[['City', 'Taraf']].groupby('City').sum().join(filtered[['City', 'Coordinates']].set_index('City'))
  filtered = geopandas.GeoDataFrame(temp, geometry= 'Coordinates').reset_index()
  fig = px.scatter_mapbox(data_frame = filtered, lat = filtered.geometry.y, lon = filtered.geometry.x,size = filtered.Taraf, title = 'Number of Tarafs in Place', opacity = .5, zoom = 0)
  fig.update_layout(title_font_color = 'red', title_x = .5, mapbox_style="stamen-terrain")
  return fig




with gr.Blocks() as demo:
  First_Year = gr.Slider(min_year, max_year, value = 0, label = 'Begining', info = 'Choose the first year to display Tarafs')
  Last_Year = gr.Slider(min_year, max_year, value = 400, label = 'End', info = 'Choose the last year to display Tarafs')
  btn = gr.Button('Submit')
  btn.click(fn = plot_taraf_map, inputs = [First_Year, Last_Year], outputs = gr.Plot())
  demo.launch()
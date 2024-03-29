# -*- coding: utf-8 -*-
"""SI649-Project2

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1-iqtWiTnvPW_ioLsUe6eRK3qD8MY_T-z
"""

import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import altair as alt
import pandas as pd
import panel as pn
import vega_datasets
from bokeh.models import Div
pn.extension('vega')

url1 = 'https://raw.githubusercontent.com/benlaken/Comment_BadruddinAslam2014/master/Data/Monsoon_data.csv'
url2 = 'https://raw.githubusercontent.com/benlaken/Comment_BadruddinAslam2014/master/Data/Olou_counts.csv'


monsoon = pd.read_csv(url1)
olou = pd.read_csv(url2)
combined_data = pd.merge(monsoon, olou, on='Date')
combined_data['Date'] = pd.to_datetime(combined_data['Date'])
combined_data['Year'] = combined_data['Date'].dt.year

ts = pd.to_datetime(combined_data['Date'])
drought_years = [1965, 1966, 1968, 1972, 1974, 1979, 1982, 1986, 1987, 2002, 2004, 2009]
flood_years = [1964, 1970, 1971, 1973, 1975, 1978, 1983, 1988, 1990, 1994, 2007, 2008]
combined_data['Event'] = np.where(combined_data['Date'].dt.year.isin(drought_years), 'Drought',
                                  np.where(combined_data['Date'].dt.year.isin(flood_years), 'Flood', 'Normal'))
toggle_button = pn.widgets.Toggle(name='Highlight Drought and Flood Years', value=False)
date_slider = pn.widgets.DateRangeSlider(name='Date Range Slider', start=ts.min(), end=ts.max(), value=(ts.min(), ts.max()))

@pn.depends(date_slider.param.value, toggle_button.param.value)
def update_plot(date_range, highlight):
    start_date, end_date = map(pd.Timestamp, date_range)
    mask = (ts >= start_date) & (ts <= end_date)
    df_filtered = combined_data.loc[mask].copy()

    # Pre-process the data for coloring based on the toggle's state
    if highlight:
        df_filtered['Color'] = np.where(df_filtered['Event'] == 'Drought', 'red',
                                        np.where(df_filtered['Event'] == 'Flood', 'blue', 'gray'))
    else:
        df_filtered['Color'] = 'gray'

    brush = alt.selection_interval(encodings=['x'])
    nearest = alt.selection(type='single', nearest=True, on='mouseover', fields=['Date'], empty='none')

    precip_chart = alt.Chart(df_filtered).mark_line().encode(
        x='Date:T',
        y='Precip:Q',
        color=alt.value('steelblue'),
        tooltip=['Date:T', 'Precip', 'Counts']
    ).properties(width=600, height=300).add_selection(brush)

    points_chart = alt.Chart(df_filtered).mark_point(color='gray').encode(
        x='Date:T',
        y='Counts:Q',
        color=alt.Color('Color:N', legend=None),
        tooltip=['Date:T', 'Counts:Q']
    ).properties(width=600, height=300)

    vLine = points_chart.mark_rule(color='red').encode(
        x='Date:T',
        opacity=alt.condition(nearest, alt.value(0.7), alt.value(0))
    ).add_selection(nearest)

    # Combine all the layers
    points_chart_with_vline = alt.layer(points_chart, vLine).transform_filter(brush)

    combined_chart = alt.vconcat(precip_chart, points_chart_with_vline).resolve_scale(y='independent').configure_view(strokeWidth=0)

    return combined_chart

app_layout = pn.Column(pn.Row(toggle_button, date_slider), update_plot)
app_layout.servable()


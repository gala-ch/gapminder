import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
#import matplotlib.pyplot as plt
import numpy as np
#import plotly.express as px
import altair as alt
import math

# Title
st.title('Gapminder')

st.write("Unlocking Lifetimes: Visualizing Progress in Longevity and Poverty Eradication")


# Load data

# Define the path to the CSV files
population_csv = 'population.csv'
life_expectancy_csv = 'life_expectancy.csv'
gni_csv = 'gni.csv'

# define the convert_to_number function
def convert_to_number(s):
    """
    Convert a string representing a number with a suffix (e.g. "3M", "12K", "12.8K", or "1689") to an integer.
    """
    suffixes = {"k": 1000, "M": 1000000, "B": 1000000000}
    if s[-1] in suffixes:
        return int(float(s[:-1]) * suffixes[s[-1]])
    else:
        return int(s)


# Define the function to load data and apply the preprocess function
@st.cache_data()
def load_data(csv_file, kpi_name):
    # Read the CSV file into a Pandas DataFrame
    df = pd.read_csv(csv_file)
    # Melt the dataframe into a tidy format
    df = pd.melt(df, id_vars=['country'], var_name='year', value_name=kpi_name)
    # Convert year column to integer
    df['year'] = df['year'].astype(int)    
    # Filter data up to year 2020
    df = df[df['year'].between(1990, 2020)]
    # Forward fill missing values
    df[kpi_name] = df[kpi_name].fillna(method='ffill')

    return df

# Load the CSV files and preprocess the data
population_df = load_data(population_csv, 'population')
life_expectancy_df = load_data(life_expectancy_csv, 'life_expectancy')
gni_df = load_data(gni_csv, 'gni')

#Convert to numbers
gni_df['gni']=gni_df['gni'].apply(convert_to_number)
population_df['population']=population_df['population'].apply(convert_to_number)

# Merge the three dataframes into one
merged_df = pd.merge(population_df, life_expectancy_df, on=['country', 'year'], how='outer')
merged_df = pd.merge(merged_df, gni_df, on=['country', 'year'], how='outer')

# Display the filtered dataframe
#st.write(merged_df)

####UNTIL HERE LOAD DATA

# Set the minimum and maximum years to select
min_year = 1990
max_year = 2020

# Set the initial value to the minimum year
start_year = min_year

# Define the slider to select the year
selected_year = st.slider(
    "Select a year",
    min_value=min_year,
    max_value=max_year,
    value=start_year,
    step=1
)

# Convert the selected year to a datetime object
selected_date = datetime(selected_year, 1, 1)

# Display the selected year
#st.write("Selected year:", selected_year)

# multiselect widget
countries = merged_df['country'].unique()

selected_countries = st.multiselect(
    'Select one or more countries:',
    countries)

#st.write('You selected:', selected_countries)

### all good

# Filter the DataFrame to show only data for selected countries and the selected year
filtered_df = merged_df[(merged_df['country'].isin(selected_countries)) & (merged_df['year'] == selected_year)].dropna(subset=['gni', 'life_expectancy', 'population'])

# Create the bubble chart using Altair
chart = alt.Chart(filtered_df).mark_circle().encode(
    x=alt.X('gni:Q', scale=alt.Scale(type='log'), title='GNI per capita'),
    y=alt.Y('life_expectancy:Q', scale=alt.Scale(zero=False), title='Life Expectancy'),
    size=alt.Size('population:Q', scale=alt.Scale(range=[0, 2000]), title='Population'),
    color=alt.Color('country:N', title='Country')
).properties(
    width=700,
    height=500
)

# Display the chart using Streamlit
st.altair_chart(chart, use_container_width=True)



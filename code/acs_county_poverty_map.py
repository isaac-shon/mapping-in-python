'''
Mapping American Community Survey 5-Year Data - I
We will create a plot that shows county-level poverty rates
It would be best to get a free API key from the U.S. Census Bureau. I'll use mine here.
'''
#%pip install geopandas
#%pip install census
#%pip install us
import geopandas as gpd
from census import Census
from us import states
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Set API key
c = Census("ca8fb76b45300f6b6fc4bde9282e872ce2111df6")

# Retrieve state-level ACS 5-Year Data:
nys_census = c.acs5.state_county_tract(fields = ('NAME', 'C17002_001E', 'C17002_002E', 'C17002_003E', 'B01003_001E'),
                                      state_fips = states.NY.fips,
                                      county_fips = "*",
                                      tract = "*",
                                      year = 2022)

# Create pandas dataframe from retrieved ACS Data:
nys_df = pd.DataFrame(nys_census)
# Create GEOID column and drop other columns:
nys_df["GEOID"] = nys_df["state"] + nys_df["county"] + nys_df["tract"]
nys_df = nys_df.drop(columns = ["state", "county", "tract"])


# Import shapfiles of NYS census tracts using online link:
nys_tract = gpd.read_file("https://www2.census.gov/geo/tiger/GENZ2022/shp/cb_2022_36_tract_500k.zip")
# Reproject shapefile to NAD83 / New York Long Island:
nys_tract = nys_tract.to_crs(epsg = 2263)


# Merge tract datasets (nys_df & nys_tract):
nys_merged = nys_tract.merge(nys_df, on = "GEOID")
# Take subset of our data and create new dataframe:
nys_poverty_tract = nys_merged[["STATEFP", "COUNTYFP", "TRACTCE", "GEOID", "geometry", 
                                "C17002_001E", "C17002_002E", "C17002_003E", "B01003_001E"]]
# Collapse our data to county level:
nys_poverty_county = nys_poverty_tract.dissolve(by = 'COUNTYFP', aggfunc = 'sum')

# Compute the poverty rate of county:
nys_poverty_county["Poverty_Rate"] = (nys_poverty_county["C17002_002E"] + nys_poverty_county["C17002_003E"]) / nys_poverty_county["B01003_001E"] * 100

# Create subplots
fig, ax = plt.subplots(1, 1, figsize = (10, 6))

nys_poverty_county.plot(column = "Poverty_Rate", ax = ax,
                       cmap = "RdPu",
                       legend = True)
# Stylize plots
ax.set_title('Poverty Rates (%) in New York State', fontdict = {'fontsize': '12', 'fontweight' : '3'})
plt.style.use('seaborn-v0_8-paper')
plt.savefig('output\\poverty.pdf')

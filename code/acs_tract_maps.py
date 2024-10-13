'''
Mapping American Community Survey 5-Year Data - II
We will create a plot that shows tract-level home prices & demographic data
It would be best to get a free API key from the U.S. Census Bureau. I'll use mine here.
'''
import geopandas as gpd
from census import Census
from us import states
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as colors

# Set API key
c = Census("ca8fb76b45300f6b6fc4bde9282e872ce2111df6")

# Retrieve ACS data
# B25077_001E: Median home price; B05012_003E: Total Foreign-Born population; B02001_003E: Total black population; B01003_001E: Total population
nys_acs = c.acs5.state_county_tract(fields = ('NAME', 'B25077_001E', 'B05012_003E', 'B02001_003E', 'B01003_001E'),
                                      state_fips = states.NY.fips,
                                      county_fips = "*",
                                      tract = "*",
                                      year = 2022)

# Create pandas dataframe from retrieved ACS Data:
nys_acs_data = pd.DataFrame(nys_acs)
# Create GEOID column and drop other columns:
nys_acs_data["GEOID"] = nys_acs_data["state"] + nys_acs_data["county"] + nys_acs_data["tract"]

# Load and merge state tract shapefile; create new df called NYS_tracts:
NYS_tract_shapefiles = gpd.read_file("https://www2.census.gov/geo/tiger/GENZ2022/shp/cb_2022_36_tract_500k.zip")
NYS_tracts = NYS_tract_shapefiles.merge(nys_acs_data, on = "GEOID")

# Subset so that we only have counties in NYC:
NYC_TRACTS = NYS_tracts[(NYS_tracts['county'] == '005')|(NYS_tracts['county'] == '061')|(NYS_tracts['county'] == '047')|
                        (NYS_tracts['county'] == '081')|(NYS_tracts['county'] == '085')]

# Drop redundant columns:
NYC_TRACTS = NYC_TRACTS.drop(columns = ["state", "county", "tract"])

# Compute Population Densities, per square kilometer:
NYC_TRACTS['Pop_Density'] = NYC_TRACTS['B01003_001E']/(NYC_TRACTS['ALAND']/1000000)
NYC_TRACTS['Black_Pop_Density'] = NYC_TRACTS['B02001_003E']/(NYC_TRACTS['ALAND']/1000000)
NYC_TRACTS['Foreign_Born_Pop_Density'] = NYC_TRACTS['B05012_003E']/(NYC_TRACTS['ALAND']/1000000)

# If median home price < 0 , replace with pd.NA
NYC_TRACTS['B25077_001E'] = NYC_TRACTS['B25077_001E'].mask(NYC_TRACTS['B25077_001E'] < 0, pd.NA)

###########################################################################################################################################################
# Creating Plots
###########################################################################################################################################################

# Median Home Prices
fig, ax = plt.subplots(1, 1, figsize = (10, 6))
# Median Home Prices
NYC_TRACTS.plot(column = "B25077_001E", ax = ax,
                       cmap = "RdYlGn",
                       legend = True,
                       edgecolor = 'black', linewidth = 0.1,
                       missing_kwds={
                           "color": "lightgray",  # Color for missing values
                           "label": "No Data"     # Label for the legend
                        }
                )
plt.style.use('seaborn-v0_8-paper')
ax.set_title('Median Home Prices in NYC ($)', fontdict = {'fontsize': '12', 'fontweight' : '3'})
plt.savefig('output\\medianhomeprices.pdf')

# Overall Population Density
fig, ax = plt.subplots(1, 1, figsize = (10, 6))
NYC_TRACTS.plot(column = "Pop_Density", ax = ax,
                       cmap = 'RdPu',
                       legend = True,
                       edgecolor = 'black', linewidth = 0.1,
                       missing_kwds={
                           "color": "gray",  # Color for missing values
                           "label": "No Data"     # Label for the legend
                        })
ax.set_title('Population Density in NYC (persons per km$^2$)', fontdict = {'fontsize': '12', 'fontweight' : '3'})
plt.style.use('seaborn-v0_8-paper')
plt.savefig('output\\popdensity.pdf')

# Black Population Density
fig, ax = plt.subplots(1, 1, figsize = (10, 6))
NYC_TRACTS.plot(column = "Black_Pop_Density", ax = ax,
                       cmap = 'PuBu',
                       legend = True,
                       edgecolor = 'black', linewidth = 0.1)
plt.style.use('seaborn-v0_8-paper')
ax.set_title('Black Population Density in NYC (persons per km$^2$)', fontdict = {'fontsize': '12', 'fontweight' : '3'})
plt.savefig('output\\blackpopdensity.pdf')

# Foreign-Born Population Density
fig, ax = plt.subplots(1, 1, figsize = (10, 6))

NYC_TRACTS.plot(column = "Foreign_Born_Pop_Density", ax = ax,
                       cmap = "YlGn",
                       legend = True,
                       edgecolor = 'black', linewidth = 0.1,
                       )
plt.style.use('seaborn-v0_8-paper')
ax.set_title('Foreign-Born Population Density in NYC (persons per km$^2$)', fontdict = {'fontsize': '12', 'fontweight' : '3'})
plt.savefig('output\\foreignpopdensity.pdf')
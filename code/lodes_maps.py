'''
Mapping 2020 LEHD Origin-Destination Employment Statistics (LODES) Data
LODES codebook: https://lehd.ces.census.gov/data/lodes/LODES8/LODESTechDoc8.1.pdf
'''
#%pip install pygris
#%pip install pydeck

from pygris.data import get_lodes
import pydeck
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

###########################################################################################################################################################

# Let's start by mapping job locations using get_lodes()
ga_lodes_wac = (get_lodes(state = 'GA',
                          year = '2020',
                          lodes_type = 'wac',
                          return_lonlat= True)
                )

def column_to_rgba(column, cmap, alpha):
    """
    This function will take in a column, normalize it, and return a column 
    'color' where each element is essentially some color for a given cmap.
    
    Args:
        column (DataFrame column): Column to normalize
        cmap (string): ColorMap  
        alpha (float): opacity

    Returns:
        colors (DataFrame column)
    """
    normalized = (column - column.min()) / (column.max() - column.min())
    my_cmap = plt.get_cmap(cmap)
    colors = normalized.apply(lambda x: [int(i * 255) for i in mcolors.to_rgba(my_cmap(x, alpha = alpha))])

    return colors

# Let's get the # of jobs in NAICS sector 61 (Educational Services)
ga_lodes_wac['color'] = column_to_rgba(ga_lodes_wac['CNS15'], 'viridis', 0.5)

# Let's map out of Workplace Area Characteristics data:
layer = pydeck.Layer(
  "ColumnLayer", # 3D visualization that renders a location as a column
  ga_lodes_wac,
  get_position=["w_lon", "w_lat"], # Lat/Long coordinates
  auto_highlight=True,
  elevation_scale=20,
  pickable=True,
  get_elevation = "CNS15", # height of Column
  get_fill_color = "color", # gives us the color of Column
  elevation_range=[0, 1000],
  extruded=True,
  coverage=1
)

# Establishes where our map will look at
view_state = pydeck.ViewState(
  latitude= 33.7501,
  longitude= -84.3885,
  zoom=6,
  min_zoom=5,
  max_zoom=15,
  pitch=40.5,
  bearing=-27.36
)

tooltip = {"html": "Number of Educational Services jobs: {CNS15}"}
r = pydeck.Deck(
  layers=[layer], 
  initial_view_state=view_state, 
  map_style = "light", 
  tooltip = tooltip
)

r.to_html('output\\ga_educational.html')

###########################################################################################################################################################

# Time to get some data on commuting flows:
ga_lodes_od = (get_lodes(state = 'GA',
                          year = '2020',
                          lodes_type = 'od',
                          agg_level = 'tract',
                          return_lonlat= True)
                )

# Census tracts that send >= 50 commuters to the Census tract of Emory University
commuter_tracts = ga_lodes_od.query('w_geocode == "13089022404" & S000 >= 50')

# Let's map out our Origin-Destination data:

GREEN_RGB = [0, 255, 0, 200]
RED_RGB = [240, 100, 0, 200]

arc_layer = pydeck.Layer(
  "ArcLayer",
  data=commuter_tracts,
  get_width="S000 / 10",
  get_source_position=["h_lon", "h_lat"],
  get_target_position=["w_lon", "w_lat"],
  get_tilt=15,
  get_source_color=RED_RGB,
  get_target_color=GREEN_RGB,
  pickable=True,
  auto_highlight=True
)

view_state = pydeck.ViewState(
  latitude=33.7501, 
  longitude= -84, 
  bearing=-20, 
  pitch=30, 
  zoom=9,
  min_zoom=8,
  max_zoom=20,
)

tooltip = {"html": "{S000} jobs <br /> Home of commuter in red; work location in green"}
r = pydeck.Deck(
  arc_layer, 
  initial_view_state=view_state, 
  tooltip=tooltip, 
  map_style = "light"
)

r.to_html('output\\emory_commuters.html')
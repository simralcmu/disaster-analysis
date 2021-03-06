
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
from bokeh.models.glyphs import Patches, Patch
from bokeh.models.widgets import RadioButtonGroup
from bokeh.layouts import column, widgetbox, row
from bokeh.models import CustomJS, Slider, Text, ColumnDataSource, Plot, Circle, HoverTool
from bokeh.plotting import figure, show, output_file
from bokeh.sampledata.us_counties import data as counties
from bokeh.sampledata.us_states import data as states
from bokeh.palettes import Greens9, OrRd9
import bokeh
from bokeh.io import output_notebook
output_notebook()
del states["HI"]
del states["AK"]


# In[2]:


stateabbrevs = {'Texas':'tx',
                'West Virgina':'wv',
                'Kansas':'ks',
                'Maryland':'md',
                'Kentucky':'ky',
                'Pennsylvania':'pa',
                'Nebraska': 'ne',
                'Utah': 'ut',
                'Montana': 'mt',
                'New York': 'ny',
                'Oregon': 'or',
                'North Dakota': 'nd',
                'Idaho': 'id',
                'South Carolina': 'sc',
                'Massachusetts': 'ma',
                'Nevada': 'nv',
                'California': 'ca',
                'District Of Columbia': 'dc',
                'Iowa': 'ia',
                'Arkansas': 'ar',
                'Minnesota': 'mn',
                'Mississippi': 'ms',
                'Connecticut': 'ct',
                'Georgia': 'ga',
                'Missouri': 'mo',
                'Illinois': 'il',
                'Washington': 'wa',
                'Virginia': 'va',
                'Florida': 'fl',
                'New Jersey': 'nj',
                'Alabama': 'al',
                'Ohio': 'oh',
                'Tennessee': 'tn',
                'Oklahoma': 'ok',
                'Vermont': 'vt',
                'Colorado': 'co',
                'New Mexico': 'nm',
                'Wisconsin': 'wi',
                'Maine': 'me',
                'North Carolina': 'nc',
                'Michigan': 'mi',
                'Delaware': 'de',
                'Rhode Island': 'ri',
                'Arizona': 'az',
                'Indiana': 'in',
                'Louisiana': 'la',
                'Wyoming': 'wy',
                'New Hampshire': 'nh',
                'South Dakota': 'sd',
                '-- All States and Areas --': 'all'
               }
abbrevstostate ={val.upper():key for key,val in stateabbrevs.items()} 


# In[3]:


def getStateColor(r):
    total = r.sum()
    if total < 100:
        return 'white'
    if total   <10000000:
        return Greens9[8]
    elif total <100000000:
        return Greens9[6]
    elif total <500000000:
        return Greens9[4]
    elif total <1000000000:
        return Greens9[3]
    elif total <5000000000:
        return Greens9[2]
    else:
        return Greens9[0]
    


# In[4]:


def assignStateColors(df):
    state_xs = [np.array(states[code]["lons"]) for code in states]
    state_ys = [np.array(states[code]["lats"]) for code in states]
    state_names = [abbrevstostate[code.upper()] for code in states]
    state_funds = []
    state_colors = []
    state_hitby = []
    for i, name in enumerate(state_names):
        hit = []
        try:
            state_colors.append(df.loc[name, 'Color'])
            state_funds.append(df.loc[name, 'Sum'])
            for col in df.columns:
                if col not in ['Color', 'Sum']:
                    if df.loc[name, col] != 0:
                        hit.append(col)
        except:
            state_colors.append('white')
            state_funds.append(0)
        state_hitby.append(', '.join(hit))
    newdf = pd.DataFrame(dict(x=state_xs, y=state_ys, color=state_colors, funds=state_funds, 
                              names=state_names, hitby=state_hitby))
    newdf.fillna(0, inplace=True)
    return ColumnDataSource(newdf)


# In[5]:


def get_Sources(df):
    init_sources = {}
    years = list(range(2005, 2018))
    for year in years:
        x = df[df['Year'] == year].copy()
        x = x.transpose()
        x.drop(labels=['Year', 'Total'], axis=0, inplace=True)
        x['Sum'] = x.apply(np.sum, axis=1)
        x['Color'] = x.apply(getStateColor, axis=1)
        init_sources[year] = x 
    return init_sources


# In[6]:


def getStatesPlot(df):
    init_sources = get_Sources(df)
    str_sources = {}
    dictionary_of_sources = {}
    for year in init_sources.keys():
        str_sources['_' + str(year)] = assignStateColors(init_sources[year])
        dictionary_of_sources[year] = '_' + str(year)

    jssources = str(dictionary_of_sources).replace("'", "")

    renderer_source = str_sources['_2006']

    hover = HoverTool(tooltips=[
        ("State", "@names"),
        ("Funds", "@funds"),
        ('Hit By', "@hitby")
    ])

    p = figure(title="Funding Given Per Hurricane", toolbar_location="left", tools=[hover],
               plot_width=900, plot_height=500)
    p.xgrid.visible = False
    p.ygrid.visible = False
    p.xaxis.visible = False
    p.yaxis.visible = False

    state_glyph = Patches(xs = 'x', ys='y', fill_alpha=0.5, fill_color = 'color',
                          line_color="#884444", line_width=1, line_alpha=1)

    jscode = """var year = slider.get('value'),
                    sources = %s,
                    new_source_data = sources[year].get('data');
                renderer_source.set('data', new_source_data);
                """ % jssources

    callback = CustomJS(args=str_sources, code=jscode)
    slider = Slider(start=2005, end=2017, step=1, value=2006, title='Year', callback=callback)
    callback.args["renderer_source"] = renderer_source
    callback.args["slider"] = slider

    text_x = -135
    text_y = 50
    funds = ['< 10 M', '< 100 M', '< 500 M', '< 1 B', '< 5 B', '> 5 B'][::-1]
    colored = [0,2,3,4,6,8]
    p.add_glyph(Text(x=text_x-2, y=text_y+2, text=['Amount of Funds Raised'], 
                     text_font_size='10pt', text_color='#666666', text_align='left'))
    for i, fund in enumerate(funds):
        p.add_glyph(Text(x=text_x+1, y=text_y, text=[fund], text_font_size='10pt', 
                         text_color='#666666', text_align='left'))
        p.add_glyph(Circle(x=text_x , y=text_y+0.4, fill_color=Greens9[colored[i]], 
                           size=15, line_color=None, fill_alpha=0.8))
        text_y = text_y - 2

    p.add_glyph(renderer_source, state_glyph)
    return slider, p


# In[7]:


def getCountySources():
    countyyears = {}
    for year in range(2005, 2018):
        try:
            countyyears[year] = np.load('State_CountyDamages_%g.npy'%year).item()
        except:
            countyyears[year] = {}
    return countyyears

def getCountyColors(damage):
    if damage < 1000:
        return 'white'
    elif damage < 1e5:
        return OrRd9[7]
    elif damage < 1e6:
        return OrRd9[6]
    elif damage < 5e6:
        return OrRd9[5]
    elif damage < 1e7:
        return OrRd9[4]
    elif damage < 5e7:
        return OrRd9[3]
    elif damage < 1e8:
        return OrRd9[2]
    elif damage < 5e8:
        return OrRd9[1]
    else:
        return OrRd9[0]
        


# In[8]:


def assignCountyColors(dic,valid=True):
    EXCLUDED = ("ak", "hi", "pr", "gu", "vi", "mp", "as", "wa", "nv", "ca", "or", 
                "id", "mt", "wy", "ut", "az", "nm", "co", "sd", "nd", "mn", "ne",
                "ia", "wi", "il", "mi")
    county_xs = [np.array(county["lons"]) for county in counties.values() if county['state'] not in EXCLUDED]
    county_ys = [np.array(county["lats"]) for county in counties.values() if county['state'] not in EXCLUDED]
    county_names = [county['name'] for county in counties.values() if county['state'] not in EXCLUDED]
    county_damages = []
    county_colors = []
    for county in counties.values():
        if county['state'] in EXCLUDED:
            continue
        if not valid:
            county_damages.append(0)
            county_colors.append('white')
        else:
            try:
                name = county['name']
                state = abbrevstostate[county['state'].upper()]
                county_damages.append(dic[state][name])
                county_colors.append(getCountyColors(dic[state][name]))
            except:
                county_damages.append(0)
                county_colors.append('white')
    newdf = pd.DataFrame(dict(x=county_xs, y=county_ys, color=county_colors, damages=county_damages, 
                              names=county_names))
    newdf.fillna(0, inplace=True)
    return ColumnDataSource(newdf)


# In[9]:


def getCountyPlot():
    init_sources = getCountySources()
    str_sources = {}
    dictionary_of_sources = {}
    for year in init_sources.keys():
        try:
            str_sources['_' + str(year)] = assignCountyColors(init_sources[year][year])
        except:
            str_sources['_' + str(year)] = assignCountyColors(init_sources[year], valid=False)
        dictionary_of_sources[year] = '_' + str(year)

    jssources = str(dictionary_of_sources).replace("'", "")

    renderer_source = str_sources['_2006']

    hover = HoverTool(tooltips=[
        ("County", "@names"),
        ("Damages", "@damages"),
    ])

    p = figure(title="Damage Done", toolbar_location="left", tools=[hover],
               plot_width=900, plot_height=500)
    p.xgrid.visible = False
    p.ygrid.visible = False
    p.xaxis.visible = False
    p.yaxis.visible = False

    county_glyph = Patches(xs = 'x', ys='y', fill_alpha=0.5, fill_color = 'color',
                          line_color="#884444", line_width=1, line_alpha=1)

    jscode = """var year = slider.get('value'),
                    sources = %s,
                    new_source_data = sources[year].get('data');
                renderer_source.set('data', new_source_data);
                """ % jssources

    callback = CustomJS(args=str_sources, code=jscode)
    slider = Slider(start=2005, end=2017, step=1, value=2006, title='Year', callback=callback)
    callback.args["renderer_source"] = renderer_source
    callback.args["slider"] = slider

    text_x = -115
    text_y = 45
    
    funds = ['< 100 K', '< 1 M', '< 5 M', '< 10 M', '< 50 M', '< 100 M', '< 500 M', '> 500 M'][::-1]
    colored = list(range(8))
    p.add_glyph(Text(x=text_x-2, y=text_y+2, text=['Amount of Funds Raised'], 
                     text_font_size='10pt', text_color='#666666', text_align='left'))
    for i, fund in enumerate(funds):
        p.add_glyph(Text(x=text_x+1, y=text_y, text=[fund], text_font_size='10pt', 
                         text_color='#666666', text_align='left'))
        p.add_glyph(Circle(x=text_x , y=text_y+0.4, fill_color=OrRd9[colored[i]], 
                           size=15, line_color=None, fill_alpha=0.8))
        text_y = text_y - 2

    p.add_glyph(renderer_source, county_glyph)
    return slider, p


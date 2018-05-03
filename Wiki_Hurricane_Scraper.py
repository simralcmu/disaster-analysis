
# coding: utf-8

# In[7]:


import requests
import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt


# In[19]:


def getHurricaneData():
    url = "https://en.wikipedia.org/wiki/List_of_costliest_Atlantic_hurricanes"
    html_string = requests.get(url).content
    if not html_string:
        print('Could Not Get Hurricane Data')
        return None
    soup = BeautifulSoup(html_string, 'html.parser')
    table = soup.find('table')
    columns = ['Name', 'Damage in Billions USD', 'Season',
               'Storm classification at peak intensity']

    num_rows = len(table.find_all('tr'))
    hurricaneDf = pd.DataFrame(columns=columns, index=range(num_rows-1))
    
    for row_marker, row in enumerate(table.find_all('tr')[1:]):
        Name = row.find('th').text
        hurricaneDf.iat[row_marker, 0] = Name

        for column_marker, column in enumerate(row.find_all('td')[:3]):
            if column_marker != 1:
                hurricaneDf.iat[row_marker, column_marker+1] = column.find('span', class_='sorttext').text
            else:
                hurricaneDf.iat[row_marker, column_marker+1] = column.find('a').text
    hurricaneDf['Season'] = hurricaneDf['Season'].apply(lambda x: int(x))
    hurricaneDf['Damage in Billions USD'] = hurricaneDf['Damage in Billions USD'].apply(lambda x: float(x[1:]) * 1000000000)
    return hurricaneDf

def extractData(dataframe):
    Name = dataframe['Name'].tolist()
    Season = dataframe['Season'].tolist()
    
def plotHurricaneDF(df):
    pltWidth, pltHeight = 20, 10
    plt.rcParams['figure.figsize'] = (pltWidth, pltHeight)
    hurricane = df.sort_values(ascending=False, by='Season')
    plt.bar(range(hurricane.shape[0]), hurricane['Damage in Billions USD'])
    plt.xticks(range(hurricane.shape[0]), hurricane['Name'], rotation=90)
    plt.ylabel('in Billion USD')
    plt.show()


# In[20]:


# plotHurricaneDF(hurricaneDf)#


## Import Packages
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date,timedelta,datetime
from scipy.sparse import csr_matrix, hstack
from sklearn.model_selection import train_test_split
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Lasso
from sklearn.linear_model import ElasticNet
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from dateutil.relativedelta import *

#Parameters
## Date
d = date.today()
while d.weekday() != 5:
    d += timedelta(1)
Nextsaturday = d.strftime("%Y-%m-%d")
Nextsunday = d + timedelta(1)
Nextsunday = Nextsunday.strftime("%Y-%m-%d")
## Airbnb Page
pg = ['0','20','40','60','80','100','120'',140','160','180','200']
## List initialization
pricelist,namelist,travellerlist,roomlist,bedlist,sdblist = [],[],[],[],[],[]
option1list,option2list,option3list,option4list = [],[],[],[]

# Web Scrapping for all the pages
for pages in pg:
    #Airbnb Scrapping Request
    page = requests.get("https://www.airbnb.fr/s/Acapulco--Mexique/homes?adults=1&refinement_paths%5B%5D=%2Fhomes&checkin="+Nextsaturday+"&checkout="+Nextsunday+"&flexible_trip_dates%5B%5D=june&flexible_trip_dates%5B%5D=may&flexible_trip_lengths%5B%5D=weekend_trip&date_picker_type=calendar&click_referer=t%3ASEE_ALL%7Csid%3A9697aa3c-ab8b-43c2-ab38-348402f77282%7Cst%3AHOME_GROUPING_FLEXIBLE_DATES&flexible_date_search_filter_type=0&title_type=NONE&search_type=pagination&tab_id=home_tab&ne_lat=16.931993582281493&ne_lng=-99.37419621313472&sw_lat=16.434084058683805&sw_lng=-100.07663456762691&zoom=11&search_by_map=true&place_id=ChIJyVDOroVXyoUR46SQivfYAZg&federated_search_session_id=251bdd36-3fe8-40af-9424-990ab890ca12&items_offset="+pages+"&section_offset=3")
    # SOUP
    soup = BeautifulSoup(page.content,'html.parser')
    airbnbdata = soup.find_all('div',class_='_gig1e7')
    i = 0
    while i < len(airbnbdata):
        j=0
        #Name 
        nameairbnb = airbnbdata[i].find('span',class_='_bzh5lkq').text
        namelist.append(nameairbnb)
        #Price
        priceairbnb = airbnbdata[i].find('span',class_='_155sga30').text
        pricelist.append(priceairbnb)
        #Place Data
        place = airbnbdata[i].find_all('div',class_='_kqh46o')[0]
        place2 = airbnbdata[i].find_all('div',class_='_kqh46o')[1]
        #Traveller
        traveller = place.find_all('span')[0].text
        travellerlist.append(traveller)
        room = place.find_all('span')[2].text
        roomlist.append(room) 
        bed = place.find_all('span')[4].text
        bedlist.append(bed)
        try:
            sdb = place.find_all('span')[6].text
            sdblist.append(sdb)
        except:
            sdblist.append(0)
            pass
        #Options
        option1 = place2.find_all('span')[0].text
        option1list.append(option1)
        try:
            option2 = place2.find_all('span')[2].text
            option2list.append(option2) 
        except:
            option2list.append(0)
        try:
            option3 = place2.find_all('span')[4].text
            option3list.append(option3)
        except:
            option3list.append(0)
        try:
            option4 = place2.find_all('span')[6].text
            option4list.append(option4)
        except:
            option4list.append(0)


        i += 1

# Dataframe        
df_we = pd.DataFrame({"Title":namelist,
                   "Traveller":travellerlist,
                   "Room":roomlist,
                   "Bed":bedlist,
                   'Bathroom':sdblist,
                   'Piscine1':option1list,
                   'Wifi1':option2list,
                   'Climatisation1':option3list,
                   'Cuisine1':option4list,
                   'Price':pricelist
                  })
#Take first letter and change data type
df_we['Traveller'] = df_we['Traveller'].astype(str).str[0]
df_we['Traveller'] = pd.to_numeric(df_we['Traveller'])
df_we['Room'] = df_we['Room'].astype(str).str[0]
df_we['Room'] = df_we['Room'].str.replace('S','0')
df_we['Room'] = pd.to_numeric(df_we['Room'])
df_we['Bed'] = df_we['Bed'].astype(str).str[0]
df_we['Bed'] = pd.to_numeric(df_we['Bed'])
#Erase useless space
df_we['Price'] = df_we['Price'].str.replace("\u202f","")
df_we['Price'] = df_we['Price'].astype(str).str[:-1]
df_we['Price'] = pd.to_numeric(df_we['Price'])

#Check if half bathroom
df_we.loc[df_we['Bathroom'].str[2] == 's', 'Bathroom']  = df_we['Bathroom'].str[0]
df_we.loc[df_we['Bathroom'].str[2] == ' ', 'Bathroom']  = df_we['Bathroom'].str[:1]
df_we.loc[df_we['Bathroom'].str[2] == '5', 'Bathroom']  = df_we['Bathroom'].str[:3]
df_we['Bathroom'] = df_we['Bathroom'].str.replace(',','.')
df_we['Bathroom'] = pd.to_numeric(df_we['Bathroom'])
    
#Check Options
#Piscine column
df_we.loc[df_we['Piscine1'] == 'Cuisine', 'Cuisine1']  = 'Cuisine'
df_we.loc[df_we['Piscine1'] == 'Climatisation', 'Climatisation1']  = 'Climatisation'
df_we.loc[df_we['Piscine1'] == 'Wifi', 'Wifi1']  = 'Wifi'
#Wifi Column
df_we.loc[df_we['Wifi1'] == 'Cuisine', 'Cuisine1']  = 'Cuisine'
df_we.loc[df_we['Wifi1'] == 'Climatisation', 'Climatisation1']  = 'Climatisation'
#Clim column
df_we.loc[df_we['Climatisation1'] == 'Cuisine', 'Cuisine1']  = 'Cuisine'

#Change to dummy
df_we.loc[df_we['Piscine1'] == 'Piscine', 'Piscine']  = 1
df_we.loc[df_we['Piscine1'] != 'Piscine', 'Piscine']  = 0
df_we.loc[df_we['Wifi1'] == 'Wifi', 'Wifi']  = 1
df_we.loc[df_we['Wifi1'] != 'Wifi', 'Wifi']  = 0
df_we.loc[df_we['Climatisation1'] == 'Climatisation', 'Climatisation']  = 1
df_we.loc[df_we['Climatisation1'] != 'Climatisation', 'Climatisation']  = 0
df_we.loc[df_we['Cuisine1'] == 'Cuisine', 'Cuisine']  = 1
df_we.loc[df_we['Cuisine1'] != 'Cuisine', 'Cuisine']  = 0
#If NaN
df_we = df_we.fillna(0)

df_we = df_we.drop(columns=['Piscine1','Wifi1','Climatisation1','Cuisine1'])
df_we = df_we[['Title','Traveller','Room','Bed','Bathroom','Piscine','Wifi','Climatisation','Cuisine','Price']]

#Avoid Luxurious department in our model
df_we = df_we.loc[df_we['Price'] < 300]

#Variables
X = df_we.iloc[:,:-1]
#Target
Y = df_we.iloc[:,-1]
#Drop Name
X.drop(columns=['Title'], inplace=True)

#Train the model
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.20, random_state=1)

# Check best algorithms
models = []
models.append(('LR', LinearRegression()))
models.append(('LA', Lasso()))
models.append(('EN', ElasticNet()))
models.append(('DTR', DecisionTreeRegressor()))
models.append(('KNR', KNeighborsRegressor()))
models.append(('RFR', RandomForestRegressor()))
models.append(('ETR', ExtraTreesRegressor()))

from sklearn.metrics import mean_absolute_error

# Evaluate each model
results = []
names = []
for name, model in models:
  model.fit(X_train, y_train)
  predictions = model.predict(X_test)
  cv_results = mean_absolute_error(y_test, predictions)
  results.append(cv_results)
  names.append(name)
  msg = '%s : %f '% (name, cv_results)
  print(msg)

######## CHECK RESULT AND SELECT BEST METHOD ###########

modeldf = pd.DataFrame({"Name":names,
                   "MAE":results})

modeldf = modeldf[modeldf.MAE == modeldf.MAE.min()]

if modeldf.iloc[:,0].values == 'LR':
    reg = LinearRegression().fit(X_train, y_train)
    predictions = reg.predict(X_pred) 
elif modeldf.iloc[:,0].values == 'LA':
    reg = Lasso().fit(X_train, y_train)
    predictions = reg.predict(X_pred)
elif modeldf.iloc[:,0].values == 'EN':
    reg = ElasticNet().fit(X_train, y_train)
    predictions = reg.predict(X_pred) 
elif modeldf.iloc[:,0].values == 'DTR':
    reg = DecisionTreeRegressor().fit(X_train, y_train)
    predictions = reg.predict(X_pred) 
elif modeldf.iloc[:,0].values == 'KNR':
    reg = KNeighborsRegressor().fit(X_train, y_train)
    predictions = reg.predict(X_pred)
elif modeldf.iloc[:,0].values == 'RFR':
    reg = RandomForestRegressor().fit(X_train, y_train)
    predictions = reg.predict(X_pred) 
elif modeldf.iloc[:,0].values == 'ETR':
    reg = ExtraTreesRegressor().fit(X_train, y_train)
    predictions = reg.predict(X_pred)
    
#Insert your appartment
X_pred = pd.DataFrame({"Traveller":4,
                   "Room":4,
                   "Bed":3,
                   'Bathroom':1.5,
                   'Piscine':1,
                   'Wifi':1,
                   'Climatisation':1,
                   'Cuisine':1}, index=[0]
                     )

print('\n Airbnb Estimated Price for a night between ', Nextsaturday,' & ', Nextsunday , 'is ',round(predictions[0],2),'???')

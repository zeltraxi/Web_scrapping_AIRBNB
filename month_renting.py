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
today = date.today()
firstmonth = today + relativedelta(months=+1)
firstmonth =  firstmonth+relativedelta(day=1)
lastmonth = today + relativedelta(months=+2)
lastmonth =  lastmonth+relativedelta(day=1)
firstmonth = firstmonth.strftime("%Y-%m-%d")
lastmonth = lastmonth.strftime("%Y-%m-%d")
## Airbnb Page
pg = ['0','20','40','60','80','100','120'',140','160','180','200']
## List initialization
pricelist,namelist,travellerlist,roomlist,bedlist,sdblist = [],[],[],[],[],[]
option1list,option2list,option3list,option4list = [],[],[],[]

# Web Scrapping for all the pages
for pages in pg:
    # Web scrapping request
    page = requests.get("https://www.airbnb.fr/s/Acapulco--Mexique/homes?adults=1&refinement_paths%5B%5D=%2Fhomes&checkin="+firstmonth+"&checkout="+lastmonth+"&flexible_trip_dates%5B%5D=june&flexible_trip_dates%5B%5D=may&flexible_trip_lengths%5B%5D=weekend_trip&date_picker_type=calendar&click_referer=t%3ASEE_ALL%7Csid%3A9697aa3c-ab8b-43c2-ab38-348402f77282%7Cst%3AHOME_GROUPING_FLEXIBLE_DATES&flexible_date_search_filter_type=0&title_type=NONE&search_type=pagination&tab_id=home_tab&ne_lat=16.931993582281493&ne_lng=-99.37419621313472&sw_lat=16.434084058683805&sw_lng=-100.07663456762691&zoom=11&search_by_map=true&place_id=ChIJyVDOroVXyoUR46SQivfYAZg&federated_search_session_id=251bdd36-3fe8-40af-9424-990ab890ca12&items_offset="+pages+"&section_offset=3")
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
df_month = pd.DataFrame({"Title":namelist,
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
df_month['Traveller'] = df_month['Traveller'].astype(str).str[0]
df_month['Traveller'] = pd.to_numeric(df_month['Traveller'])
df_month['Room'] = df_month['Room'].astype(str).str[0]
#Check if No bed but only Studio
df_month['Room'] = df_month['Room'].str.replace('S','0')
df_month['Room'] = pd.to_numeric(df_month['Room'])
df_month['Bed'] = df_month['Bed'].astype(str).str[0]
df_month['Bed'] = pd.to_numeric(df_month['Bed'])
#Erase useless space
df_month['Price'] = df_month['Price'].str.replace("\u202f","") 
df_month['Price'] = df_month['Price'].astype(str).str[:-1]
df_month['Price'] = pd.to_numeric(df_month['Price'])

#Check if half bathroom
df_month.loc[df_month['Bathroom'].str[2] == 's', 'Bathroom']  = df_month['Bathroom'].str[0]
df_month.loc[df_month['Bathroom'].str[2] == ' ', 'Bathroom']  = df_month['Bathroom'].str[:1]
df_month.loc[df_month['Bathroom'].str[2] == '5', 'Bathroom']  = df_month['Bathroom'].str[:3]
df_month['Bathroom'] = df_month['Bathroom'].str.replace(',','.')
df_month['Bathroom'] = pd.to_numeric(df_month['Bathroom'])
    
#Check Options
#Piscine column
df_month.loc[df_month['Piscine1'] == 'Cuisine', 'Cuisine1']  = 'Cuisine'
df_month.loc[df_month['Piscine1'] == 'Climatisation', 'Climatisation1']  = 'Climatisation'
df_month.loc[df_month['Piscine1'] == 'Wifi', 'Wifi1']  = 'Wifi'
#Wifi Column
df_month.loc[df_month['Wifi1'] == 'Cuisine', 'Cuisine1']  = 'Cuisine'
df_month.loc[df_month['Wifi1'] == 'Climatisation', 'Climatisation1']  = 'Climatisation'
#Clim column
df_month.loc[df_month['Climatisation1'] == 'Cuisine', 'Cuisine1']  = 'Cuisine'

#Change to dummy
df_month.loc[df_month['Piscine1'] == 'Piscine', 'Piscine']  = 1
df_month.loc[df_month['Piscine1'] != 'Piscine', 'Piscine']  = 0
df_month.loc[df_month['Wifi1'] == 'Wifi', 'Wifi']  = 1
df_month.loc[df_month['Wifi1'] != 'Wifi', 'Wifi']  = 0
df_month.loc[df_month['Climatisation1'] == 'Climatisation', 'Climatisation']  = 1
df_month.loc[df_month['Climatisation1'] != 'Climatisation', 'Climatisation']  = 0
df_month.loc[df_month['Cuisine1'] == 'Cuisine', 'Cuisine']  = 1
df_month.loc[df_month['Cuisine1'] != 'Cuisine', 'Cuisine']  = 0

#Drop Useless Columns
df_month = df_month.drop(columns=['Piscine1','Wifi1','Climatisation1','Cuisine1'])
#Reorder Columns
df_month = df_month[['Title','Traveller','Room','Bed','Bathroom','Piscine','Wifi','Climatisation','Cuisine','Price']]
#If NaN
df_month = df_month.fillna(0)
#Avoid Luxurious department in our model
df_month = df_month.loc[df_month['Price'] < 1000]
#Machine Learning
#Variables
X = df_month.iloc[:,:-1]
#Target
Y = df_month.iloc[:,-1]
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

X_pred = pd.DataFrame({"Traveller":4,
                   "Room":4,
                   "Bed":3,
                   'Bathroom':2,
                   'Piscine':1,
                   'Wifi':1,
                   'Climatisation':1,
                   'Cuisine':1}, index=[0]
                     )
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
                   'Bathroom':2,
                   'Piscine':1,
                   'Wifi':1,
                   'Climatisation':1,
                   'Cuisine':1}, index=[0]
                     )

print('\n Airbnb Estimated Price for a rent between ', firstmonth,' & ', lastmonth , 'is ',round(predictions[0],2),'€')

import requests
#Import BeautifulSoup
from bs4 import BeautifulSoup
import pandas as pd

Nextsaturday = datetime.today() + timedelta(days=datetime.today().isoweekday() - 2)
Nextsaturday = Nextsaturday.strftime("%Y-%m-%d")
Nextsunday = datetime.today() + timedelta(days=datetime.today().isoweekday() - 1)
Nextsunday = Nextsunday.strftime("%Y-%m-%d")

pg = ['0','20','40','60','80','100','120'',140','160']

pricelist,namelist,travellerlist,roomlist,bedlist,sdblist = [],[],[],[],[],[]
option1list,option2list,option3list,option4list = [],[],[],[]
for pages in pg:
    page = requests.get("https://www.airbnb.fr/s/Acapulco--Mexique/homes?adults=1&refinement_paths%5B%5D=%2Fhomes&checkin=2021-05-15&checkout=2021-05-16&flexible_trip_dates%5B%5D=june&flexible_trip_dates%5B%5D=may&flexible_trip_lengths%5B%5D=weekend_trip&date_picker_type=calendar&click_referer=t%3ASEE_ALL%7Csid%3A9697aa3c-ab8b-43c2-ab38-348402f77282%7Cst%3AHOME_GROUPING_FLEXIBLE_DATES&flexible_date_search_filter_type=0&title_type=NONE&search_type=pagination&tab_id=home_tab&ne_lat=16.931993582281493&ne_lng=-99.37419621313472&sw_lat=16.434084058683805&sw_lng=-100.07663456762691&zoom=11&search_by_map=true&place_id=ChIJyVDOroVXyoUR46SQivfYAZg&federated_search_session_id=251bdd36-3fe8-40af-9424-990ab890ca12&items_offset="+pages+"&section_offset=3")
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
            options2list.append(0)
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
 
df_all = pd.DataFrame({"Title":namelist,
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
df_all['Traveller'] = df_all['Traveller'].astype(str).str[0]
df_all['Traveller'] = pd.to_numeric(df_all['Traveller'])
df_all['Room'] = df_all['Room'].astype(str).str[0]
df_all['Room'] = pd.to_numeric(df_all['Room'])
df_all['Bed'] = df_all['Bed'].astype(str).str[0]
df_all['Bed'] = pd.to_numeric(df_all['Bed'])
df_all['Price'] = df_all['Price'].astype(str).str[:-1]
df_all['Price'] = pd.to_numeric(df_all['Price'])

#Check if half bathroom
df_all.loc[df_all['Bathroom'].str[2] == 's', 'Bathroom']  = df_all['Bathroom'].str[0]
df_all.loc[df_all['Bathroom'].str[2] == '5', 'Bathroom']  = df_all['Bathroom'].str[:3]
df_all['Bathroom'] = df_all['Bathroom'].str.replace(',','.')
df_all['Bathroom'] = pd.to_numeric(df_all['Bathroom'])
    
#Check Options
#Piscine column
df_all.loc[df_all['Piscine1'] == 'Cuisine', 'Cuisine1']  = 'Cuisine'
df_all.loc[df_all['Piscine1'] == 'Climatisation', 'Climatisation1']  = 'Climatisation'
df_all.loc[df_all['Piscine1'] == 'Wifi', 'Wifi1']  = 'Wifi'
#Wifi Column
df_all.loc[df_all['Wifi1'] == 'Cuisine', 'Cuisine1']  = 'Cuisine'
df_all.loc[df_all['Wifi1'] == 'Climatisation', 'Climatisation1']  = 'Climatisation'
#Clim column
df_all.loc[df_all['Climatisation1'] == 'Cuisine', 'Cuisine1']  = 'Cuisine'

#Change to dummy
df_all.loc[df_all['Piscine1'] == 'Piscine', 'Piscine']  = 1
df_all.loc[df_all['Piscine1'] != 'Piscine', 'Piscine']  = 0
df_all.loc[df_all['Wifi1'] == 'Wifi', 'Wifi']  = 1
df_all.loc[df_all['Wifi1'] != 'Wifi', 'Wifi']  = 0
df_all.loc[df_all['Climatisation1'] == 'Climatisation', 'Climatisation']  = 1
df_all.loc[df_all['Climatisation1'] != 'Climatisation', 'Climatisation']  = 0
df_all.loc[df_all['Cuisine1'] == 'Cuisine', 'Cuisine']  = 1
df_all.loc[df_all['Cuisine1'] != 'Cuisine', 'Cuisine']  = 0

df_all = df_all.drop(columns=['Piscine1','Wifi1','Climatisation1','Cuisine1'])
df_all = df_all[['Title','Traveller','Room','Bed','Bathroom','Piscine','Wifi','Climatisation','Cuisine','Price']]

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

X = df_all.iloc[:,:-1]
Y = df_all.iloc[:,-1]
X.drop(columns=['Title'], inplace=True)
X_list = [6,4,3,2,1,1,1,1]
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.20, random_state=1)

# Spot check algorithms
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
  model.fit(x_train, y_train)
  predictions = model.predict(x_valid)
  cv_results = mean_absolute_error(y_valid, predictions)
  results.append(cv_results)
  names.append(name)
  msg = '%s : %f '% (name, cv_results)
  print(msg)
base = y_test.values.tolist()
pred = y_pred.tolist()
data_tuples = list(zip(base,pred))
result = pd.DataFrame(data_tuples,columns=['Real','Predicted'])

X_pred = pd.DataFrame({"Traveller":6,
                   "Room":4,
                   "Bed":3,
                   'Bathroom':2,
                   'Piscine':1,
                   'Wifi':1,
                   'Climatisation':1,
                   'Cuisine':1}, index=[0])

predictions = knn.predict(X_pred)

print(predictions[0],'€')

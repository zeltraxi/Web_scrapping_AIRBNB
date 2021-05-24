# -*- coding: utf-8 -*-
"""
Created on Sat May 22 22:14:41 2021

@author: Guillaume
"""

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
from dateutil.relativedelta import *
import warnings
warnings.filterwarnings("ignore")
#Tkinter
from  tkinter import *
from tkcalendar import *

#Enter Function
def submit():
    city_get = City.get()
    from_get = From.get()
    To_get = To.get()
    Travellers_get = travellers.get()
    Room_get = Room.get()
    Bed_get = Bed.get()
    Bathroom_get = Bathroom.get()
    Wifi_get = Wific.get()
    kitchen_get = Kitchenc.get()
    Clim_get = Climc.get()
    Pool_get = Poolc.get()
    
    #Input Parameters
    loc = str(city_get)
    date1 = datetime.strptime(from_get, '%d/%m/%Y').strftime("%Y-%m-%d") 
    date2 = datetime.strptime(To_get, '%d/%m/%Y').strftime("%Y-%m-%d") 

    #Parameters
    ## Airbnb Page
    page = requests.get("https://www.airbnb.fr/s/"+loc+"/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&checkin="+date1+"&checkout="+date2+"&items_offset=0&section_offset=3")
    soup = BeautifulSoup(page.content,'html.parser')
    airbnbpage = soup.find_all('div',class_='_1h559tl')
    airbnbpg = airbnbpage[0].text
    airbnbpg = airbnbpg[4:6]
    airbnbpg = int(airbnbpg)
    ## List initialization
    pricelist,travellerlist,roomlist,bedlist,sdblist = [],[],[],[],[]
    option1list,option2list,option3list,option4list = [],[],[],[]
    
    # Web Scrapping for all the pages
    for pages in range(0, 25*airbnbpg, 25):
        # Web scrapping request
        page = requests.get("https://www.airbnb.fr/s/"+loc+"/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&checkin="+date1+"&checkout="+date2+"&items_offset="+str(pages)+"&section_offset=3")
        # SOUP
        soup = BeautifulSoup(page.content,'html.parser')
        airbnbdata = soup.find_all('div',class_='_gig1e7')
        i = 0
        try:
            while i < 25:
                #Name 
                #nameairbnb = airbnbdata[i].find('span',class_='_bzh5lkq').text
                #namelist.append(nameairbnb)
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
                
        except IndexError:
            pass
    
    # Dataframe        
    df_month = pd.DataFrame({
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
    df_month.loc[df_month['Bathroom'].str[0] == 'D', 'Bathroom']  = '0.5'
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
    df_month = df_month[['Traveller','Room','Bed','Bathroom','Piscine','Wifi','Climatisation','Cuisine','Price']]
    #If NaN
    df_month = df_month.fillna(0)
    #Machine Learning
    #Variables
    X = df_month.iloc[:,:-1]
    #Target
    Y = df_month.iloc[:,-1]
    
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
    
    #Insert your appartment
    X_pred = pd.DataFrame({"Traveller":Travellers_get,
                       "Room":Room_get,
                       "Bed":Bed_get,
                       'Bathroom':Bathroom_get,
                       'Piscine':Pool_get,
                       'Wifi':Wifi_get,
                       'Climatisation':Clim_get,
                       'Cuisine':kitchen_get}, index=[0]
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
    
    #Result
    #label1 = Label(window, text= "Airbnb Estimated Price for a rent between, %s &  %s  is %f €" % (date1, date2,predictions[0]))
    res =  str(round(predictions[0],2)) +'€'
    label_text.set(res)
    #print('\nAirbnb Estimated Price for a rent between ', date1,' & ', date2 , 'is ',round(predictions[0],2),'€')

window= Tk()

window.title('Airbnb Price Detection')
window.geometry("400x400+10+20")
#Grid iteration
i = 0
j = 0
#Title
lbltitle= Label(window, text="Airbnb Price Detection", fg='red', font=("Helvetica", 16))
lbltitle.grid(row=i, column=j, columnspan=2)
i += 1
#City
lblcity= Label(window, text="City" ,fg='black', font=("Helvetica", 14))
lblcity.grid(row=i, column=j)
j+=1
City= Entry(window, text="City", textvariable=StringVar(), bd=2)
City.grid(row=i, column=j)
 
#Calendar
#From
i += 1
j = 0
lblfrom= Label(window, text="Date From", fg='black', font=("Helvetica", 14))
lblfrom.grid(row=i, column=j)
j+=1
From = DateEntry(window, background='darkblue', foreground='white', borderwidth=2)
From.grid(row=i, column=j)

#To
i += 1
j = 0
lblto= Label(window, text="Date To", fg='black', font=("Helvetica", 14))
lblto.grid(row=i, column=j)
j+=1
To = DateEntry(window, background='darkblue', foreground='white')
To.grid(row=i, column=j)

#Max Traveller
i += 1
j = 0
lblnbr= Label(window, text="Number of Travellers" , fg='black', font=("Helvetica", 14))
lblnbr.grid(row=i, column=j)
j += 1
travellers= Scale(window, orient="horizontal", resolution=1,from_=1, to=10,activebackground="blue")
travellers.grid(row=i, column=j)
#Option
#Room
i += 1
j = 0
lblRoom= Label(window, text="Room", fg='black', font=("Helvetica", 14))
lblRoom.grid(row=i, column=j)
j+=1
Room= Scale(window, orient="horizontal", resolution=1,from_=1, to=10,activebackground="blue")
Room.grid(row=i, column=j)

#Bed
i += 1
j = 0
lblbed= Label(window, text="Bed", fg='black', font=("Helvetica", 14))
lblbed.grid(row=i, column=j)
j+=1
Bed= Scale(window, orient="horizontal", resolution=1,from_=1, to=10,activebackground="blue")
Bed.grid(row=i, column=j)

#Bathroom
i += 1
j = 0
lblbathroom= Label(window, text="Bathroom", fg='black', font=("Helvetica", 14))
lblbathroom.grid(row=i, column=j)
j+=1
Bathroom= Scale(window, orient="horizontal", resolution=0.5,from_=0.5, to=5,activebackground="blue")
Bathroom.grid(row=i, column=j)

#Wifi
i += 1
j = 0
Wific = IntVar()
Wifi = Checkbutton(window, text = "Wifi",variable=Wific)
Wifi.grid(row=i, column=j)

#Kitchen
j = 1
Kitchenc = IntVar()
kitchen = Checkbutton(window, text = "Kitchen",variable=Kitchenc, anchor='w')
kitchen.grid(row=i, column=j, sticky='W')

#Pool
i += 1
j = 0
Poolc = IntVar()
Pool = Checkbutton(window, text = "Pool",variable=Poolc)
Pool.grid(row=i, column=j)

#Clim
j += 1
Climc = IntVar()
Clim = Checkbutton(window, text = "Climatisation",variable=Climc, anchor='w')
Clim.grid(row=i, column=j, sticky='W')

#Enter Button
i += 1
j = 0
enterbtn= Button(window, text="Machine Learning Calculation", fg='blue', height = 1, width = 40,  command = submit)
enterbtn.grid(row=i, column=j, columnspan=2)
j += 1

#Quit Button
"""
quitbtn= Button(window, text="Quit", fg='blue', height = 1, width = 10,command= window.destroy)
quitbtn.grid(row=i, column=j)
"""
i += 1
j = 0

label_text = StringVar()
result= Label(window, text="", textvariable=label_text, font=("Helvetica", 20,'bold')).grid(row=i,column=j, columnspan=2)

#Launch
window.mainloop()

import requests
#Import BeautifulSoup
from bs4 import BeautifulSoup
import pandas as pd
page = requests.get("https://www.airbnb.fr/s/Acapulco--Mexique/homes?adults=1&place_id=ChIJyVDOroVXyoUR46SQivfYAZg&refinement_paths%5B%5D=%2Fhomes&checkin=2021-05-15&checkout=2021-05-16")
soup = BeautifulSoup(page.content,'html.parser')
airbnbdata = soup.find_all('div',class_='_gig1e7')

pricelist,namelist,travellerlist,roomlist,bedlist,sdblist = [],[],[],[],[],[]
i = 0
while i < len(airbnbdata):
    j=0
    #Name 
    nameairbnb = airbnbdata[i].find('span',class_='_bzh5lkq').text
    namelist.append(nameairbnb)
    #Price
    priceairbnb = airbnbdata[i].find('span',class_='_155sga30').text
    pricelist.append(priceairbnb)
    #Traveller
    place = airbnbdata[i].find('div',class_='_kqh46o')
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
    
    i += 1
 
df = pd.DataFrame({"Title":namelist,
                   "Traveller":travellerlist,
                   "Room":roomlist,
                   "Bedlist":bedlist,
                   'Bathroom':sdblist,
                   'Price':pricelist
                  })

print(df)

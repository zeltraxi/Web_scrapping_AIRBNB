import requests
#Import BeautifulSoup
from bs4 import BeautifulSoup
import pandas as pd

Nextsaturday = datetime.today() + timedelta(days=datetime.today().isoweekday() - 2)
Nextsaturday = Nextsaturday.strftime("%Y-%m-%d")
Nextsunday = datetime.today() + timedelta(days=datetime.today().isoweekday() - 1)
Nextsunday = Nextsunday.strftime("%Y-%m-%d")

page = requests.get("https://www.airbnb.fr/s/Acapulco--Mexique/homes?adults=1&place_id=ChIJyVDOroVXyoUR46SQivfYAZg&refinement_paths%5B%5D=%2Fhomes&checkin="+Nextsaturday +"&checkout="+Nextsunday)
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
 
df = pd.DataFrame({"Title":namelist,
                   "Traveller":travellerlist,
                   "Room":roomlist,
                   "Bedlist":bedlist,
                   'Bathroom':sdblist,
                   'Option1':option1list,
                   'Option2':option2list,
                   'Option3':option3list,
                   'Option4':option4list,
                   'Price':pricelist
                  })

print(df)

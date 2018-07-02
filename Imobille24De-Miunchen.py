""" https://www.immobilienscout24.de Web Scraping project by Vytautas Bielinskas"""

# Import the libraries
import requests, re
from bs4 import BeautifulSoup

def getURLs(pagesNumber):
    
    listOfURLs = []
    URL_01part = "https://www.immobilienscout24.de/Suche/S-T/P-"
    URL_02part = "/Wohnung-Miete/Bremen"
    
    for page_number in range(1, pagesNumber, 1): #range(1, pagesNumber, 1)
        fullURL = URL_01part + str(page_number) + URL_02part
        listOfURLs.append(fullURL)
        
    return listOfURLs

def getData(URLs):
    import googlemaps
    gmaps_01 = googlemaps.Client(key = "AIzaSyBtP8saWU5lOt7H-o2lOiExzXH967KThyI")
    
    """Get Lan and Lon by GOOGLE MAPS API : START"""
    def getLotLan(geocode_result):
        try:
            print("Trying API")
            lat = geocode_result[0]["geometry"]["location"]["lat"]
            lon = geocode_result[0]["geometry"]["location"]["lng"]
        except:
            lat = 0
            lon = 0
        print(lat, lon)
        return lat, lon
    """Get Lan and Lon by GOOGLE MAPS API : END"""
    """Get the title of the object : START"""
    def getTitleCity(objectsBlock):
        titleOfObject = objectsBlock.find_all("div", {"class":"result-list-entry__address"})
        Title = titleOfObject[0].text
        City = str(Title).split(",")[len(Title.split(","))-1]
        return Title, City  
    """Get the title of the object : END"""
    
    """ Get the number of rooms : START """
    def getNumberOfRooms(objectsBlock):
        numberOfRooms = float(objectsBlock.find_all("dd", {"class":"font-nowrap font-line-xs"})[2].text.replace(",","."))
        return numberOfRooms
    """ Get the number of rooms : END """
    
    """ Get the area in m2 of the object : START """
    def getArea(objectBlock):

        AreaString = ((objectBlock.find_all("div", {"class":"result-list-entry__criteria"})[0].text).split("m²")[0]).replace(" ", "")
        
        AreaR = ""
        stringIndex = len(AreaString)-1
        while AreaString[stringIndex].isalpha() != True:
            if stringIndex > 1:
                AreaR = AreaR + AreaString[stringIndex]
                stringIndex = stringIndex - 1

        Area = ""
        for i in reversed(range(len(AreaR))):
            Area = Area + AreaR[i]
        
        print("Final area: ",Area)
        
        return float(Area.split("-")[0].replace(",", "."))
    """ Get the area in m2 of the object : END """
    ListOfData = []
    
    for page in range (1, len(URLs), 1):
        print(page,":", URLs[page])
        r = requests.get(URLs[page])
        c = r.content
        soup = BeautifulSoup(c, "html.parser")
        objects = soup.find_all("article", {"data-item":"result"})  
        
        
        for item in range(0, len(objects), 1):   
            DataDict = {}
            DataDict["Title"] = getTitleCity(objects[item])[0]
            DataDict["City"] = getTitleCity(objects[item])[1]
            DataDict["Price"] = float(((objects[item].find_all("div", {"class":"result-list-entry__criteria"})[0].text).split(" ")[0]).replace(".", "").replace(",","."))
            try:
                DataDict["Rooms"] = getNumberOfRooms(objects[item])
            except:
                DataDict["Rooms"] = 0
            DataDict["Area"] = getArea(objects[item])
            if DataDict["Area"] > 0:
                DataDict["Price per Square"] = DataDict["Price"] / DataDict["Area"]
            else:
                DataDict["Price per Square"] = 0
            geocode_result = gmaps_01.geocode(DataDict["Title"])
            DataDict["Latitude"] = getLotLan(geocode_result)[0]
            DataDict["Longitude"] = getLotLan(geocode_result)[1]
            
            ListOfData.append(dict(DataDict))
        
    return ListOfData

pagesNumber = 33
URLs = getURLs(pagesNumber)
DF = getData(URLs)

import pandas as pd
FinalDF = pd.DataFrame(DF)

FinalDF.to_csv('immobilienscout24.de - with API2 - Bremen.csv')
import logging
import re
import os
import csv
import requests
import gpxpy
import gpxpy.gpx
import src.lib.OpenStreetMap.gpx as gpxLib
from pathlib import Path
from bs4 import BeautifulSoup


COLOR_DICT = {
    "OK": '#ffe808',
    "Un peu dégradé": '#ffce00',
    "Dégradé": '#ff9a00',
    "Très dégradé": '#ff5a00',
    "Détruit": '#ff0000',
    "Non visible": '#65737e',
    "Inconnu": '#000000',
    "neutral": '#eecc22',
    "destroyed": '#d00d0d',
    "flashed": '#88e030'
}
COLOR_REPLACEMENT_DICT = {
    "neutral": "OK",
}


def createInvaderGpx(name: str):
    gpx = gpxpy.gpx.GPX()
    gpx.name = name
    gpx.nsmap = {
        'defaultns': 'http://www.topografix.com/GPX/1/1',
        'osmand': 'https://osmand.net',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }
    return gpx

def findCityNumberingFormat(cityDict: dict) -> int:
    strNumberList = list(cityDict.keys())
    lenList = []
    for strNumber in strNumberList:
        lenList.append(len(strNumber))
    nNumber = max(set(lenList), key = lenList.count)
    return nNumber


def convertToNumberingFormat(number, nNumber):
    if len(number) < nNumber:
        nZerosToAdd = nNumber - len(number)
        for n in range(nZerosToAdd):
            number = '0' + number
    elif len(number) == nNumber:
        pass
    else:
        logging.error("number len is exceeding number format.")
        number = number[len(number) - nNumber:]
    return number


def findCityNameAndNumber(waypoint: gpxpy.gpx.GPXWaypoint):
    pattern = r'^[A-Za-z]{1,4}_\d{1,4}$'
    if waypoint.name is not None:
        match = re.match(pattern, waypoint.name)
        if match is not None:
            invaderName = match.string
            cityName = invaderName.split('_')[0]
            if not cityName.isupper():
                cityName = cityName.upper()
            number = invaderName.split('_')[1]
        else:
            cityName = None
            number = None
    else:
        cityName = None
        number = None
    return cityName, number


def getGpxInvaders(gpxPath: Path, cityFilter: str = None) -> dict:
    """Gets all the cities referenced in the invader Gpx file.

    Args:
        gpxPath (Path): Path of the gpx file.
        cityFilter (str, optional): Name of the city. Defaults to None.

    Returns:
        dict: Dict of invaders by city.
    """
    gpx = gpxLib.openGpx(gpxPath)
    filesDict = {}
    for waypoint in gpx.waypoints:
        cityName, number = findCityNameAndNumber(waypoint)
        if ((cityFilter is not None and cityFilter == cityName) or cityFilter is None) and cityName is not None:
            if cityName not in filesDict.keys():
                filesDict[cityName] = {number: waypoint}
            else:
                filesDict[cityName][number] = waypoint
    for city in filesDict.keys():
        nNumber = findCityNumberingFormat(filesDict[city])
        for number in filesDict[city].keys():
            number = convertToNumberingFormat(number, nNumber)
    return filesDict


def openInvaderCSV(path: Path) -> dict:
    """Open csv of space invaders and stroe them in  a dict.

    Args:
        path (Path): Path of CSV file.

    Returns:
        dict: Dict of cities and invaders.
    """
    dict = {}
    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for city in row.keys():
                number = row[city]
                if len(number) < 4:
                    zeroPad = ''
                    for idx in range(4-len(number)):
                        zeroPad += '0'
                    number = zeroPad + number
                if city in dict.keys():
                    dict[city].append(number)
                else:
                    dict[city] = [number]
    return dict


def getFlashedInfoFromGPX(gpxPath: Path) -> dict:
    """Gets flashed infos from colors in gpx and stores them in a dict. 

    Args:
        gpxPath (Path): Path of gpx file.

    Returns:
        dict: Dict of invaders and their flash state.
    """
    infosDict = {}
    gpx = gpxLib.openGpx(gpxPath)
    for waypoint in gpx.waypoints:
        splitName = waypoint.name.split(',')[0]
        splitName = splitName.split(' ')[-1]
        if 'PA' not in splitName.split('_') and 'VRS' not in splitName.split('_'):
            if '_' in waypoint.name:
                splitName = waypoint.name.split('_')[-1]
            splitName = 'PA_' + splitName
        waypointColor = gpxLib.getWaypointProperty(waypoint=waypoint, property=gpxLib.WAYPOINT_PROPERTIES.COLOR)
        if waypointColor == '#88e030':
            status = 'flashed'
            color = '#88e030'
            infosDict[splitName] = {}
            infosDict[splitName]['status'] = status
            infosDict[splitName]['color'] = color
        elif waypointColor == '#d00d0d':
            status = 'destroyed'
            color = '#d00d0d'
            infosDict[splitName] = {}
            infosDict[splitName]['status'] = status
            infosDict[splitName]['color'] = color
    return infosDict


def groupGpxIntoOne(folderPath: Path, name):
    invadersDict = {}
    for fileName in os.listdir(folderPath):
        if fileName.split('.')[-1] == 'gpx':
            fileInvadersDict = getGpxInvaders(gpxPath=folderPath/fileName)
            for city in fileInvadersDict.keys():
                if city not in invadersDict.keys():
                    invadersDict[city] = {}
                for number in fileInvadersDict[city].keys():
                    if number not in invadersDict[city].keys():
                        invadersDict[city][number] = fileInvadersDict[city][number]
                    else:
                        logging.warning(f'duplicate found on {city}_{number}')
    gpx = createGpxFromInvadersDict(invadersDict=invadersDict, name=name)
    gpxLib.saveGpx(gpx, folderPath/ (name+'.gpx'))


def createGpxFromInvadersDict(invadersDict, name):
    gpx = createInvaderGpx(name)
    for city in invadersDict.keys():
        for number in invadersDict[city].keys():
            waypoint = invadersDict[city][number]
            waypoint.type = name
            gpx.waypoints.append(waypoint)
    return gpx


def getInvaderSpotterStateInfos(cityDict: dict):
    url = "https://www.invader-spotter.art/listing.php"
    stateDict = {}
    for city in cityDict.keys():
        page = 0
        i = 0
        while i != 1:
            if page == 0:
                r = requests.post(
                    url="https://www.invader-spotter.art/listing.php",
                    data={"ville": city, "arron": "00", "mode": "lst", "rang": "10"},
                    headers={"Referer": "https://www.invader-spotter.art/villes.php", "Origin": "https://www.invader-spotter.art"}
                )
            else:
                r = requests.post(
                    url="https://www.invader-spotter.art/listing.php",
                    data={"ville": city, "arron": "00", "mode": "lst", "rang": "10", "page": str(int(page+1))},
                    headers={"Referer": "https://www.invader-spotter.art/villes.php", "Origin": "https://www.invader-spotter.art"}
                )
            soup = BeautifulSoup(r.text, "html.parser")
            elements = soup.find_all("tr", {"class": "haut"})
            if elements != []:
                for element in elements:
                    content = element.contents[1]
                    state = content.text.split('Date')[0]
                    state = state.split(':  ')[-1]
                    name = content.text.split(' ')[0]
                    if '!' in state:
                        state = state.split(' !')[0]
                    if 'Instagram' in state:
                        state = state.split('Instagram')[0]
                    logging.info(name + " : " + state)
                    stateDict[name] = state
                page += 1
            else:
                i = 1
    return stateDict


def findStatusFromNews(newsLine: str, cue: str):
    invadersList = []
    pattern = r'^[A-Za-z]{1,4}_\d{1,4}$'
    newsLineSplitted = newsLine.split('.')
    for split in newsLineSplitted:
        if cue in split.split(' '):
            for word in split.split(' '):
                match = re.match(pattern, word)
                if match is not None:
                    invadersList.append(match.string)
    return invadersList


def getInvaderSpotterNews(month: int, year: int):
    newsDict = {
        'Destruction': [],
        'Réactivation': [],
        'Dégradation': [],
        'Restauration': [],
        'statut': [],
    }
    url = "https://www.invader-spotter.art/news.php"
    stateDict = {}
    r = requests.get(
        url="https://www.invader-spotter.art/news.php"
    )
    soup = BeautifulSoup(r.text, "html.parser")
    if len(str(month)) < 2:
        month = '0' + str(month)
    else:
        month = str(month)
    dateStr = "mois" + str(year) + month
    elements = soup.find_all("div", {"id": dateStr})
    if elements != []:
        for element in elements:
            for newsLine in element.contents:
                if newsLine != '\n':
                    newsLine = newsLine.text
                    for cue in newsDict.keys():
                        statusList = findStatusFromNews(newsLine, cue)
                        for invader in statusList:
                            newsDict[cue].append(invader)
    return stateDict


def updateInvadersDictFromStateDict(invadersDict: dict, stateDict: dict, showFlashed: bool = True):
    for city in invadersDict.keys():
        for number in invadersDict[city].keys():
            waypoint = invadersDict[city][number]
            waypointColor = gpxLib.getWaypointProperty(waypoint=waypoint, property='color')
            state = getInvaderStateFromColor(waypointColor)
            if showFlashed is True:
                if state != "flashed":
                    invaderName = city + '_' + number
                    if invaderName in stateDict.keys():
                        waypoint = gpxLib.replaceWaypointProperty(waypoint=waypoint, property='color', propertyText=COLOR_DICT[stateDict[invaderName]])
                    else:
                        waypoint = gpxLib.replaceWaypointProperty(waypoint=waypoint, property='color', propertyText=COLOR_DICT['OK'])
            else:
                invaderName = city + '_' + number
                if invaderName in stateDict.keys():
                    waypoint = gpxLib.replaceWaypointProperty(waypoint=waypoint, property='color', propertyText=COLOR_DICT[stateDict[invaderName]])
                else:
                    waypoint = gpxLib.replaceWaypointProperty(waypoint=waypoint, property='color', propertyText=COLOR_DICT['OK'])
    return invadersDict


def getInvaderStateFromColor(hexColor):
    if hexColor in COLOR_DICT.values():
        key_list = list(COLOR_DICT.keys())
        val_list = list(COLOR_DICT.values())
        position = val_list.index(hexColor)
        state = key_list[position]
        if state in COLOR_REPLACEMENT_DICT.keys():
            state = COLOR_REPLACEMENT_DICT[state]
    else:
        state = COLOR_DICT["OK"]
    return state

def getWaypointFormat(gpxPath):
    infosDict = {}
    gpx_file = open(gpxPath, 'r')
    gpx = gpxpy.parse(gpx_file)
    waypoint = gpx.waypoints[0]
    return waypoint.extensions

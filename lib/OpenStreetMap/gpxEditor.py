import gpxpy
import gpxpy.gpx
import csv

def openInvaderCSV(path):
    dict = {}
    with open('ressources/Invaders Arthur.csv', newline='') as csvfile:
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


def getFlashedInfoFromGPX(gpxPath):
    infosDict = {}
    gpx_file = open(gpxPath, 'r')
    gpx = gpxpy.parse(gpx_file)
    for waypoint in gpx.waypoints:
        splitName = waypoint.name.split(',')[0]
        splitName = splitName.split(' ')[-1]
        if 'PA' not in splitName.split('_') and 'VRS' not in splitName.split('_'):
            if '_' in waypoint.name:
                splitName = waypoint.name.split('_')[-1]
            splitName = 'PA_' + splitName
        for element in waypoint.extensions:
            if element.text == '#88e030':
                status = 'flashed'
                color = '#88e030'
                infosDict[splitName] = {}
                infosDict[splitName]['status'] = status
                infosDict[splitName]['color'] = color
            elif element.text == '#d00d0d':
                status = 'destroyed'
                color = '#d00d0d'
                infosDict[splitName] = {}
                infosDict[splitName]['status'] = status
                infosDict[splitName]['color'] = color
    return infosDict


def applyModificationFromDictAndSaveGpx(gpxPath, favouriteName, modifsDict):
    gpx_file = open(gpxPath, 'r')
    gpx = gpxpy.parse(gpx_file)
    gpx.name = favouriteName
    modifiedList = []
    for waypoint in gpx.waypoints:
        waypoint.type = 'SpaceInvader'
        splitName = waypoint.name.split(',')[0]
        splitName = splitName.split(' ')[0]
        waypoint.name = splitName
        waypoint.description = 'name='+splitName
        if splitName in modifsDict.keys():
            if parisDict[splitName]['color'] is not None:
                for element in waypoint.extensions:
                    if element.tag == '{https://osmand.net}color':
                        element.text = modifsDict[splitName]['color']
                        modifiedList.append(splitName)
    nameList = []
    for waypoint in gpx.waypoints:
        if waypoint.name in nameList:
            gpx.waypoints.remove(waypoint)
        nameList.append(waypoint.name)
    return gpx


def addInfosFromCsv(gpx, csvPath):
    csvDict = openInvaderCSV(csvPath)
    for waypoint in gpx.waypoints:
        waypointName = waypoint.name
        for city in csvDict.keys():
            for number in csvDict[city]:
                if waypointName == city+'_'+number:
                    for element in waypoint.extensions:
                        if element.tag == '{https://osmand.net}color':
                            element.text = '#88e030'
    return gpx


def saveGpx(gpx, path):
    with open(path, "w") as f:
        f.write(gpx.to_xml())


parisDict = getFlashedInfoFromGPX('ressources/favorites-Invaders_Paris.gpx')
gpx = applyModificationFromDictAndSaveGpx('ressources/favorites-invaders_Monde.gpx', 'SpaceInvaders', parisDict)
gpx = addInfosFromCsv(gpx, 'ressources/Invaders Arthur.csv')
saveGpx(gpx, 'ressources/SpaceInvaders.gpx')


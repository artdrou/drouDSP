import argparse
import logging
import os, sys
from pathlib import Path

sys.path.append(Path(os.getcwd()).as_posix())
from src.lib.OpenStreetMap import gpx as gpxLib
from src.lib.OpenStreetMap import invadersEditor

CITY = "PA"
GPX_PATH = Path("X:/Utilisateur/Documents/drouDSP/ressources/Space Invaders.gpx")
CSV_PATH = Path("X:/Utilisateur/Documents/drouDSP/ressources/Invaders OC.csv")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    invadersDict = invadersEditor.getGpxInvaders(gpxPath=GPX_PATH)
    stateDict = invadersEditor.getInvaderSpotterStateInfos(invadersDict)
    invadersDict = invadersEditor.updateInvadersDictFromStateDict(invadersDict=invadersDict, stateDict=stateDict, showFlashed=False)
    csvDict = invadersEditor.openInvaderCSV(CSV_PATH)
    updatedGpxFromCsv = invadersEditor.updateGpxFromCSV(invadersDict, csvDict, name='Space Invaders OC')
    gpxLib.saveGpx(updatedGpxFromCsv, Path('X:/Utilisateur/Documents/drouDSP/ressources/Space Invaders OC.gpx'))
    gpxLib.visualizeGpx(updatedGpxFromCsv)
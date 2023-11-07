import argparse
import logging
import os, sys
from pathlib import Path

sys.path.append(Path(os.getcwd()).as_posix())
from src.lib.OpenStreetMap import gpx as gpxLib
from src.lib.OpenStreetMap import invadersEditor


def getArgs():
    parser = argparse.ArgumentParser(
        description="Plot space invaders map from web and gpx",
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=2000, width=1000),
    )
    parser.add_argument("-gpx", "--gpxPath", help="str path of space invaders gpx", default="ressources/Space Invaders.gpx")
    parser.add_argument("-c", "--city", help="city filter prefix", default="ROM")
    parser.add_argument("-f", "--flashed", help="Shows flashed invaders or not", default=False)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    argument = getArgs()
    invadersDict = invadersEditor.getGpxInvaders(gpxPath=argument.gpxPath, cityFilter=argument.city)
    stateDict = invadersEditor.getInvaderSpotterStateInfos(invadersDict)
    invadersDict = invadersEditor.updateInvadersDictFromStateDict(invadersDict=invadersDict, stateDict=stateDict, showFlashed=argument.flashed)
    newGpx = invadersEditor.createGpxFromInvadersDict(invadersDict=invadersDict, name='Space Invaders')
    gpxLib.visualizeGpx(newGpx)
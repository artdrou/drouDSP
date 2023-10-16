import logging
import gpxpy
import gpxpy.gpx
import csv
from pathlib import Path
import folium
import webbrowser


class WAYPOINT_PROPERTIES:
    ICON = "icon"
    COLOR = "color"
    BACKGROUND = "background"
    HIDDEN = "hidden"


def openGpx(gpxPath: Path) -> gpxpy.gpx.GPX:
    """Open gpx file and parse it.

    Args:
        gpxPath (Path): Path of gpx file.

    Returns:
        gpxpy.gpx.GPX: Parsed gpx file.
    """
    gpx_file = open(gpxPath, 'r')
    gpx = gpxpy.parse(gpx_file)
    return gpx


def saveGpx(gpx: gpxpy.gpx.GPX, path: Path) -> None:
    """Saves gpx file

    Args:
        gpx (gpxpy.gpx.GPX): Gpx parsed file.
        path (Path): Path of sved file.
    """
    with open(path, "w") as f:
        f.write(gpx.to_xml())

def getWaypointProperty(waypoint: gpxpy.gpx.GPXWaypoint, property: WAYPOINT_PROPERTIES) -> str:
    """Replace property of waypoint.

    Args:
        waypoint (gpxpy.gpx.GPXWaypoint): Waypoint.
        property (WAYPOINT_PROPERTIES): Name of the property.

    Returns:
        str: Property text of waypoint.
    """
    for idx in waypoint.extensions:
        if property in idx.tag:
            waypointIcon = idx.text
        else:
            logging.warning(f"No {property} found on waypoint")
    return waypointIcon


def replaceWaypointProperty(waypoint: gpxpy.gpx.GPXWaypoint, property: WAYPOINT_PROPERTIES, propertyText: str) -> gpxpy.gpx.GPXWaypoint:
    """Replace property of waypoint.

    Args:
        waypoint (gpxpy.gpx.GPXWaypoint): Waypoint.
        property (WAYPOINT_PROPERTIES): Name of the property.
        iconName (str): Name of property.

    Returns:
        gpxpy.gpx.GPXWaypoint: Waypoint with property text replaced.
    """
    for idx in waypoint.extensions:
        if property in idx.tag:
            idx.text = propertyText
        else:
            logging.warning(f"No color found on waypoint")
    return waypoint


def visualizeGpx(gpx):
    m = folium.Map(location=[0, 0], zoom_start=10)
    for waypoint in gpx.waypoints:
        # Get the waypoint name, symbol, and color
        name = waypoint.name if waypoint.name else "Waypoint"
        symbol = waypoint.symbol
        color = getWaypointProperty(waypoint, 'color')
        lastWaypointLocation = [waypoint.latitude, waypoint.longitude]
        # Create a marker with the specified icon and color
        # icon = folium.Icon(icon_color=color, color=color)
        # folium.Marker(
        #     location=[waypoint.latitude, waypoint.longitude],
        #     icon=icon,
        #     popup=name,
        # ).add_to(m)
        folium.CircleMarker(
            [waypoint.latitude, waypoint.longitude],
            radius=6,
            color=color,
            fill_color=color,
            fill=True,
            fill_opacity=1
            ).add_to(m)
    m.location = lastWaypointLocation
    m.save("waypoints_map.html")
    webbrowser.open("waypoints_map.html")


if __name__ == '__main__':
    pass







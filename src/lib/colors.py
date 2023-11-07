import logging


def convertRGBtoHEX(rgbList: list[int, int, int]) -> str:
    """Converts Rgb color list to HEX str format

    Args:
        rgbList (list[int, int, int]): List of R, G and B values.

    Returns:
        str: Hex color (#000000)
    """
    return "#{:02X}{:02X}{:02X}".format(int(rgbList[0]), int(rgbList[1]), int(rgbList[2]))


def convertHEXToRGB(hexColor: str) -> list:
    """Converts Hex color str to rgb list.

    Args:
        hexColor (str): Hex color str.

    Returns:
        list: List of R, G and B values.
    """
    return [int(hexColor.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]


def saturateRGB(rgbList: list[int, int, int], factor: float) -> list[int, int, int]:
    """saturate rgb color according to a factor

    Args:
        rgbList (list[int, int, int]): list of R, G and B values.
        factor (float): saturation factor (min 0).

    Returns:
        list[int, int, int]: saturated Rgb list.
    """
    if not 0 < factor:
        logging.warning("Cannot input a factor lower than 0, set to 0")
        factor = 0
    saturatedRgbList = []
    for value in rgbList:
        value *= factor
        if value >= 255:
            value = 255
        saturatedRgbList.append(value)
    return saturatedRgbList


def saturateHEX(hexColor: str, factor: float) -> str:
    """saturate hex color according t oa factor

    Args:
        hexColor (str): list of R, G and B values.
        factor (float): saturation factor (min 0).

    Returns:
        str: saturated hex str.
    """
    rgbList = convertHEXToRGB(hexColor)
    rgbList = saturateRGB(rgbList, factor)
    saturatedHexColor = convertRGBtoHEX(rgbList)
    return saturatedHexColor
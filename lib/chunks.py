import numpy as np


def frameSignal(x: np.ndarray, frameLength: int, overlapLength: int) -> np.ndarray:
    """Splits signal into multiple chunks with defined overlay size.

    Args:
        x (np.ndarray): Signal.
        frameLength (int): length of each chunk (in indexes).
        overlapLength (int): length of overlapp between each chunk (in indexes).

    Returns:
        np.ndarray: array of chunks.
    """
    framedSignal = []
    indexStatus = 0
    while indexStatus <= len(x)-frameLength:
        framedSignal.append(x[indexStatus:indexStatus+frameLength])
        indexStatus += overlapLength
    framedSignal = np.array(framedSignal)
    framedSignal = np.transpose(framedSignal)
    return framedSignal


def overlapAndAdd(framedSignal: np.ndarray, overlapLength: int, frameLength: int) -> np.ndarray:
    """Contruct temporal signal from array of chunks.

    Args:
        framedSignal (np.ndarray): signal splitted into multiple chunks.
        overlapLength (int, optional): length of overlapp between each chunk (in indexes).
        frameLength (int, optional): length of each chunk (in indexes).

    Returns:
        np.ndarray: temporal signal.
    """
    signal = []
    n = 0
    while n < np.shape(framedSignal)[1]:
        overlapSum = framedSignal[:int(frameLength/2), n] + framedSignal[int(frameLength/2):, n-1]
        signal.append(overlapSum)
        n += 1
    signal = np.concatenate(signal)
    return signal

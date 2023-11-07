from pathlib import Path
import soundfile
import sounddevice
import numpy as np
import numpy.fft as fft
import matplotlib.pyplot as plt
import scipy.signal


def keepFftPositiveF(fastft: np.ndarray) -> np.ndarray:
    """keeps only positive frequencies indexes of a fft

    Args:
        fastft (np.ndarray): input fft with positive and negative frequencies

    Returns:
        np.ndarray: output fft with only positive frequency indexes.
    """
    if len(fastft)%2 == 0:
        posfft = fastft[0: int(np.floor(len(fastft)/2))]
    else:
        posfft = fastft[0: int(np.floor(len(fastft)/2)+1)]
    return posfft


def addFftNegativeF(fastft: np.ndarray) -> np.ndarray:
    """Adds the negative frequency indexes to a only positive frequency indexes fft

    Args:
        fastft (np.ndarray): fft with only positive frequency indexes.

    Returns:
        np.ndarray: output complete fft.
    """
    if len(fastft)%2 == 0:
        symFft = np.flip(np.conj(fastft))
        fastft = np.concatenate((fastft, symFft[2:-1]))
    else:
        symFft = np.flip(np.conj(fastft))
        fastft = np.concatenate((fastft, symFft[1:-1]))
    return fastft

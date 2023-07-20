from pathlib import Path
import soundfile
import sounddevice
import os, sys
import numpy as np
import numpy.fft as fft
import matplotlib.pyplot as plt
import scipy.signal

import chunks
import fourierTransforms as ft


def computeFft(x: np.ndarray, n: int=None) -> np.ndarray:
    """Overlay function to compute positive frequency indexes fft

    Args:
        x (np.ndarray): signal.
        n (int, optional): nfft. Defaults to None.

    Returns:
        np.ndarray: fft
    """
    if n is None:
        n = len(x)
    xfft = fft.fft(x, n)
    return ft.keepFftPositiveF(xfft)

def computeIfft(xfft: np.ndarray) -> np.ndarray:
    """Computes temporal signal from positive frequency indexes fft.

    Args:
        xfft (np.ndarray): positive frequency indexes fft

    Returns:
        np.ndarray: temporal signal.
    """
    x = fft.ifft(ft.addFftNegativeF(xfft))
    return x


def computeStft(x: np.ndarray, overlapLength: int, ndft: int) -> np.ndarray:
    """computes short term fourier transform of temporal signal.

    Args:
        x (np.ndarray): signal.
        overlapLength (int): length of overlapp between each chunk (in indexes).
        ndft (int): size of fourier transform.

    Returns:
        np.ndarray: Short term fourier transform.
    """
    framedSignal = chunks.frameSignal(x, ndft, overlapLength)
    window = np.sin(np.linspace(0, np.pi, ndft))
    stft = np.zeros((int(ndft/2+1),np.shape(framedSignal)[1]), dtype=complex)
    for n in range(np.shape(stft)[1]):
        stft[:, n] = computeFft(framedSignal[:, n]*window)
    return stft


def computeIstft(stft: np.ndarray, overlapLength: int, ndft: int) -> np.ndarray:
    """Computes signal from stft by applying inverse short term fourier transform.

    Args:
        stft (np.ndarray): Short term fourier transform of a signal.   
        overlapLength (int): length of overlapp between each chunk (in indexes).
        ndft (int): size of fourier transform.

    Returns:
        np.ndarray: _description_
    """
    framedSignal = np.zeros((ndft,np.shape(stft)[1]))
    window = np.sin(np.linspace(0, np.pi, ndft))
    for n in range(np.shape(stft)[1]):
        framedSignal[:, n] = computeIfft(stft[:, n])*window
    signal = chunks.overlapAndAdd(framedSignal, overlapLength, ndft)
    return signal


def _processStft(stft: np.ndarray, fs: int, nfft: int):
    """Example function of processing on frequency domain. (low pass filter)

    Args:
        stft (np.ndarray): Short term fourier transform.
        fs (int): sampling frequency.
        nfft (int): fourier transform size.
    """
    b, a = scipy.signal.iirfilter(2, Wn=1000, fs=fs, btype="low", ftype="butter")
    _, h = scipy.signal.freqz(b=b, a=a, worN=int(nfft/2+1), fs=fs)
    for n in range(np.shape(stft)[1]):
        stft[:, n] = h*stft[:, n]


if __name__ == '__main__':
    # input parameters
    nfft = 4096
    hopLength = int(nfft/2)
    # file loading
    audiopath = Path("C:/Users/drew/Documents/audio/resources/moron.wav")
    data, rate = soundfile.read(file=audiopath)
    # make mono
    data = data[:, 0] 
    # STFT
    myStft = computeStft(data, overlapLength=hopLength, ndft=nfft)
    # Processing STFT(not mandatory)
    # _processStft(myStft, rate, nfft)
    # ISTFT
    signal = computeIstft(myStft, overlapLength=hopLength, ndft=nfft)
    # Play signal
    # sounddevice.play(signal, rate)
    # plot signal to compare to original
    plt.figure()
    plt.plot(data)
    plt.plot(signal, linewidth=0.5)
    plt.grid()
    plt.show()

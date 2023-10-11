import numpy
import scipy
import pyaudio
import sounddevice
from scipy.io.wavfile import read
import matplotlib.pyplot as plt
import stft


FADE_LINEAR = 'linear'
FADE_HANNING = 'hanning'


def fadeSignal(
    signal: numpy.ndarray, fs: int, fadeInLength: float = 0.25, fadeOutlength: float = 0.25, fadeType: str = FADE_LINEAR
):
    """Adds fade in & fade out to a signal.

    Args:
        signal (numpy.ndarray): Audio signal.
        fs (int): Sampling frequency, rate (in Hz).
        fadeInLength (float, optional): Length (in s) of the fade in. Defaults to 0.25.
        fadeOutlength (float, optional): Length (in s) of the fade out. Defaults to 0.25.
        fadeType (str, optional): Type of the fade,
            can be linear or following hanning enveloppe. Defaults to 'linear'.

    Returns:
        numpy.ndarray: Audio signal with fade in and fade out.
    """

    fs = int(fs)
    NfadeInLength = fadeInLength * fs
    NfadeOutLength = fadeOutlength * fs
    if fadeType == FADE_LINEAR:
        fadeIn = numpy.linspace(start=0, stop=1, num=int(NfadeInLength))
        fadeOut = numpy.linspace(start=1, stop=0, num=int(NfadeOutLength))
    elif fadeType == FADE_HANNING:
        fadeIn = numpy.hanning(2 * NfadeInLength)
        fadeIn = fadeIn[0 : int(len(fadeIn) / 2)]
        fadeOut = numpy.hanning(int(2 * NfadeOutLength))
        fadeOut = fadeOut[int(len(fadeOut) / 2) :]

    window = numpy.ones(len(signal))
    window[0 : len(fadeIn)] = fadeIn
    window[len(window) - len(fadeOut) :] = fadeOut
    fadedSignal = signal * window
    return fadedSignal


def generateSweptSineArray(
    amp: float = 0.75,
    f0: float = 20,
    f1: float = 20000,
    temporal_array: list = None,
    duration: float = 10,
    fs: int = 48000,
    fade: bool = True,
    novak: bool = False,
):
    """Generates a Sweptsine, from f0 to f1, with a possibility to satisfy novaks conditions
        (based on https://www.ant-novak.com/publications/papers/2010_ieee_novak.pdf).

    Args:
        amp (float): amplitudes of swept sine.
        f0 (float): start frequency (in Hz).
        f1 (float): end frequency (in Hz).
        t (list, optional): time vector.
        duration (float): Duration (in seconds) of the swept sine,
                        duration may slighty change if novak conditions are respected
        fs (int): sampling frequency, rate (in Hz)
        fade (bool): if True, creates a fade in and out on the swept sine.
        novak (bool): imposes novaks condition to Dt between 2 instantaneous frequencies,
                        usefull to easily deconvolute input from output recording,
                        and separate fondamental signal and harmonic signals.
    Returns:
        t (list): time vector corresponding to x data
        x (list): list of amplitudes of the swept sine
        instFreq (list): list of instantaneous frequencies corresponding to time t
    """
    fs = int(fs)

    if temporal_array is None:
        temporal_array = numpy.linspace(0, duration, int(duration * fs))

    if novak is True:
        temporal_array = None
        L = numpy.floor((f0 * duration) / numpy.log(f1 / f0)) / f0
        newDuration = L * numpy.log(f1 / f0)
        temporal_array = numpy.linspace(0, duration, int(newDuration * fs))
    else:
        L = duration / numpy.log(f1 / f0)
    instFreq = f0 * numpy.exp(temporal_array / L)

    signal = amp * numpy.sin(2 * numpy.pi * f0 * L * (numpy.exp(temporal_array / L) - 1))
    if fade is True:
        signal = fadeSignal(signal, fs, fadeInLength=0.25, fadeOutlength=0.05)

    return temporal_array, signal, instFreq


if __name__ == "__main__":
    fs = 48000
    r1 = 10
    t, x, ft = generateSweptSineArray(amp=0.95, f0=20, f1=20000, duration=3, fs=fs, fade=True)
    xfft = stft.computeFft(x)
    measurement = True
    speaker = 1
    plt.figure()
    # Open stream with correct settings
    print('playing')
    recordedSignal = sounddevice.playrec(
            x, samplerate=fs,
            blocking=True,
            input_mapping=[1, 2]
            )
    vSpk = recordedSignal[:, 0]
    vRes = recordedSignal[:, 1]
    ySpkFft = stft.computeFft(vSpk)
    freq = stft.computeFftFreq(vSpk, fs)
    yResFft = stft.computeFft(vRes)
    zImp = r1*(ySpkFft/yResFft)
    plt.subplot(211)
    plt.semilogx(freq, abs(zImp))
    plt.xlim(20, 20000)
    plt.ylim(0, 12)
    plt.subplot(212)
    plt.semilogx(freq, numpy.angle(zImp))
    plt.xlim(20, 20000)
    plt.show()
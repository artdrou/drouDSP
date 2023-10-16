import scipy.io.wavfile
import scipy.signal
import matplotlib.pyplot as plt
import logging
import numpy
from pathlib import Path
import soundfile
import constants.dsp
import constants.inputs


# ------------------------------------------ Generation constants ------------------------------------------------------
ZERO_PADDING_MOD_START = "start"
ZERO_PADDING_MOD_MIDDLE = "mid"
ZERO_PADDING_MOD_END = "end"


def generateSweptsine(
    amp: float = constants.inputs.FULL_SCALE_AMPLITUDE,
    f0: float = constants.inputs.AUDIO_BANDWIDTH[0],
    f1: float = constants.inputs.AUDIO_BANDWIDTH[1],
    temporal_array: list = None,
    duration: float = constants.inputs.SWEPTSINE_DURATION_LONG,
    fs: int = constants.dsp.DEFAULT_RATE,
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


def generateSweptsineWithPulses(
    amp: float = constants.inputs.FULL_SCALE_AMPLITUDE,
    f0: float = constants.inputs.AUDIO_BANDWIDTH[0],
    f1: float = constants.inputs.AUDIO_BANDWIDTH[1],
    duration: float = constants.inputs.SWEPTSINE_DURATION_LONG,
    fs: int = constants.dsp.DEFAULT_RATE,
    fade: bool = True,
    novak: bool = False,
    outputPath: Path = None,
):
    """Generates a Sweptsine wavfile based on generate sweptsine array function.

    Args:
        amp (float): Amplitudes of swept sine.
        f0 (float): Start frequency (in Hz).
        f1 (float): End frequency (in Hz).
        duration (float): Duration (in seconds) of the swept sine,
            duration may slightly change if novak conditions are respected.
        fs (int): Sampling frequency, rate (in Hz).
        fade (bool): If True, creates a fade in and out on the swept sine.
        novak (bool): Imposes novaks condition to Dt between 2 instantaneous frequencies,
            useful to easily deconvolute input from output recording,
            and separate fundamental signal and harmonic signals.
        outputPath: (Path): Filepath of the output wavfile
    """
    fs = int(fs)

    _, signal, _ = generateSweptsine(amp=amp, f0=f0, f1=f1, duration=duration, fs=fs, fade=fade, novak=novak)
    generateAudioWithSyncPulses(signal, fs, "V2", outputPath)


def getSweptSineInstantaneousFrequency(
    duration: float = constants.inputs.SWEPTSINE_DURATION_LONG,
    f0: float = constants.inputs.AUDIO_BANDWIDTH[0],
    f1: float = constants.inputs.AUDIO_BANDWIDTH[1],
    rate: int = constants.dsp.DEFAULT_RATE,
) -> list:
    """
    Returns the instantaneous frequency according to sweep parameters
    """
    return f0 * numpy.exp(numpy.linspace(0, duration, int(duration * rate)) / (duration / numpy.log(f1 / f0)))


def generateSine(
    amp: float = constants.inputs.FULL_SCALE_AMPLITUDE,
    f0: float = 1000,
    duration: float = 10,
    fs: int = constants.dsp.DEFAULT_RATE,
    fade: bool = False,
):
    """Generates a sine, with f0 frequency, and specific amplitude.

    Args:
        amp (float, optional): Amplitudes of Sine. Defaults to STANDARD_AMPLITUDE.
        f0 (float, optional): Frequency of the sine (in Hz). Defaults to 1000.
        duration (float, optional): Duration (in seconds) of the sine. Defaults to 10.
        fs (int, optional): Sampling frequency, rate (in Hz). Defaults to DEFAULT_RATE.
        fade (bool, optional): If True, creates a fade in and out on the sine. Defaults to False.

    Returns:
        t (numpy.ndarray): Temporal vector.
        signal (numpy.ndarray): Values array of the generated signal.
    """

    fs = int(fs)
    temporal_array = numpy.linspace(0, duration, int(duration * fs))
    signal = amp * numpy.sin(2 * numpy.pi * f0 * temporal_array)
    if fade is True:
        signal = fadeSignal(signal, fs)
    return temporal_array, signal


def generatePulsesArray(gain: float, fs: int, fade: bool = True):
    if fade is True:
        fadeLength = constants.inputs.SYNC_PULSES_FADE_DURATION
    else:
        fadeLength = 0
    pulseLen = constants.inputs.SYNC_PULSE_DURATION
    startPulse = numpy.concatenate(
        (
            fadeSignal(
                generateSine(amp=gain, f0=constants.inputs.PULSES_FREQUENCIES[0], duration=pulseLen, fs=fs)[1],
                fs,
                fadeLength,
                fadeLength,
            ),
            fadeSignal(
                generateSine(amp=gain, f0=constants.inputs.PULSES_FREQUENCIES[1], duration=pulseLen, fs=fs)[1],
                fs,
                fadeLength,
                fadeLength,
            ),
        )
    )
    endPulse = numpy.concatenate(
        (
            fadeSignal(
                generateSine(amp=gain, f0=constants.inputs.PULSES_FREQUENCIES[2], duration=pulseLen, fs=fs)[1],
                fs,
                fadeLength,
                fadeLength,
            ),
            fadeSignal(
                generateSine(amp=gain, f0=constants.inputs.PULSES_FREQUENCIES[3], duration=pulseLen, fs=fs)[1],
                fs,
                fadeLength,
                fadeLength,
            ),
        )
    )
    return startPulse, endPulse


def generateSilenceArray(duration: float, fs: int) -> numpy.ndarray:
    return numpy.zeros(int(duration * fs))


def generateAudioWithSyncPulses(
    audioArray: numpy.ndarray, fs: int = constants.dsp.DEFAULT_RATE, outputPath: Path = None
):
    """Adds SyncPulses to an audio array and exports it to wav.

    Args:
        audioArray ([type]): Audio signal.
        fs (int, optional): Sampling frequency, rate (in Hz). Defaults to DEFAULT_RATE.
        outputPath (Path, optional): Path of the exported file. Defaults to None.

    Raises:
        ValueError: Error raised if audioArray is not a list nor a numpy.ndarray.
    """

    if not isinstance(audioArray, numpy.ndarray) and not isinstance(audioArray, list):
        raise ValueError("Audio array must be list or np.array")
    fs = int(fs)
    # SyncPulses
    pulsesF = constants.inputs.PULSES_FREQUENCIES
    pulseLen = constants.inputs.SYNC_PULSE_DURATION
    toneList = []
    for pulseFrequency in pulsesF:
        toneList.append(numpy.sin(2 * numpy.pi * pulseFrequency * numpy.linspace(0, pulseLen, int(pulseLen * fs))))
    toneS = numpy.concatenate((toneList[0], toneList[1]))
    toneE = numpy.concatenate((toneList[2], toneList[3]))
    # Generate audio silence
    sound = numpy.array([])
    silence = numpy.zeros(int((constants.inputs.SWEPTSINE_START - constants.inputs.SYNC_PULSE_DURATION) * fs))
    for addedSound in [silence, toneS, silence, audioArray, silence, toneE, silence]:
        sound = numpy.concatenate((sound, numpy.array(addedSound)))
    soundfile.write(outputPath, sound, fs)


def fadeSignal(
    signal: numpy.ndarray, fs: int, fadeInLength: float = constants.inputs.FADE_DURATION,
    fadeOutlength: float = constants.inputs.FADE_DURATION, fadeType: str = constants.inputs.FADE_LINEAR
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
    if fadeType == constants.inputs.FADE_LINEAR:
        fadeIn = numpy.linspace(start=0, stop=1, num=int(NfadeInLength))
        fadeOut = numpy.linspace(start=1, stop=0, num=int(NfadeOutLength))
    elif fadeType == constants.inputs.FADE_HANNING:
        fadeIn = numpy.hanning(2 * NfadeInLength)
        fadeIn = fadeIn[0 : int(len(fadeIn) / 2)]
        fadeOut = numpy.hanning(int(2 * NfadeOutLength))
        fadeOut = fadeOut[int(len(fadeOut) / 2) :]
    window = numpy.ones(len(signal))
    window[0 : len(fadeIn)] = fadeIn
    window[len(window) - len(fadeOut) :] = fadeOut
    fadedSignal = signal * window
    return fadedSignal


def getZeroPaddedArray(signal: numpy.ndarray, length: int, mode: str = ZERO_PADDING_MOD_END):
    """Match signal length with a desired length by adding zeropadding.

    Args:
        signalPadded (list, numpy.ndarray): signal to zeropad.
        length (int): output signal length
        mode (str, optional): Where to add zero padding (start, end or mid). Defaults to 'end'.

    Returns:
        (list, numpy.ndarray): Signal zeropadded.
    """
    if length < len(signal):
        raise ValueError("Cannot zeroPad to a shorter length")
    signalPadded = numpy.zeros(length)
    if mode == ZERO_PADDING_MOD_END:
        signalPadded[: len(signal)] = signal
    elif mode == ZERO_PADDING_MOD_START:
        signalPadded[len(signalPadded) - len(signal) :] = signal
    elif mode == ZERO_PADDING_MOD_MIDDLE:
        signalPadded[int((length - len(signal)) / 2) : int((length + len(signal)) / 2)] = signal
    return signalPadded


def getLag(signal1: numpy.ndarray, signal2: numpy.ndarray, rate: int = constants.dsp.DEFAULT_RATE, plot: bool = False):
    """Return lag in number of indexes and/or seconds between signals of same length x1 and x2

    Args:
        signal1 (list, numpy.ndarray): Array number 1.
        signal2 (list, numpy.ndarray): Array number 2.
        rate (int): Sampling rate/frequency (in Hz).
        plot (bool, optional): [description]. Defaults to False.

    Returns:
        int: Lag between the 2 arrays (in indexes).
    """
    if len(signal1) != len(signal2):
        logging.info("signal1 and signal2 are not the same length, zero padding applied prior to lag computation")
        maxlen = max(len(signal1), len(signal2))
        signal1 = getZeroPaddedArray(signal1, maxlen)
        signal2 = getZeroPaddedArray(signal2, maxlen)
    bH, aH = scipy.signal.butter(N=2, Wn=20, btype="high", fs=rate, output="ba")
    signal1 = scipy.signal.filtfilt(bH, aH, signal1)
    signal2 = scipy.signal.filtfilt(bH, aH, signal2)
    x1x2Corr = scipy.signal.correlate(signal1, signal2, mode="same")
    lags = numpy.arange(int(-len(signal1) / 2), int(len(signal1) / 2))
    lag = lags[numpy.argmax(x1x2Corr)]

    if plot:
        plt.figure()
        plt.plot(lags, x1x2Corr)
        plt.grid()
        plt.show()
    return lag


def delayByLag(signal: numpy.ndarray, lag: int):
    """Delay a signal by a number of indexes

    Args:
        signal (list, numpy.ndarray): sigal to delay.
        lag (int): number of indexes that the signal will be delayed off.

    Returns:
        (list, numpy.ndarray): Delayed signal.
    """
    xDelay = numpy.roll(signal, lag)
    if lag > 0:
        xDelay[0:lag] = 0
    elif lag < 0:
        xDelay[len(xDelay) + lag :] = 0
    return xDelay

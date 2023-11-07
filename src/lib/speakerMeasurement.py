import numpy
import sounddevice
import matplotlib.pyplot as plt
import stft
import time
import signalGeneration


def measureChannels(signal: numpy.ndarray, fs: int, mapping: list, averages: int=1, window: numpy.ndarray=None) -> tuple:
    """Measure fft of input channels

    Args:
        signal (numpy.ndarray): Input signal.
        fs (int): Sample frequency.
        mapping (list): Input mapping list.
        averages (int, optional): Number of measurement averages. Defaults to 1.
        window (numpy.ndarray, optional): Measurement Window. Defaults to None.

    Returns:
        tuple: Tuple of frequecy list and fft complex amplitudes.
    """
    for nn in range(averages):
        recordedSignal = sounddevice.playrec(
                signal, samplerate=fs,
                blocking=False,
                input_mapping=mapping
                )
        time.sleep(1.25*(len(signal)/fs))
        freq = stft.computeFftFreq(recordedSignal[:, 0], fs)
        signalFft = numpy.zeros((int(recordedSignal.shape[0]/2), recordedSignal.shape[1]), dtype='complex')
        for channel in range(recordedSignal.shape[1]):
            v = recordedSignal[:, channel]/averages
            if window is not None:
                _signalFft = stft.computeFft(numpy.multiply(v, window))
            else:
                _signalFft = stft.computeFft(v)
            signalFft[:, channel] = numpy.add(signalFft[:, channel], _signalFft)
    return freq, signalFft


def computeComplexImpedence(fft1: numpy.ndarray, fft2:numpy.ndarray, r: float) -> numpy.ndarray:
    """Computes complex impedance of measurement circuit.

    Args:
        fft1 (numpy.ndarray): fft of voltage measurement of speaker and resistor.
        fft2 (numpy.ndarray): fft of voltage measurement of resistor only.
        r (float): Resistor impedence value (in ohms)

    Returns:
        numpy.ndarray: Complex impedence of speaker.
    """
    return r*(numpy.divide(fft1, fft2) - 1)


def computeTransferFunction(fft1: numpy.ndarray, fft2:numpy.ndarray) -> numpy.ndarray:
    """Computes Transfer function response of 2 signals fft.

    Args:
        fft1 (numpy.ndarray): Fft of signal 1.
        fft2 (numpy.ndarray): Fft of signal 2.

    Returns:
        numpy.ndarray: Tranfer function response.
    """
    return numpy.divide(fft1, fft2)


def plotComplexImpedance(zImpList, frequencyList, bandwidth):
    if isinstance(zImpList, list) is not True:
        zImpList = [zImpList]
    plt.figure()
    for idx, zImp in enumerate(zImpList):
        plt.subplot(211)
        plt.semilogx(frequencyList, abs(zImp), label=f"Spk {idx+1}")
        plt.grid()
        plt.xlim(bandwidth)
        plt.ylim(0, 30)
        plt.subplot(212)
        plt.semilogx(frequencyList, numpy.angle(zImp))
        plt.xlim(bandwidth)
        plt.grid()
    plt.legend()
    plt.show()


def plotTransferFunction(frequencyList, tfList):
    if isinstance(tfList, list) is not True:
        tfList = [tfList]
    plt.figure()
    for idx, tf in enumerate(tfList):
        plt.subplot(211)
        plt.semilogx(frequencyList, 20*numpy.log10(abs(tf)), label=f"Spk {idx+1}")
        amp = max(20*numpy.log10(abs(tf)))
        plt.plot([20, 20000], [amp, amp], 'r', label=round(amp, 2))
        plt.legend()
        plt.grid()
        plt.xlim(20, 20000)
        plt.subplot(212)
        plt.semilogx(frequencyList, numpy.angle(tf))
        plt.xlim(20, 20000)
        plt.grid()
    plt.show()


def measureMultipleSpeakersImpedances(signal, fs, averages, nSpeakers, rValue, bandwidth):
    speaker = 1
    stop = False
    zImpList = []
    while stop != True and speaker <= nSpeakers:
        if nSpeakers > 1:
            yesNo = input(f"measure speaker {speaker}: (y/n)")
        else:
            yesNo = 'y'
        if yesNo == 'y':
            freq, signalFft = measureChannels(signal, fs, [1, 2], averages)
            zImp = computeComplexImpedence(signalFft[:, 0], signalFft[:, 1], rValue)
            zImpList.append(zImp)
            speaker += 1
        else:
            stop = True
    plotComplexImpedance(zImpList=zImpList, frequencyList=freq, bandwidth=bandwidth)


def measureTransfertFunction(signal, fs, averages):
    freq, signalFft = measureChannels(signal, fs, [1, 2], averages)
    tf = computeTransferFunction(signalFft[:, 0], signalFft[:, 1])
    plotTransferFunction(frequencyList=freq, tfList=tf)


if __name__ == "__main__":
    fs = 48000
    bandwidth = [5, 5000]
    r1 = 1
    averages = 5
    duration = 1
    t, x, _ = signalGeneration.generateSweptsine(amp=0.95, f0=bandwidth[0], f1=bandwidth[1], duration=duration, fs=fs, fade=True)
    measureMultipleSpeakersImpedances(x, fs, averages, 1, r1, bandwidth)
    

1. Dependency:
    1. pyaudio
    2. numpy
    3. matplotlib
    4. scipy

2. Module structure:
    2.1 preprocess.py: 
            Interface: 
                signal_to_powerspec(signal, fs = 8000, wlen = 0.025, inc = 0.01, nfft = 512, preemph = 0.9375, endpoint = False, show = False):
                    """Convert from audio signal to power spectrum

                    :param signal: raw audio signal(16-bit).
                    :param fs: sample rate, default is 8000 Hz
                    :param wlen: length of every frame in seconds, default is 25 ms
                    :param inc: the steps between successive windows in seconds, default is 10 ms
                    :param nfft: the fft length to use, default is 512.
                    :param preemph: apply preemphasis filter with preemph as coefficient. 0 is no filter. Default is 0.9375.
                    :param endpoint: whether to apply end-point detection when doing frame job, default is False.
                    :param show: whether plot frames based on end-point detection, defualt is False.

                    :returns: A numpy array of size fn * nfft. Each row holds power spectrum of one frame.
                    """
                    
    2.2 mfcc.py:
            Interface:
                mfcc(signal, fs = 8000, wlen = 0.025, inc = 0.01, nfft = 512, nfilt = 26, numcep = 13, lowfreq = 0, highfreq = None, preemph = 0.9375,
             ceplifter = 22, endpoint = False, appendEnergy = False):
                    """Compute MFCC features from audio signal.

                    :param signal: raw audio signal(16-bit).
                    :param fs: sample rate, default is 8000 Hz
                    :param wlen: length of every frame in seconds, default is 25 ms
                    :param inc: the steps between successive windows in seconds, default is 10 ms
                    :param nfft: the fft length to use, default is 512.
                    :param nfilt: the amount of filter bands to be used, default is 26.
                    :param numcep: the number of cepstrum to return, default is 13
                    :param lowfreq: lowest band edge of mel filters. In Hz, default is 0.
                    :param highfreq: highest band edge of mel filters. In Hz, default is samplerate/2
                    :param preemph: apply preemphasis filter with preemph as coefficient. 0 is no filter. Default is 0.9375.
                    :param ceplifter: apply a lifter to final cepstral coefficients. 0 is no lifter. Default is 22.
                    :param endpoint: whether to apply end-point detection when doing frame job, default is False.
                    :param appendEnergy: replace first cepstral coefficient of each frame with the log of it's total frame energy, default is Flase.

                    :returns: A numpy array of size fn * numcep. Each row holds one MFCC feature vector.
                    """
                          
    2.3 dtw.py:
            Interface:
                dtw(r, t):
                    """Calculate similarities between two non-indentical length series(But each frame vector has same size).

                    :param r: Reference template. Numpy array.
                    :param t: Test template. Numpy array.
                    :returns: Similarity score.
                    """






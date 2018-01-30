
"""A python implementation of the Goertzel algorithm to decode DTMF tones.
 
The wave file is split into bins and each bin is analyzed
for all the DTMF frequencies. The method run() will return a numeric
representation of the DTMF tone.
"""

import math
import os
import re
import struct
import wave
from shutil import copy
from time import time

from mtaf.user_exception import UserException as Ux
from pkg_resources import Requirement, resource_filename

hi = [1209.0, 1336.0, 1477.0, 1633.0]
lo = [697.0, 770.0, 852.0, 941.0]
digits = {
    (lo[0], hi[0]): '1',
    (lo[0], hi[1]): '2',
    (lo[0], hi[2]): '3',
    (lo[0], hi[3]): 'A',
    (lo[1], hi[0]): '4',
    (lo[1], hi[1]): '5',
    (lo[1], hi[2]): '6',
    (lo[1], hi[3]): 'B',
    (lo[2], hi[0]): '7',
    (lo[2], hi[1]): '8',
    (lo[2], hi[2]): '9',
    (lo[2], hi[3]): 'C',
    (lo[3], hi[0]): '*',
    (lo[3], hi[1]): '0',
    (lo[3], hi[2]): '#',
    (lo[3], hi[3]): 'D'
}
coeff = {}
framestart = None


def make_coeff(samplerate):
    global coeff
    for k in hi + lo:
        normalizedfreq = k / samplerate
        coeff[k] = 2.0*math.cos(2.0 * math.pi * normalizedfreq)


class PygoertzelDtmf:
    def __init__(self, samplerate):
        global coeff
        self.samplerate = samplerate
         
        self.s_prev = {}
        self.s_prev2 = {}
        self.totalpower = {}
        self.N = {}

        # create goertzel parameters for each frequency so that
        # all the frequencies are analyzed in parallel
        for k in hi + lo:
            self.s_prev[k] = 0.0
            self.s_prev2[k] = 0.0
            self.totalpower[k] = 0.0
            self.N[k] = 0.0
             
            # normalizedfreq = k / self.samplerate
            # self.coeff[k] = 2.0*math.cos(2.0 * math.pi * normalizedfreq)

    @staticmethod
    def __get_number(freqs):
        # hi = [1209.0,1336.0,1477.0,1633.0]
        # lo = [697.0,770.0,852.0,941.0]
         
        # get hi freq
        hifreq = 0.0
        hifreq_v = 0.0
        for f in hi:
            if freqs[f] > hifreq_v:
                hifreq_v = freqs[f]
                hifreq = f
         
        # get lo freq
        lofreq = 0.0
        lofreq_v = 0.0
        for f in lo:
            if freqs[f] > lofreq_v:
                lofreq_v = freqs[f]
                lofreq = f

        if (lofreq, hifreq) in digits:
            return digits[(lofreq, hifreq)]
        else:
            return ''

    def run(self, sample):
        freqs = {}
        for freq in hi + lo:
            s = sample + (coeff[freq] * self.s_prev[freq]) - self.s_prev2[freq]
            self.s_prev2[freq] = self.s_prev[freq]
            self.s_prev[freq] = s
            self.N[freq] += 1
            power = (self.s_prev2[freq] * self.s_prev2[freq]) \
                + (self.s_prev[freq]*self.s_prev[freq]) \
                - (coeff[freq]*self.s_prev[freq]*self.s_prev2[freq])
            self.totalpower[freq] += sample*sample
            if self.totalpower[freq] == 0:
                self.totalpower[freq] = 1
            freqs[freq] = power / self.totalpower[freq] / self.N[freq]
        return self.__get_number(freqs)


def dtmf_seq_in_wav(fname, seq, wavdir='.', verbose=False):
    # - seq is a string made up of dtmf ascii characters and possibly commas
    # - fname is name of a .wav file
    # - if seq has no commas, search fname  for a sequence of dtmf digits in that order, with no other
    #   digits detected in between the elements in the sequence
    # - presence of an unexpected dtmf tone causes the sequence-detection process to start over
    # - search continues until sequence found
    # - returns True if the sequence is found, otherwise returns False
    # - for patterns separated by commas, checks for the patterns one after the other, and returns True
    #   if all are found in order, otherwise returns False
    global framestart
    src = os.path.join(wavdir, fname)
    wav = wave.open(src, 'r')
    (nchannels, sampwidth, framerate, nframes, comptype, compname) = wav.getparams()
    make_coeff(framerate)
    frames = wav.readframes(nframes * nchannels)
    frames = struct.unpack_from("%dH" % nframes * nchannels, frames)
    retval = True
    framestart = 0
    for _seq in seq.split(','):
        if not search_wav_for_seq(frames, framerate, _seq, verbose):
            retval = False
    wav.close()
    # save a copy of the wav file if the test fails
    if wavdir != '.' and retval is False:
        dst = '%s%s_%s' % (wavdir, int(time()), fname)
        copy(src, dst)
    return retval


def search_wav_for_seq(frames, framerate, seq, verbose):
    binsize = 400
    global framestart
    # Split the bin in 4 to average out errors due to noise
    binsize_split = 4
    prevvalue = ""
    prevcounter = 0
    s = ''
    # Step the starting point through the block of unsigned ints 100 at a time, and run the
    # goertzel algorithm on a each unsigned int in the group of 400 values starting at that
    # point, one unsigned int at a time; use the last of the 400 values returned for the group
    # as the calculated dtmf digit
    # The algorithm is initialized by creating a class object at the beginning
    # of each increment of the group starting point
    for i in range(framestart, len(frames)-binsize, binsize/binsize_split):
        goertzel = PygoertzelDtmf(framerate)
        for j in frames[i:i+binsize]:
            value = goertzel.run(j)
        if value == prevvalue:
            prevcounter += 1
            # adds dtmf value to the string and checks for a match after 10
            # identical readings, but if the desired string has not been found
            # yet, keeps incrementing prevcounter until value changes (gap between tones)
            if prevcounter == 10:
                s += str(value)
                if verbose:
                    if value == '':
                        print '.',
                    else:
                        print value,
                if s.find(seq) != -1:
                    if verbose:
                        print
                        print s
                    framestart = i
                    return True
        else:
            prevcounter = 0
            prevvalue = value
    if verbose:
        print
    return False


def create_wav_file(path, quiet=False):
    dtmf_match = re.match('dtmf_([\d\*#]+)\.wav', os.path.basename(path))
    voice_match = re.match('([\d\*#]+)\.wav', os.path.basename(path))
    if dtmf_match:
        # join dtmf tones with silence gap, end with dtmf '#'
        source_keys = list('s'.join(list(dtmf_match.group(1) + '#')))
        use_dtmf = True
    elif voice_match:
        # just add an a440 tone to the end of voice prompt files
        source_keys = list(voice_match.group(1) + 'a')
        use_dtmf = False
    else:
        raise Ux('unable to create wav file %s' % path)
    source_wav_dir = resource_filename(Requirement.parse("mtaf"), "mtaf/wav")
    # generate a new wav file by concatenating the elements
    data = []
    frame_count = 0
    for source_key in source_keys:
        if source_key == 'a':
            if quiet:
                source_wav = 'a440q.wav'
            else:
                source_wav = 'a440.wav'
        elif source_key == 's':
            source_wav = 'silence_120ms.wav'
        else:
            if use_dtmf:
                if source_key == '#':
                    source_wav = 'dtmf_pound.wav'
                elif source_key == '*':
                    source_wav = 'dtmf_star.wav'
                else:
                    source_wav = 'dtmf_%s.wav' % source_key
            else:
                if source_key == '#':
                    source_wav = 'pound.wav'
                elif source_key == '*':
                    source_wav = 'star.wav'
                else:
                    if quiet:
                        source_wav = '%sq.wav' % source_key
                    else:
                        source_wav = '%s.wav' % source_key
        w = wave.open(os.path.join(source_wav_dir, source_wav), 'rb')
        params = w.getparams()
        frame_count += params[3]
        data.append([params, w.readframes(w.getnframes())])
        w.close()
    output = wave.open(path, 'wb')
    output_params = list(data[0][0])
    output_params[3] = frame_count
    output.setparams(output_params)
    for dgroup in data:
        output.writeframes(dgroup[1])
    output.close()

if __name__ == '__main__':
    # print dtmf_seq_in_wav('../callgui/wav/1002_1003_1001.wav','1002#,1003#,1001#',True)
    print dtmf_seq_in_wav('../sanity/wav/rec_1002.wav','1003#',True)
    print dtmf_seq_in_wav('../sanity/wav/rec_1003.wav','1002#',True)

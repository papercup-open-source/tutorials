"""This script takes one clipped file and declips it. It was created for
the declipping blog post."""
from scipy.io.wavfile import read, write
import numpy as np
import matplotlib.pyplot as plt
import argparse
from scipy.interpolate import interp1d

def get_segments(np_array):
    nmax = max(np_array)
    nmin = min(np_array)

    clipped_segments = []
    inside_clip = False
    clip_start = 0
    clip_end = 0

    for i, sample in enumerate(np_array):
        if (sample <= nmin + 1) or (sample >= nmax - 1):  # sample equal to or extremely close to max or min
            if not inside_clip:
                inside_clip = True  # declare we are inside clipped segment
                clip_start = i  # this is the first clipped sample

        elif inside_clip:
            inside_clip = False  # not longer inside clipped segment
            clip_end = i-1  # previous sample is end of segment
            clipped_segment = (clip_start, clip_end)  # save segment as tuple
            clipped_segments.append(clipped_segment)  # store tuple in list of clipped segments

    return clipped_segments

def declip_segments(clipped_segments, np_array):
    new_array = np_array.copy()  # make copy of original np_array
    for segment in clipped_segments:
        start = segment[0]
        end = segment[1]

        # get surrounding true values
        x_true = list(range(start - 5, start)) + list(range(end + 1, end + 6))
        y_true = [np_array[i] for i in x_true]

        # interpolate
        interpolation_function = interp1d(x_true, y_true, kind='cubic')
        x_axis = list(range(start - 5, end + 6))
        y_axis_new = [ float(int(i)) for i in interpolation_function(x_axis)]

        # plot segments
        y_axis_old = [np_array[i] for i in x_axis]
        plt.plot(x_axis, y_axis_old,'bo-')
        plt.plot(x_axis, y_axis_new,'r--')
        plt.show()

        # update new array with new values
        for i, x in enumerate(x_axis):
            if start <= x <= end:
                new_array[x] = y_axis_new[i]

    return new_array


def plot_special_segment(np_array):
    x_axis = list(range(int(2.920125*48000), int(2.926043*48000)))
    y_axis = [np_array[i] for i in x_axis]
    x_labels = [x/48000 for x in x_axis]
    plt.plot(x_labels, y_axis, 'b-')
    plt.xlabel("time (seconds)")
    plt.show()


def save_bad_file(sample_rate, new_array):
    write("bad_file.wav", sample_rate, new_array)


def save_file(sample_rate, new_array, new_path):
    new_max = max(abs(new_array))
    new_array = np.divide(new_array, new_max)
    new_array = np.multiply(new_array, 32768.0)
    new_array = new_array.astype('int16')

    # plot the special segment from the tutorial wav file
    plot_special_segment(new_array)

    # save the wav
    write(new_path, sample_rate, new_array)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--wav_path', required=True, help='Path of the wav file to be declipped')
    parser.add_argument('--new_path', required=True, help='Path to save the new declipped wav file')
    args = parser.parse_args()

    sample_rate, file_info = read(args.wav_path)
    np_array = np.array(file_info, dtype=float)  # load int16 wav file

    # plot the special segment from the tutorial wav file
    plot_special_segment(np_array)

    # identify bad segments
    segments = get_segments(np_array)

    # declip the segments
    new_array = declip_segments(segments, np_array)

    # plot the special segment from the tutorial wav file
    plot_special_segment(new_array)

    # save bad array from tutorial to demonstrate that we need to rescale
    save_bad_file(sample_rate, new_array)

    # save new wav file
    save_file(sample_rate, new_array, args.new_path)

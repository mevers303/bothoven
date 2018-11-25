import argparse
import music21 as m21
import os

from bothoven_globals import progress_bar
from functions.file_functions import get_filenames
from functions.pickle_workaround import pickle_dump


def get_args():

    parser = argparse.ArgumentParser(
        description="Converts a directory (and subdirectories) of MIDI files to music21 object pickles.")
    parser.add_argument("in_path", help="The directory of MIDI files to be read.")
    parser.add_argument("out_path", help="Where to save the pickled music21 objects.")
    args = parser.parse_args()

    in_dir = args.in_path
    out_dir = args.out_path

    return in_dir, out_dir


def cache(in_dir, out_dir):

    files = get_filenames(in_dir, [".mid", ".midi", ".smf"])
    done = 0

    for file in files:

        progress_bar(done, len(files), file)
        done += 1

        try:
            score = m21.converter.parse(file)
        except Exception as e:
            continue

        relative_path = file[len(in_dir):]
        if relative_path[0] == "/":
            relative_path = relative_path[1:]
        new_file = os.path.join(out_dir, relative_path) + ".pkl"
        new_dir = os.path.dirname(new_file)
        os.makedirs(new_dir, exist_ok=True)
        pickle_dump(score, new_file, verbose=False)

    progress_bar(done, len(files), "Done!")


def main():

    in_dir, out_dir = get_args()

    print("Caching library...")
    cache(in_dir, out_dir)


if __name__ == "__main__":
    main()

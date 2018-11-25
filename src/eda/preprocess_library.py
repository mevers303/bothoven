import argparse
import music21 as m21
import os
import pandas as pd

from bothoven_globals import progress_bar
from functions.file_functions import get_filenames


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
    csv_path = os.path.join(out_dir, "key_signatures.csv")
    if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
        df = pd.read_csv(csv_path, index_col="path")
        needs_column_header = False
    else:
        df = pd.DataFrame(columns=["tonic", "mode"])
        df.index.name = "path"
        needs_column_header = True
    csv_f = open(csv_path, "a")
    if needs_column_header:
        csv_f.write("path,tonic,mode\n")

    for file in files:

        progress_bar(done, len(files), "Loading:".ljust(12) + file + "...")
        done += 1

        relative_path = file[len(in_dir):]
        if relative_path[0] == "/":
            relative_path = relative_path[1:]
        new_file = os.path.join(out_dir, relative_path) + ".pkl"
        if new_file in df.index.values:
            continue
        new_dir = os.path.dirname(new_file)
        os.makedirs(new_dir, exist_ok=True)

        try:
            score = m21.converter.parse(file)
        except Exception as e:
            continue
        progress_bar(done - 1, len(files), "Analyzing:".ljust(12) + file + "...")
        key = score.analyze('key')
        csv_f.write(",".join([f'"{new_file}"', key.tonic.name, key.mode]) + "\n")
        csv_f.flush()

        m21.converter.freeze(score, fp=new_file)

    csv_f.close()
    progress_bar(done, len(files), "Done!")


def main():

    in_dir, out_dir = get_args()

    print("Caching library...")
    cache(in_dir, out_dir)


if __name__ == "__main__":
    main()

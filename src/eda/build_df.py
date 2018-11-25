import argparse
import music21 as m21
import os
import pandas as pd

from bothoven_globals import progress_bar
from functions.file_functions import get_filenames
from functions.pickle_workaround import pickle_load


def build_csv(cache_dir):

    files = get_filenames(cache_dir, [".pkl"])
    done = 0
    csv_path = os.path.join(cache_dir, "key_signatures.csv")
    if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
        df = pd.read_csv(csv_path, index_col="path")
    else:
        df = pd.DataFrame(columns=["tonic", "mode"])
        df.index.name = "path"
    csv_f = open(csv_path, "a")

    for file in files:

        progress_bar(done, len(files), file)
        done += 1

        if file in df.index:
            continue

        score = pickle_load(file, verbose=False)
        key = score.analyze('key')
        df.loc[file] = [key.tonic.name, key.mode]
        s = ",".join([f'"{file}"', key.tonic.name, key.mode]) + "\n"
        csv_f.write(s)
        csv_f.flush()

    csv_f.close()
    progress_bar(done, len(files), "Done!")

    return df


def get_args():

    parser = argparse.ArgumentParser(description="Creates a .csv in <path>/key_signatures.csv containing the key signature of each song.")
    parser.add_argument("path", help="The directory of music21 pickles to analyze.")
    args = parser.parse_args()

    cache_dir = args.path

    return cache_dir


def main():

    cache_dir = get_args()
    print(f"Building key signature datafram for {cache_dir}...")
    build_csv(cache_dir)


if __name__ == "__main__":
    main()

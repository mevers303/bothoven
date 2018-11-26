import numpy as np
import pandas as pd
import scipy.sparse as sps
from midi_handlers.Music21ArrayBuilder import Music21ArrayBuilder
from functions.pickle_workaround import pickle_dump

from midi_handlers.MusicLibrary import MusicLibrary, MusicLibraryFlat, MusicLibrarySplit
from midi_handlers.Music21Library import Music21LibrarySplit
import functions.s3 as s3


def main():

    lib_name = "Cmaj_small"
    df = pd.read_csv("/media/mark/Data/midi/midiclassics_m21/key_signatures.csv", index_col="path")
    np.random.seed(1111)
    corpus = np.random.choice(df.index.values[(df["tonic"] == "C") & (df["mode"] == "major")], size=120, replace=False)
    lib = Music21LibrarySplit(filenames=corpus)

    print("Pickling...")
    path = f"midi/pickles/{lib_name}_cont_offset.pkl"
    pickle_dump(lib, path)
    s3.upload_file(path)
    print("Done!")


if __name__ == "__main__":
    main()

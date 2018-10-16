import keras
import numpy as np
import pickle

from midi_handlers.MusicLibrary import MusicLibraryFlat


lib_name = "metallica_m21"

model = keras.models.load_model("/media/mark/Data/Documents/python/bothoven/models/metallica_666555444333222111/epoch_04-0.04.hdf5")
print("Loading dataset...")
with open(f"midi/pickles/{lib_name}.pkl", "rb") as f:
    dataset = pickle.load(f)


for x, y in dataset.step_through():
    p = model.predict(np.array([x]))[0]
    print(p)

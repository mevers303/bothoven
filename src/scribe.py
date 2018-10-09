import keras
import numpy as np
import pickle

from midi_handlers.MidiLibrary import MidiLibraryFlat


lib_name = "metallica"

model = keras.models.load_model("/media/mark/Data/Documents/python/bothoven/models/metallica_666555444333222111/epoch_20-2.74.hdf5")
print("Loading dataset...")
with open(f"midi/pickles/{lib_name}.pkl", "rb") as f:
    dataset = pickle.load(f)


for x, y in dataset.step_through():
    print(model.predict(np.array([x])))

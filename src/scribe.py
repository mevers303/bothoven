import keras
import numpy as np
import pickle

from midi_handlers.MidiLibrary import MidiLibraryFlat


lib_name = "metallica"

model = keras.models.load_model("/media/mark/Data/Documents/python/bothoven/models/metallica_666444/epoch_20-8.93.hdf5")
print("Loading dataset...")
with open(f"midi/pickles/{lib_name}.pkl", "rb") as f:
    dataset = pickle.load(f)


for x, y in dataset.step_through():
    p = model.predict(np.array([x]))
    x_note = np.argmax(x[-1,:-1])
    x_delay = x[-1,-1]
    note = np.argmax(p[0][0])
    time = p[1][0]
    print(p)

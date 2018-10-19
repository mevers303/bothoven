import keras
import numpy as np
from functions.pickle_workaround import pickle_load

from midi_handlers.MidiLibrary import MidiLibraryFlat


lib_name = "blink182_midi"

model = keras.models.load_model("/media/mark/Data/Documents/python/bothoven/models/blink182_midi_654321/epoch_019_0.0141.hdf5")
print("Model:", model.name)
print("Loading dataset...")
dataset = pickle_load(f"midi/pickles/{lib_name}.pkl")


for x, y in dataset.step_through():
    p = model.predict(np.array([x]))[0]
    notes = p[:258]
    note = np.argmax(notes)
    top_notes = np.argsort(notes)[::-1][:10]
    delays = p[258:]
    delay = dataset.one_hot_to_delay[np.argmax(delays)]
    top_delays = [dataset.one_hot_to_delay[x] for x in np.argsort(notes)[::-1][:10]]

    print(f"note_on: {note}" if note < 128 else f"note_off: {note - 128}", "delay:", delay)
    print("Top notes", top_notes)
    print("Top delays:", top_delays)
    print()

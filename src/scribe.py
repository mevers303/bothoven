import keras
import numpy as np
from functions.pickle_workaround import pickle_load

from midi_handlers.SplitOutputMidiLibrary  import SplitOutputMidiLibraryFlat


lib_name = "bach_short_midi_split_output"

model = keras.models.load_model("/media/mark/Data/Documents/python/bothoven/models/bach_short_midi_split_output_4_layer_6543/epoch_100_0.4403.hdf5")
print("Model:", model.name)
print("Loading dataset...")
dataset = pickle_load(f"midi/pickles/{lib_name}.pkl")


new_song = np.zeros((64, dataset.buf.shape[1]))
new_song[-1, -2] = 1


for i in range(100):
    x = np.array([new_song[i:dataset.NUM_STEPS + i]])
    p = model.predict(x)
    notes = p[0][0]
    note = np.argmax(notes)
    top_notes = np.argsort(notes)[::-1][:10]
    delays = p[1][0]
    delay_i = np.argmax(delays)
    delay = dataset.one_hot_to_delay[delay_i]
    top_delays = [dataset.one_hot_to_delay[x] for x in np.argsort(delays)[::-1][:10]]

    print(f"note_on:  {note}" if note < 128 else f"note_off: {note - 128}", "delay:", delay)
    # print("Top notes", top_notes)
    # print("Top delays:", top_delays)
    # print()

    new_step = np.zeros(dataset.buf.shape[1])
    new_step[note] = 1
    new_step[delay_i + 258] = 1
    new_song = np.vstack([new_song, new_step])

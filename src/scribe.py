import keras
import numpy as np
import mido
from functions.pickle_workaround import pickle_load

from midi_handlers.SplitOutputMidiLibrary  import SplitOutputMidiLibraryFlat


lib_name = "bach_short_midi_split_output"

model = keras.models.load_model("/media/mark/Data/Documents/python/bothoven/models/bach_short_midi_split_output_4_layer_6543/epoch_100_0.4403.hdf5")
print("Model:", model.name)
print("Loading dataset...")
dataset = pickle_load(f"midi/pickles/{lib_name}.pkl")



def pad_track(track):

    track_start = np.zeros(dataset.buf.shape[1])
    track_start[256] = 1
    msg_list = [track_start]

    for msg in track:

        if not (msg.type == 'note_on' or msg.type == 'note_off') or msg.channel == 9:  # skip drum tracks
            continue

        # find the one-hot note
        note_code = msg.note
        if msg.type == "note_off" or not msg.velocity:
            note_code += 128

        delay_code = dataset.delay_to_one_hot[msg.time] + 258

        this_step = np.zeros(dataset.buf.shape[1])
        this_step[note_code] = 1
        this_step[delay_code] = 1
        msg_list.append(this_step)

    if len(msg_list) == 1:
        return None

    track_end = np.zeros(dataset.buf.shape[1])
    track_end[257] = 1
    msg_list.append(track_end)

    if len(msg_list) < dataset.NUM_STEPS:
        difference = dataset.NUM_STEPS - len(msg_list)
        pad = [np.zeros(dataset.buf.shape[1]) for _ in range(difference)]
        msg_list = pad + msg_list

    return np.array(msg_list)


seed = mido.MidiFile("/home/mark/test_out/test.mid")
track_i = 0

for seed_track in seed.tracks:

    new_song = pad_track(seed_track)
    if new_song is None:
        track_i += 1
        continue

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

        # print(f"note_on:  {note}" if note < 128 else f"note_off: {note - 128}", "delay:", delay)
        # print("Top notes", top_notes)
        # print("Top delays:", top_delays)
        # print()

        new_step = np.zeros(dataset.buf.shape[1])
        new_step[note] = 1
        new_step[delay_i + 258] = 1
        new_song = np.vstack([new_song, new_step])

        if note < 128:
            seed_track.append(mido.Message("note_on", note=note, time=delay, channel=0))
        elif note < 256:
            seed_track.append(mido.Message("note_off", note=note - 128, time=delay, channel=0))

    # new_mid = mido.MidiFile(ticks_per_beat=192)
    # new_mid.tracks.append(seed_track)
    # new_mid.save(f"output/output_{track_i}.mid")
    # print(f"Saved output/output_{track_i}.mid")

    seed.tracks[track_i] = seed_track
    print("Completed track", track_i)
    track_i += 1

seed.save(f"output/the_track.mid")
print(f"Saved output/the_track.mid")

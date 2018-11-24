import keras
import numpy as np
import music21

from bothoven_globals import NUM_STEPS, progress_bar
from functions.pickle_workaround import pickle_load
from midi_handlers.Music21ArrayBuilder import Music21ArrayBuilder
from midi_handlers.Music21Library import Music21LibraryFlat, Music21LibrarySplit


lib_name = "chopin_2hand_m21"
model_json = "models-old/chopin_2hand_m21_666555444_drop0.333_lr6.66e-05_decay0_batch64/chopin_2hand_m21_666555444_drop0.333_lr6.66e-05_decay0_batch64.json"
model_h5 = "models-old/chopin_2hand_m21_666555444_drop0.333_lr6.66e-05_decay0_batch64/epoch_020_4.2121.h5"
seed_file = "/home/mark/Documents/python/bothoven/midi/chopin_2hand/Sonata op35 n3 .mid"
num_predictions = 200
start_i = 1000


def song_buf_to_onehot(integer_encoded_song, dataset):

    onehot_encoded_song = np.zeros((integer_encoded_song.shape[0], dataset.num_features), dtype=np.byte)

    for i in range(integer_encoded_song.shape[0]):
        note, duration, offset = integer_encoded_song[i]
        onehot_encoded_song[i, dataset.note_to_one_hot[note]] = 1
        onehot_encoded_song[i, dataset.duration_to_one_hot[duration] + len(dataset.note_to_one_hot)] = 1
        onehot_encoded_song[i, dataset.offset_to_one_hot[offset] + len(dataset.note_to_one_hot) + len(dataset.duration_to_one_hot)] = 1

    return onehot_encoded_song


def sample(a, temperature=1.0):
    # helper function to sample an index from a probability array
    a = np.log(a) / temperature
    dist = np.exp(a) / np.sum(np.exp(a))
    choices = range(len(a))
    return np.random.choice(choices, p=dist)



print("Loading dataset...")
dataset = pickle_load(f"midi/pickles/{lib_name}.pkl")
print(" -> Loading seed song...")
seed = song_buf_to_onehot(Music21ArrayBuilder(seed_file).mid_to_array(), dataset)
new_song = np.vstack([seed[start_i:start_i  + NUM_STEPS], np.zeros((num_predictions, dataset.num_features))])
score = music21.stream.Score()
part = music21.stream.Part()
part.id = 'part1'

print("Loading model...")
print(" -> Loading structure...")
with open(model_json, "r") as f:
    model = keras.models.model_from_json(f.read())
print(" -> Loading weights...")
model.load_weights(model_h5)


current_list = part
notes_in_chord = 0


for i in range(num_predictions):

    p = model.predict(np.array([seed[i + start_i:i + start_i + NUM_STEPS]]))
    p_note = sample(p[0][0], temperature=2)
    p_duration = sample(p[1][0], temperature=1.2)
    p_offset = np.argmax(p[2][0])

    new_song[i + NUM_STEPS, p_note] = 1
    new_song[i + NUM_STEPS, p_duration + p[0].shape[1]] = 1
    new_song[i + NUM_STEPS, p_offset + p[0].shape[1] + p[1].shape[1]] = 1

    note = dataset.one_hot_to_note[p_note]
    duration = dataset.one_hot_to_duration[p_duration]
    offset = dataset.one_hot_to_offset[p_offset]

    if offset != -1 and offset != -2:
        if note == -3 or duration == -3 or offset == -3:
            if notes_in_chord:
                part.append(music21.chord.Chord(current_list))
                notes_in_chord = 0
            current_list = []
        elif note == -4 or duration == -4 or offset == -4:
            if notes_in_chord:
                part.append(music21.chord.Chord(current_list))
                notes_in_chord = 0
            current_list = part
        elif note >= 0:
            if notes_in_chord >= 4:
                part.append(music21.chord.Chord(current_list))
                notes_in_chord = 0
                current_list = part
            current_list.append(music21.note.Note(note, quarterLength=duration))
            if not current_list is part:
                notes_in_chord += 1

    progress_bar(i, num_predictions)


score.insert(0, part)
score.write('midi', fp='output/out.mid')

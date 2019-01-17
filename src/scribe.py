import tensorflow.keras as keras
import numpy as np
import music21
import os

from bothoven_globals import NUM_STEPS, progress_bar
from functions.pickle_workaround import pickle_load
from midi_handlers.Music21ArrayBuilder import Music21ArrayBuilder
from midi_handlers.Music21Library import Music21LibraryFlat, Music21LibrarySplit
from functions.s3 import download_file, down_sync_s3, upload_file


lib_name = "format0_maj_m21"
model_json = "models/format0_maj_m21_888-666-444_drop0.333_lr6.66e-05_decay0_batch64/format0_maj_m21_888-666-444_drop0.333_lr6.66e-05_decay0_batch64.json"
download_file(model_json)
model_h5 = "models/format0_maj_m21_888-666-444_drop0.333_lr6.66e-05_decay0_batch64/epoch_010_4.3823.h5"
download_file(model_h5)
num_predictions = 420
start_i = 420
seed_files = ['chpn_op25_e1_format0.mid',
                 'mz_333_2_format0.mid',
                 'mz_331_3_format0.mid',
                 'beethoven_les_adieux_1_format0.mid',
                 'chpn-p13_format0.mid',
                 'alb_se7_format0.mid',
                 'grieg_zwerge_format0.mid',
                 'schubert_D935_2_format0.mid',
                 'alb_esp2_format0.mid',
                 'mz_545_1_format0.mid',
                 'scn15_9_format0.mid',
                 'chpn-p17_format0.mid',
                 'alb_se3_format0.mid',
                 'gra_esp_4_format0.mid',
                 'waldstein_3_format0.mid',
                 'beethoven_hammerklavier_4_format0.mid',
                 'chpn_op33_2_format0.mid',
                 'mond_2_format0.mid',
                 'deb_clai_format0.mid',
                 'mz_570_1_format0.mid',
                 'burg_perlen_format0.mid',
                 'chpn_op7_1_format0.mid',
                 'schum_abegg_format0.mid',
                 'scn15_7_format0.mid',
                 'chpn_op33_4_format0.mid',
                 'hay_40_2_format0.mid']



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


print("Loading model...")
print(" -> Loading structure...")
with open(model_json, "r") as f:
    model = keras.models.model_from_json(f.read())
print(" -> Loading weights...")
model.load_weights(model_h5)

print("Loading dataset...")
download_file(f"midi/pickles/{lib_name}.pkl")
down_sync_s3("midi/format0_maj")
dataset = pickle_load(f"midi/pickles/{lib_name}.pkl")


def doit(seed_file):

    print(" -> Loading seed song...")
    seed = song_buf_to_onehot(Music21ArrayBuilder("midi/format0_maj/" + seed_file).mid_to_array(), dataset)

    note_temp = .1
    while note_temp <= 1.5:
        duration_temp = .1
        while duration_temp <= 1.5:

            output_file = f"output/{seed_file[:-12]}/note_temp-{float(round(note_temp, 1))}__duration_temp-{float(round(duration_temp, 1))}.mid"
            print(f"Saving '{output_file}'...")

            new_song = np.vstack([seed[start_i:start_i  + NUM_STEPS], np.zeros((num_predictions, dataset.num_features))])
            score = music21.stream.Score()
            part = music21.stream.Part()
            part.id = 'part1'

            current_list = part
            notes_in_chord = 0

            for i in range(num_predictions):

                p = model.predict(np.array([seed[i + start_i:i + start_i + NUM_STEPS]]))
                p_note = sample(p[0][0], temperature=note_temp)
                p_duration = sample(p[1][0], temperature=duration_temp)
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
                    elif note >= 0 and duration >= 0:
                        if notes_in_chord >= 4:
                            part.append(music21.chord.Chord(current_list))
                            notes_in_chord = 0
                            current_list = part
                        current_list.append(music21.note.Note(note, quarterLength=duration))
                        if not current_list is part:
                            notes_in_chord += 1

                progress_bar(i + 1, num_predictions, output_file, clear_when_done=True)

            score.insert(0, part)
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            score.write('midi', fp=output_file)
            upload_file(output_file)

            duration_temp += 0.1

        note_temp += 0.1


for file in seed_files:
    doit(file)

# Mark Evers
# Created: 3/30/2018
# _model_scratchpad.py
# RNN classifier _model

import keras
import numpy as np
import os
import pickle

# import sys
# sys.path.append("src")

from midi_handlers.MidiLibrary import MidiLibraryFlat
from wwts_globals import NUM_STEPS, NUM_FEATURES, N_EPOCHS, BATCH_SIZE


# fix random seed for reproducibility
np.random.seed(777)





def create_model(name):

    # # CREATE THE _model
    # _model = keras.models.Sequential()
    # _model.add(keras.layers.LSTM(units=666, input_shape=(NUM_STEPS, NUM_FEATURES), return_sequences=True))
    # _model.add(keras.layers.Dropout(.555))
    # _model.add(keras.layers.LSTM(units=444, return_sequences=True))
    # _model.add(keras.layers.Dropout(.333))
    # _model.add(keras.layers.LSTM(222))
    # _model.add(keras.layers.Dropout(.111))
    # _model.add(keras.layers.Dense(units=NUM_FEATURES))
    # _model.compile(loss='mae', optimizer='adam')
    # print(_model.summary())

    # CREATE THE _model
    inputs = keras.layers.Input(shape=(NUM_STEPS, NUM_FEATURES))
    x = keras.layers.LSTM(units=666)(inputs)
    x = keras.layers.Dropout(.444)(x)

    note_branch = keras.layers.Dense(units=(NUM_FEATURES - 1), activation="softmax", name="note_branch")(x)
    time_branch = keras.layers.Dense(units=1, activation="relu", name="time_branch")(x)

    _model = keras.models.Model(inputs=inputs, outputs=[note_branch, time_branch], name=name)
    _model.compile(loss={"note_branch": "categorical_crossentropy", "time_branch": "mse"}, loss_weights={"note_branch": 0.05, "time_branch":1e4}, optimizer="adam")

    print(_model.summary())

    save_model_structure(_model)

    return _model



def load_model_structure(name):

    structure_filename = os.path.join("models/", name, "model.json")
    # weights_filename = os.path.join("models/", name, "epoch_" + epoch + ".h5")


    # load json and create _model
    with open(structure_filename, 'r') as f:
        json_str = f.read()
    _model = keras.models.model_from_json(json_str)
    # load weights into new _model
    # _model.load_weights(weights_filename)
    print("Loaded model from disk")

    return _model


def save_model_structure(_model):

    filename = os.path.join("models/", _model.name, "model.json")

    print("Saving model to disk...")
    # serialize _model to JSON
    _model_json = _model.to_json()
    with open(filename, "w") as json_file:
        json_file.write(_model_json)


def fit_model(_model, _dataset):

    logfile = os.path.join("models/", _model.name, "log.txt")

    steps_per_epoch = (_dataset.buf.shape[0] - 1) // BATCH_SIZE # it's - 1 because the very last step is a prediction only
    model_save_filepath = os.path.join("models/", _model.name, "epoch_{epoch:02d}-{loss:.2f}.hdf5")
    callbacks = [keras.callbacks.ModelCheckpoint(model_save_filepath, monitor='loss')]

    history = _model.fit_generator(_dataset.next_batch(), steps_per_epoch=steps_per_epoch, epochs=N_EPOCHS, callbacks=callbacks)

    with open(logfile, "a") as f:
        f.write(str(history))
        f.write("\n\n")
    print("")  # newline


    return _model




def main():

    lib_name = "metallica"
    model_name = "metallica_666444"

    if not os.path.exists(f"models/{model_name}"):
        os.mkdir(f"models/{model_name}")

    print("Creating model...")
    model = create_model(model_name)

    print("Loading dataset...")
    # dataset = MidiLibrarySplit(lib_path)
    with open(f"midi/pickles/{lib_name}.pkl", "rb") as f:
        dataset = pickle.load(f)

    print("Fitting model...")
    fit_model(model, dataset)


if __name__ == "__main__":

    main()

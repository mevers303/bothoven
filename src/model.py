# Mark Evers
# Created: 3/30/2018
# _model_scratchpad.py
# RNN classifier _model

import keras
import numpy as np
import os

from midi_handlers.MidiLibrary import MidiLibraryFlat
from midi_handlers.Music21Library import Music21LibraryFlat
from bothoven_globals import N_EPOCHS
from functions.pickle_workaround import pickle_load


# fix random seed for reproducibility
np.random.seed(777)


lib_name = "beatles_midi"
model_name = lib_name + "_654321"


def two_loss(y_true, y_pred):

    a = keras.backend.categorical_crossentropy(y_true[:, :258], y_pred[:, :258])
    b = keras.backend.categorical_crossentropy(y_true[:, 258:], y_pred[:, 258:])

    return a + b

def two_accuracy(y_true, y_pred):

    return keras.backend.mean(keras.metrics.categorical_accuracy(y_true[:, 258], y_pred[:, :258]) + keras.metrics.categorical_accuracy(y_true[:, 258:], y_pred[:, 258:]))


def create_model(name, dataset):

    # CREATE THE _model
    _model = keras.models.Sequential(name=name)
    _model.add(keras.layers.LSTM(units=666, input_shape=(dataset.NUM_STEPS, dataset.buf.shape[1]), return_sequences=True))
    _model.add(keras.layers.Dropout(.555))
    _model.add(keras.layers.LSTM(units=444, input_shape=(dataset.NUM_STEPS, dataset.buf.shape[1]), return_sequences=True))
    _model.add(keras.layers.Dropout(.333))
    _model.add(keras.layers.LSTM(units=222))
    _model.add(keras.layers.Dropout(.111))
    _model.add(keras.layers.Dense(units=dataset.buf.shape[1], activation='sigmoid'))
    sgd = keras.optimizers.RMSprop(lr=1e-4, rho=0.9, epsilon=None, decay=0.0)
    _model.compile(loss=two_loss, optimizer=sgd, metrics=[two_accuracy])
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
    with open(filename, "w") as json_file:
        json_file.write(_model.to_json())


def fit_model(_model, dataset):

    logfile = os.path.join("models/", _model.name, "log.txt")

    steps_per_epoch = (dataset.buf.shape[0] - 1) // dataset.BATCH_SIZE # it's - 1 because the very last step is a prediction only
    model_save_filepath = os.path.join("models/", model_name, "epoch_{epoch:03d}_{loss:.4f}.hdf5")
    callbacks = [keras.callbacks.ModelCheckpoint(model_save_filepath, monitor='loss')]

    history = _model.fit_generator(dataset.next_batch(), steps_per_epoch=steps_per_epoch, epochs=N_EPOCHS, callbacks=callbacks)

    with open(logfile, "a") as f:
        f.write(str(history))
        f.write("\n\n")
    print("")  # newline


    return _model




def main():

    if not os.path.exists(f"models/{model_name}"):
        os.makedirs(f"models/{model_name}")

    print("Loading dataset...")
    # dataset = MidiLibrarySplit(lib_path)
    dataset = pickle_load(f"midi/pickles/{lib_name}.pkl")

    print("Creating model...")
    model = create_model(model_name, dataset)
    # print("Loading model from disk...")
    # model = keras.models.load_model("models/blink182_midi_654321/epoch_019_0.0141.hdf5")

    print("Fitting model...")
    fit_model(model, dataset)


if __name__ == "__main__":

    main()

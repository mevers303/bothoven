# Mark Evers
# Created: 3/30/2018
# _model_scratchpad.py
# RNN classifier _model

import keras
# from keras.models import Sequential, model_from_json
# from keras.layers import LSTM, Dense, Dropout
# from keras.wrappers.scikit_learn import KerasClassifier
# from keras.callbacks import Callback
# from keras.utils import plot_model
# from sklearn.model_selection import cross_val_score
# from sklearn.metrics import precision_recall_fscore_support
# from sklearn.model_selection import KFold
# import pickle
import numpy as np
import os
import pickle

from midi_handlers.MidiLibrary import MidiLibrarySplit
from wwts_globals import NUM_STEPS, NUM_FEATURES, N_EPOCHS, BATCH_SIZE


# fix random seed for reproducibility
np.random.seed(777)





def create_model(name):

    # CREATE THE _model
    _model = keras.models.Sequential()
    _model.add(keras.layers.LSTM(units=666, input_shape=(NUM_STEPS, NUM_FEATURES), return_sequences=True))
    _model.add(keras.layers.Dropout(.555))
    _model.add(keras.layers.LSTM(units=444, return_sequences=True))
    _model.add(keras.layers.Dropout(.333))
    _model.add(keras.layers.LSTM(222))
    _model.add(keras.layers.Dropout(.111))
    _model.add(keras.layers.Dense(units=NUM_FEATURES))
    _model.compile(loss='mae', optimizer='adam')
    print(_model.summary())

    save_model_structure(_model, name)

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


def save_model_structure(_model, name):

    filename = os.path.join("models/", name, "model.json")

    print("Saving model to disk")
    # serialize _model to JSON
    _model_json = _model.to_json()
    with open(filename, "w") as json_file:
        json_file.write(_model_json)


def fit_model(_model, _dataset, name):

    logfile = "models/final.txt"

    # FIT THE _model
    print("Training model...")
    with open(logfile, "a") as f:
        f.write("***Model***\n")
        f.write("Neurons: 666 -> 444 -> 222\n")
        f.write("Dropout: .555 -> .333 -> .111\n")

    train_steps_per_epoch = (_dataset.train_lib.buf.shape[0] - 1) / BATCH_SIZE # it's - 1 because the very last step is a prediction only
    test_steps_per_epoch = (_dataset.test_lib.buf.shape[0] - 1) / BATCH_SIZE
    model_save_filepath = os.path.join("src/models/", name, "epoch_{epoch:02d}-{val_loss:.2f}.hdf5")
    callbacks = [keras.callbacks.ModelCheckpoint(model_save_filepath, monitor='val_loss', verbose=0)]

    history = _model.fit_generator(_dataset.train_lib.step_through(), steps_per_epoch=train_steps_per_epoch, epochs=N_EPOCHS, callbacks=callbacks, validation_data=_dataset.test_lib.step_through(), validation_steps=test_steps_per_epoch)

    with open(logfile, "a") as f:
        f.write(str(history))
        f.write("\n\n")
    print("")  # newline


    return _model




def main():

    model_name = "bach666555444333222111"
    lib_path = "midi/bach_cleaned"
    pickle_path = "midi/pickles/bach.pkl"

    # dataset = MidiLibrarySplit(lib_path)
    with open(pickle_path, "rb") as f:
        dataset = pickle.load(f)
    model = create_model(model_name)
    fit_model(model, dataset, model_name)


if __name__ == "__main__":

    main()

# Mark Evers
# Created: 3/30/2018
# _model_scratchpad.py
# RNN classifier _model

import numpy as np
from keras.models import Sequential, model_from_json
from keras.layers import LSTM, Dense, Dropout
from keras.wrappers.scikit_learn import KerasClassifier
from keras.callbacks import Callback
from keras.utils import plot_model
from sklearn.model_selection import cross_val_score
from sklearn.metrics import precision_recall_fscore_support
from sklearn.model_selection import KFold
import pickle
import os

import wwts_globals

# fix random seed for reproducibility
np.random.seed(777)





def create_model(name):

    # CREATE THE _model
    _model = Sequential()
    _model.add(LSTM(units=666, input_shape=(wwts_globals.NUM_STEPS, wwts_globals.NUM_FEATURES), return_sequences=True))
    _model.add(Dropout(.555))
    _model.add(LSTM(units=444, return_sequences=True))
    _model.add(Dropout(.333))
    _model.add(LSTM(222))
    _model.add(Dropout(.111))
    _model.add(Dense(units=wwts_globals.NUM_FEATURES))
    _model.compile(loss='mae', optimizer='adam')
    print(_model.summary())

    save_model_structure(_model, name)

    return _model



def load_model_structure(name):

    structure_filename = os.path.join("src/models/", name, "model.json")
    # weights_filename = os.path.join("src/models/", name, "epoch_" + epoch + ".h5")


    # load json and create _model
    with open(structure_filename, 'r') as f:
        json_str = f.read()
    _model = model_from_json(json_str)
    # load weights into new _model
    # _model.load_weights(weights_filename)
    print("Loaded model from disk")

    return _model


def save_model_structure(_model, name):

    filename = os.path.join("src/models/", name, "model.json")

    print("Saving model to disk")
    # serialize _model to JSON
    _model_json = _model.to_json()
    with open(filename, "w") as json_file:
        json_file.write(_model_json)


def fit_model(_dataset, _model):

    logfile = "models/final.txt"
    X_train, X_test, y_train, y_test = _dataset.get_all_split()

    # FIT THE _model
    print("Training model...")
    with open(logfile, "a") as f:
        f.write("***Model***\n")
        f.write("Neurons: 666 -> 444 -> 222\n")
        f.write("Dropout: .555 -> .333 -> .111\n")

    history = _model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=wwts_globals.N_EPOCHS, batch_size=wwts_globals.BATCH_SIZE)

    with open(logfile, "a") as f:
        f.write(str(history))
        f.write("\n\n")
    print("")  # newline


    return _model



if __name__ == "__main__":

    pass

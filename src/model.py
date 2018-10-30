# Mark Evers
# Created: 3/30/2018
# _model_scratchpad.py
# RNN classifier _model

import keras
import numpy as np
import os

from midi_handlers.Music21Library import Music21LibrarySplit, Music21LibraryFlat
from bothoven_globals import N_EPOCHS
from functions.pickle_workaround import pickle_load


# fix random seed for reproducibility
np.random.seed(777)


lib_name = "bach_short_m21"
model_name = lib_name + "_3_layer_666333"


note_one_hot_len = 0
duration_one_hot_len = 0
offset_one_hot_len = 0


def create_model(dataset):

    # # CREATE THE _model
    # _model = keras.models.Sequential(name=name)
    # _model.add(keras.layers.LSTM(units=666, input_shape=(dataset.NUM_STEPS, dataset.buf.shape[1]), return_sequences=True))
    # _model.add(keras.layers.Dropout(.555))
    # _model.add(keras.layers.LSTM(units=444, input_shape=(dataset.NUM_STEPS, dataset.buf.shape[1]), return_sequences=True))
    # _model.add(keras.layers.Dropout(.333))
    # _model.add(keras.layers.LSTM(units=222))
    # _model.add(keras.layers.Dropout(.111))
    # _model.add(keras.layers.Dense(units=dataset.buf.shape[1], activation='sigmoid'))
    # sgd = keras.optimizers.RMSprop(lr=1e-4, rho=0.9, epsilon=None, decay=0.0)
    # _model.compile(loss=two_loss, optimizer=sgd, metrics=[two_accuracy])
    # print(_model.summary())

    inputs = keras.layers.Input(shape=(dataset.NUM_STEPS, dataset.NUM_FEATURES))
    x = keras.layers.LSTM(units=666, input_shape=(dataset.NUM_STEPS, dataset.NUM_FEATURES), return_sequences=True)(inputs)
    x = keras.layers.Dropout(.333)(x)
    x = keras.layers.LSTM(units=666, input_shape=(dataset.NUM_STEPS, dataset.NUM_FEATURES), return_sequences=True)(x)
    x = keras.layers.Dropout(.333)(x)
    x = keras.layers.LSTM(units=666, input_shape=(dataset.NUM_STEPS, dataset.NUM_FEATURES))(x)
    x = keras.layers.Dropout(.333)(x)

    note_output = keras.layers.Dense(name="n", units=len(dataset.note_to_one_hot), activation='softmax')(x)
    duration_output = keras.layers.Dense(name="d", units=len(dataset.duration_to_one_hot), activation='softmax')(x)
    offset_output = keras.layers.Dense(name="o", units=len(dataset.offset_to_one_hot), activation='softmax')(x)

    _model = keras.models.Model(name=model_name, inputs=inputs, outputs=[note_output, duration_output, offset_output])
    optimizer = keras.optimizers.RMSprop(lr=6.66e-5, rho=0.9, epsilon=None, decay=0.0)
    losses = {"n": "categorical_crossentropy", "d": "categorical_crossentropy", "o": "categorical_crossentropy"}
    metrics = {"n": "categorical_accuracy", "d": "categorical_accuracy", "o": "categorical_accuracy"}
    _model.compile(optimizer=optimizer, loss=losses, metrics=metrics)

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

    steps_per_epoch = (dataset.train_lib.buf.shape[0] - 1) // dataset.BATCH_SIZE # it's - 1 because the very last step is a prediction only
    validation_steps_per_epoch = (dataset.test_lib.buf.shape[0] - 1) // dataset.BATCH_SIZE
    model_save_filepath = os.path.join("models/", model_name, "epoch_{epoch:03d}_{loss:.4f}.hdf5")
    callbacks = [keras.callbacks.ModelCheckpoint(model_save_filepath, monitor='loss')]

    history = _model.fit_generator(dataset.train_lib.next_batch(), steps_per_epoch=steps_per_epoch, epochs=N_EPOCHS, callbacks=callbacks, validation_data=dataset.test_lib.next_batch(), validation_steps=validation_steps_per_epoch)

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
    model = create_model(dataset)
    # print("Loading model from disk...")
    # model = keras.models.load_model("/media/mark/Data/Documents/python/bothoven/models/beatles_midi_split_output_654321/epoch_041_1.9419.hdf5")

    print("Fitting model...")
    fit_model(model, dataset)


if __name__ == "__main__":

    main()

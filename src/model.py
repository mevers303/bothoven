# Mark Evers
# Created: 3/30/2018
# model_scratchpad.py
# RNN classifier model

import keras
import numpy as np
import os
import shutil
import time

from midi_handlers.Music21Library import Music21LibrarySplit, Music21LibraryFlat
from bothoven_globals import N_EPOCHS
from functions.pickle_workaround import pickle_load


# fix random seed for reproducibility
np.random.seed(777)


units = 256
dropout = .333
lr = 6.66e-5
decay = 0

lib_name = "bach_short_m21"
model_name = lib_name + f"_5_layer_u{units}_dr{dropout}_lr{lr:.2e}_d{decay}"


note_one_hot_len = 0
duration_one_hot_len = 0
offset_one_hot_len = 0


def create_model(dataset):

    inputs = keras.layers.Input(shape=(dataset.NUM_STEPS, dataset.NUM_FEATURES))
    x = keras.layers.LSTM(units=units, return_sequences=True)(inputs)
    x = keras.layers.Dropout(dropout)(x)
    x = keras.layers.LSTM(units=units, return_sequences=True)(x)
    x = keras.layers.Dropout(dropout)(x)
    x = keras.layers.LSTM(units=units, return_sequences=True)(x)
    x = keras.layers.Dropout(dropout)(x)
    x = keras.layers.LSTM(units=units, return_sequences=True)(x)
    x = keras.layers.Dropout(dropout)(x)
    x = keras.layers.LSTM(units=units)(x)
    x = keras.layers.Dropout(dropout)(x)

    note_output = keras.layers.Dense(name="n", units=len(dataset.note_to_one_hot), activation='softmax')(x)
    duration_output = keras.layers.Dense(name="d", units=len(dataset.duration_to_one_hot), activation='softmax')(x)
    offset_output = keras.layers.Dense(name="o", units=len(dataset.offset_to_one_hot), activation='softmax')(x)

    model = keras.models.Model(name=model_name, inputs=inputs, outputs=[note_output, duration_output, offset_output])
    optimizer = keras.optimizers.RMSprop(lr=lr, rho=0.9, epsilon=None, decay=decay)
    losses = {"n": "categorical_crossentropy", "d": "categorical_crossentropy", "o": "categorical_crossentropy"}
    metrics = {"n": "categorical_accuracy", "d": "categorical_accuracy", "o": "categorical_accuracy"}
    model.compile(optimizer=optimizer, loss=losses, metrics=metrics)

    save_model_structure(model)
    # delete the old tensorboard log file
    if os.path.exists(f"tensorboard/{model.name}"):
        shutil.rmtree(f"tensorboard/{model.name}")

    return model


def load_model(name):

    best_epoch = 0
    best_file = ""

    # find all the previous models
    for file in os.listdir(os.path.join("models/", name)):

        if file.endswith(".hdf5"):

            epoch = int(file.split("_")[1])
            if epoch > best_epoch:
                best_epoch = epoch
                best_file = file

    if best_epoch:
        print(f"Loading model from disk (epoch {best_epoch})...")
        return keras.models.load_model(os.path.join("models/", name, best_file)), best_epoch
    else:
        return None, 0


def save_model_structure(model):

    filename = os.path.join("models/", model.name, "model.json")

    print("Saving model to disk...")
    # serialize model to JSON
    with open(filename, "w") as json_file:
        json_file.write(model.to_json())


def fit_model(model, dataset, start_epoch):

    logfile = os.path.join("models/", model.name, "log.txt")

    steps_per_epoch = (dataset.train_lib.buf.shape[0] - 1) // dataset.BATCH_SIZE # it's - 1 because the very last step is a prediction only
    validation_steps_per_epoch = (dataset.test_lib.buf.shape[0] - 1) // dataset.BATCH_SIZE
    model_save_filepath = os.path.join("models/", model_name, "epoch_{epoch:03d}_{val_loss:.4f}.hdf5")
    callbacks = [keras.callbacks.ModelCheckpoint(model_save_filepath, monitor='val_loss'), keras.callbacks.TensorBoard(log_dir=f"tensorboard/{model.name}")]

    history = model.fit_generator(dataset.train_lib.next_batch(), steps_per_epoch=steps_per_epoch, epochs=N_EPOCHS,
                                   callbacks=callbacks, validation_data=dataset.test_lib.next_batch(),
                                   validation_steps=validation_steps_per_epoch, initial_epoch=start_epoch)

    with open(logfile, "a") as f:
        f.write(str(history))
        f.write("\n\n")
    print("")  # newline


    return model




def main():

    if not os.path.exists(f"models/{model_name}"):
        os.makedirs(f"models/{model_name}")

    print("Loading dataset...")
    # dataset = MidiLibrarySplit(lib_path)
    dataset = pickle_load(f"midi/pickles/{lib_name}.pkl")

    model, start_epoch = load_model(model_name)
    if not model:
        print("Creating model...")
        model = create_model(dataset)

    print(model.summary())
    print("Fitting model...")
    fit_model(model, dataset, start_epoch)


if __name__ == "__main__":

    main()

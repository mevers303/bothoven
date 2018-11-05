# Mark Evers
# Created: 3/30/2018
# model_scratchpad.py
# RNN classifier model

import argparse
import keras
import numpy as np
import os
import shutil

from midi_handlers.Music21Library import Music21LibrarySplit, Music21LibraryFlat
from bothoven_globals import BATCH_SIZE, NUM_STEPS
from functions.pickle_workaround import pickle_load
import functions.s3 as s3

# fix random seed for reproducibility
np.random.seed(777)



class S3Callback(keras.callbacks.Callback):

    def __init__(self, model_name):
        super().__init__()
        self.model_name = model_name
    
    def on_epoch_end(self, epoch, logs=None):
        s3.upload_file(f"models/{self.model_name}/log.csv")
        s3.upload_latest_file(f"models/{self.model_name}")
        s3.upload_latest_file(f"tensorboard/{self.model_name}")

    def on_train_end(self, logs=None):
        s3.up_sync_s3(f"models/{self.model_name}")
        s3.up_sync_s3(f"tensorboard/{self.model_name}")



def create_model(dataset, model_name, layers, nodes, dropout, lr, decay):

    if layers < 1:
        raise ValueError("Number of layers must be greater than zero.")

    inputs = keras.layers.Input(shape=(NUM_STEPS, dataset.NUM_FEATURES))
    x = keras.layers.LSTM(units=nodes, return_sequences=(layers != 1))(inputs)
    x = keras.layers.Dropout(dropout)(x)
    for i in range(1, layers):
        x = keras.layers.LSTM(units=nodes, return_sequences=(i < layers - 1))(x)
        x = keras.layers.Dropout(dropout)(x)

    note_output = keras.layers.Dense(name="n", units=len(dataset.note_to_one_hot), activation='softmax')(x)
    duration_output = keras.layers.Dense(name="d", units=len(dataset.duration_to_one_hot), activation='softmax')(x)
    offset_output = keras.layers.Dense(name="o", units=len(dataset.offset_to_one_hot), activation='softmax')(x)

    model = keras.models.Model(name=model_name, inputs=inputs, outputs=[note_output, duration_output, offset_output])
    optimizer = keras.optimizers.RMSprop(lr=lr, rho=0.9, epsilon=None, decay=decay)
    losses = {"n": "categorical_crossentropy", "d": "categorical_crossentropy", "o": "categorical_crossentropy"}
    metrics = {"n": "categorical_accuracy", "d": "categorical_accuracy", "o": "categorical_accuracy"}
    model.compile(optimizer=optimizer, loss=losses, metrics=metrics)

    path = f"models/{model_name}/model.json"
    with open(path, "w") as f:
        f.write(model.to_json())
    s3.upload_file(path)

    path = f"models/{model_name}/summary.txt"
    with open(path, "w") as f:
        model.summary(print_fn=lambda line: f.write(line + "\n"))
    s3.upload_file(path)

    # delete the old tensorboard log file
    path = f"tensorboard/{model_name}"
    if os.path.exists(path):
        shutil.rmtree(path)

    return model


def load_model(model_name):

    last_epoch = 0
    last_file = ""

    # download any new files from S3
    if s3.down_sync_s3(f"models/{model_name}"):
        try:
            s3.download_file(f"models/{model_name}/log.csv")
        except Exception:
            pass
    s3.down_sync_s3(f"tensorboard/{model_name}")

    # find all the previous models
    for file in os.listdir(f"models/{model_name}"):
        if file.endswith(".hdf5"):
            epoch = int(file.split("_")[1])
            if epoch > last_epoch:
                last_epoch = epoch
                last_file = file

    if last_epoch:
        print(f"Loading model from disk (epoch {last_epoch})...")
        return keras.models.load_model(f"models/{model_name}/{last_file}"), last_epoch
    else:
        return None, 0


def fit_model(model, model_name, dataset, epochs, start_epoch):

    logfile = f"models/{model_name}/log.csv"

    steps_per_epoch = (dataset.train_lib.buf.shape[0] - 1) // BATCH_SIZE # it's - 1 because the very last step is a prediction only
    validation_steps_per_epoch = (dataset.test_lib.buf.shape[0] - 1) // BATCH_SIZE
    model_save_filepath = os.path.join(f"models/{model_name}", "epoch_{epoch:03d}_{val_loss:.4f}.hdf5")
    callbacks = [keras.callbacks.CSVLogger(logfile, append=True),
                 keras.callbacks.ModelCheckpoint(model_save_filepath, monitor='val_loss'),
                 keras.callbacks.TensorBoard(log_dir=f"tensorboard/{model_name}", write_graph=True, write_grads=True,
                                             write_images=True),
                 S3Callback(model_name)]

    model.fit_generator(dataset.train_lib.next_batch(), steps_per_epoch=steps_per_epoch, epochs=epochs,
                                   callbacks=callbacks, validation_data=dataset.test_lib.next_batch(),
                                   validation_steps=validation_steps_per_epoch, initial_epoch=start_epoch)

    return model


def get_args():

    parser = argparse.ArgumentParser(description="Converts a directory (and subdirectories) of MIDI files using the plugins.")
    parser.add_argument("library", help="The name of the library to load (str).", type=str)
    parser.add_argument("--layers", help="The number of hidden LSTM layers (int).", type=int)
    parser.add_argument("--nodes", help="The number of nodes in each hidden LSTM layer (int).", type=int)
    parser.add_argument("--dropout", help="The dropout value (float).", type=float)
    parser.add_argument("--lr", help="The learning rate (float)", type=float)
    parser.add_argument("--decay", help="The learning rate decay (float).", type=float)
    parser.add_argument("--epochs", help="The number of epochs to stop at (int).", type=int)
    args = parser.parse_args()

    lib_name = args.library
    layers = args.layers if args.layers else 5
    units = args.nodes if args.nodes else 512
    dropout = args.dropout if args.dropout else .333
    lr = args.lr if args.lr else 6.66e-5
    decay = args.decay if args.decay else 0
    epochs = args.epochs if args.epochs else 25

    model_name = lib_name + f"_layers{layers}_units{units}_drop{dropout}_lr{lr:.2e}_decay{decay}_batch{BATCH_SIZE}"

    return lib_name, model_name, layers, units, dropout, lr, decay, epochs



def main():

    lib_name, model_name, layers, nodes, dropout, lr, decay, epochs = get_args()

    if not os.path.exists(f"models/{model_name}"):
        os.makedirs(f"models/{model_name}")

    print("Loading dataset...")
    path = f"midi/pickles/{lib_name}.pkl"
    if not os.path.exists(path):
        s3.download_file(path)
    dataset = pickle_load(path)

    model, start_epoch = load_model(model_name)
    if not model:
        print("Creating model...")
        model = create_model(dataset, model_name, layers, nodes, dropout, lr, decay)

    print()
    print("***** DATASET")
    print("Features:".ljust(15), dataset.NUM_FEATURES)
    print("Training set:".ljust(15), len(dataset.train_indices))
    print("Test set:".ljust(15), len(dataset.test_indices))
    print()
    print("***** MODEL")
    print("Layers:".ljust(15), layers)
    print("Nodes:".ljust(15), nodes)
    print("Dropout:".ljust(15), dropout)
    print("Learning Rate:".ljust(15), lr)
    print("Decay:".ljust(15), decay)
    print("Epochs:".ljust(15), epochs)
    print("Parameters:".ljust(15), model.count_params())
    print()

    print("Fitting model...")
    fit_model(model, model_name, dataset, epochs, start_epoch)


if __name__ == "__main__":
    main()

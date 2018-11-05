import os
from functools import reduce


def get_filenames(base_dir, extensions=None):

    filenames = []

    for root, dirs, files in os.walk(base_dir):

        for file in files:

            full_path = os.path.join(root, file)

            if extensions:
                filename_lower = file.lower()
                if not reduce(lambda accum, x: accum or filename_lower.endswith(x), extensions):
                    print("Unknown file:", full_path)
                    continue

            filenames.append(full_path)

    return filenames

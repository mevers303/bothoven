import os


def get_filenames(base_dir):

    filenames = []

    for root, dirs, files in os.walk(base_dir):

        for file in files:

            full_path = os.path.join(root, file)
            filename = file.lower()
            if not (filename.endswith(".mid") or filename.endswith(".midi") or filename.endswith(".smf")):
                print("Unknown file:", full_path)
                continue

            filenames.append(full_path)

    return filenames


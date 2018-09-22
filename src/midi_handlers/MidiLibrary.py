import os
import random
from sklearn.model_selection import train_test_split
import wwts_globals



class MidiLibrary:

    def __init__(self, base_dir):

        self.base_dir = base_dir

        self.filenames = None
        self.filenames_count = 0
        self.labels = None
        self.composers = None

        self.get_filenames()


    def get_filenames(self):

        """
            Returns a list of files in <self.base_dir> and their associated label in y.  Files must be in
            <dir>/<composer>/*.mid"

            :return: None
        """

        self.filenames = []
        self.labels = []
        self.composers = set()

        for composer in os.listdir(self.base_dir):

            composer_files = []
            for root, dirs, files in os.walk(os.path.join(self.base_dir, composer)):

                for file in files:

                    full_path = os.path.join(root, file)
                    if not (file.lower().endswith(".mid") or file.lower().endswith(".midi")):
                        print("Unknown file:", full_path)
                        continue

                    composer_files.append(full_path)

            composer_works = len(composer_files)
            if composer_works < wwts_globals.MINIMUM_WORKS:
                print("Not enough works for {}, ({})".format(composer, composer_works))
                continue
            if composer_works > wwts_globals.MAXIMUM_WORKS:
                composer_files = random.sample(composer_files, wwts_globals.MAXIMUM_WORKS)
                composer_works = wwts_globals.MAXIMUM_WORKS

            self.filenames.extend(composer_files)
            self.labels.extend([composer] * composer_works)
            self.composers.add(composer)
            print("Added {} ({})".format(composer, composer_works))

        self.filenames_count = len(self.filenames)
        print("Found", self.filenames_count, "files from", len(self.composers), "artists!")



class MidiLibrarySplit(MidiLibrary):

    def __init__(self, base_dir):

        super().__init__(base_dir)

        self.filenames_train = None
        self.labels_train = None
        self.filenames_test = None
        self.labels_test = None

        self.split_files()


    def split_files(self):

        self.filenames_train, self.filenames_test, self.labels_train, self.labels_test = train_test_split(self.filenames, self.labels, stratify=self.labels)

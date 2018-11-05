# Sam Cohan
# https://stackoverflow.com/a/43419027

import pickle


class BigFile(object):

    def __init__(self, f):
        self.f = f

    def __getattr__(self, item):
        return getattr(self.f, item)

    def read(self, n):
        # print("reading total_bytes=%s" % n)
        if n >= (1 << 31):
            buffer = bytearray(n)
            idx = 0
            while idx < n:
                batch_size = min(n - idx, 1 << 31 - 1)
                # print("reading bytes [%s,%s)..." % (idx, idx + batch_size), end="")
                buffer[idx:idx + batch_size] = self.f.read(batch_size)
                # print("done.")
                idx += batch_size
            return buffer
        return self.f.read(n)

    def write(self, buffer):
        n = len(buffer)
        # print(f" -> Writing {n} total bytes...")
        idx = 0
        while idx < n:
            batch_size = min(n - idx, 1 << 31 - 1)
            # print(f" ---> Writing bytes [{idx}, {idx + batch_size})... ")
            self.f.write(buffer[idx:idx + batch_size])
            # print(f" ---> Done")
            idx += batch_size


def pickle_dump(obj, file_path):
    print(f"Caching {file_path}...")
    with open(file_path, "wb") as f:
        result = pickle.dump(obj, BigFile(f), protocol=pickle.HIGHEST_PROTOCOL)
    # print(" -> Done")
    return result


def pickle_load(file_path):
    print(f"Loading {file_path} from cache...")
    with open(file_path, "rb") as f:
        obj = pickle.load(BigFile(f))
    # print(" -> Done")
    return obj

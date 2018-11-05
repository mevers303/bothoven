import boto, boto.s3 as s3
import json

from functions.file_functions import get_filenames


with open("s3_key.json", "r") as f:
    _keyfile = json.load(f)
_bucket_name = "bothoven"


def sync_s3(dir, overwrite=False):

    files = get_filenames(dir)
    conn = boto.connect_s3(_keyfile["key"], _keyfile["secret_key"])
    bucket = conn.get_bucket(_bucket_name)

    if overwrite:
        upload_files_to_s3(bucket, files)
    else:
        keys = [key.name for key in bucket.get_all_keys()]
        new_files = set(files) - set(keys)
        upload_files_to_s3(bucket, new_files)


def upload_files_to_s3(bucket, files):

    for file in files:
        print(f"Uploading '{file}' to S3 bucket '{bucket.name}'...")
        key = s3.key.Key(bucket, file)
        key.set_contents_from_filename(file)



if __name__ == "__main__":
    sync_s3("models")
    sync_s3("tensorboard", overwrite=True)

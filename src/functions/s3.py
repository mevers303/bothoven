import boto, boto.s3 as s3
import json
import os

from functions.file_functions import get_filenames

with open("s3_key.json", "r") as f:
    _keyfile = json.load(f)
_bucket_name = "bothoven"



def upload_file_to_s3(file, bucket=None):

    if not bucket:
        conn = boto.connect_s3(_keyfile["key"], _keyfile["secret_key"])
        bucket = conn.get_bucket(_bucket_name)

    print(f"Uploading '{file}' to S3 bucket '{bucket.name}'...")
    key = s3.key.Key(bucket, file)
    key.set_contents_from_filename(file)


def sync_s3(dir, overwrite=False):

    conn = boto.connect_s3(_keyfile["key"], _keyfile["secret_key"])
    bucket = conn.get_bucket(_bucket_name)
    files = get_filenames(dir)

    if overwrite:
        upload_files_to_s3(bucket, files)
    else:
        keys = [key.name for key in bucket.get_all_keys()]
        new_files = set(files) - set(keys)
        upload_files_to_s3(bucket, new_files)


def upload_files_to_s3(bucket, files):

    for file in files:
        upload_file_to_s3(file, bucket)


def upload_latest_file(dir):

    conn = boto.connect_s3(_keyfile["key"], _keyfile["secret_key"])
    bucket = conn.get_bucket(_bucket_name)

    files = get_filenames(dir)
    latest_file = max(files, key=os.path.getctime)
    upload_file_to_s3(latest_file, bucket)




if __name__ == "__main__":
    sync_s3("models")
    sync_s3("tensorboard", overwrite=True)

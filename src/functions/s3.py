import boto, boto.s3 as s3
import json
import os

from functions.file_functions import get_filenames

with open("s3_key.json", "r") as f:
    _keyfile = json.load(f)
_bucket_name = "bothoven"



def get_bucket():
    conn = boto.connect_s3(_keyfile["key"], _keyfile["secret_key"])
    return conn.get_bucket(_bucket_name)


def upload_file(file, bucket=None):

    print(f"Uploading '{file}' to S3...")
    if not bucket:
        bucket = get_bucket()
    key = s3.key.Key(bucket, file)
    key.set_contents_from_filename(file)


def up_sync_s3(dir, overwrite=False):

    bucket = get_bucket()
    files = get_filenames(dir)

    if overwrite:
        upload_files(bucket, files)
        return len(files)
    else:
        keys = [key.name for key in bucket.get_all_keys()]
        new_files = set(files) - set(keys)
        upload_files(bucket, new_files)
        return len(new_files)


def upload_files(bucket, files):

    for file in files:
        upload_file(file, bucket)


def upload_latest_file(dir):

    bucket = get_bucket()

    files = get_filenames(dir)
    latest_file = max(files, key=os.path.getctime)
    upload_file(latest_file, bucket)


def down_sync_s3(dir, overwrite=False):
    
    bucket = get_bucket()
    files = get_filenames(dir)

    if overwrite:
        download_files(bucket, files)
        return len(files)
    else:
        keys = [key.name for key in bucket.get_all_keys() if key.name.startswith(dir)]
        new_files = set(keys) - set(files)
        download_files(bucket, new_files)
        return len(new_files)


def download_file(file, bucket=None):

    print(f"Downloading '{file}' from S3...")
    if not bucket:
        bucket = get_bucket()

    if not os.path.exists(os.path.dirname(file)):
        os.makedirs(os.path.dirname(file))

    key = s3.key.Key(bucket, file)
    key.get_contents_to_filename(file)


def download_files(bucket, files):
    
    for file in files:
        download_file(file, bucket)


if __name__ == "__main__":
    up_sync_s3("models")
    up_sync_s3("tensorboard", overwrite=True)

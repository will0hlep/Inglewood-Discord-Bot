"""
This module implements a check for changes in the bots code, allowing 
"""
import os
import pathlib
import hashlib
import pickle


def hash_dict():
    """
    Returns a dictionary containing md5 hashes of all python files in
    the current directory.

    Returns:
        output : dict
    """
    output = {}
    for file in os.listdir():
        if pathlib.PurePosixPath(file).suffix == '.py':
            with open(file, 'rb') as file_to_check:
                data = file_to_check.read()
                md5_returned = hashlib.md5(data).hexdigest()
                output[file] = md5_returned
    return output


def hash_check():
    """
    Returns True if the no python files in the current directory have
    been altered.

    Returns:
        bool
    """
    if os.path.exists('hash_dict.pkl'):
        with open('hash_dict.pkl', 'rb') as f:
            last_hash = pickle.load(f)
    else:
        last_hash = None
    new_hash = hash_dict()
    if new_hash != last_hash:
        with open('hash_dict.pkl', 'wb') as f:
            pickle.dump(new_hash, f)
        return True
    return False

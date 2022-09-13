"""Filesystem-based cache for storing JSON objects."""
import json
import os
from typing import Optional, TypeVar, cast

CACHE_DIR = os.path.join(os.getcwd(), ".autobot_cache")

T = TypeVar("T")


def cache_filename(key: str) -> str:
    return os.path.join(CACHE_DIR, key)


def has_in_cache(key: str) -> bool:
    os.makedirs(os.path.dirname(cache_filename(key)), exist_ok=True)
    return os.path.exists(cache_filename(key))


def get_from_cache(key: str) -> Optional[T]:
    os.makedirs(os.path.dirname(cache_filename(key)), exist_ok=True)
    try:
        with open(cache_filename(key), "r") as fp:
            return cast(T, json.load(fp))
    except FileNotFoundError:
        return None


def set_in_cache(key: str, value: T) -> None:
    os.makedirs(os.path.dirname(cache_filename(key)), exist_ok=True)
    with open(cache_filename(key), "w") as fp:
        json.dump(value, fp)


def delete_from_cache(key: str) -> bool:
    os.makedirs(os.path.dirname(cache_filename(key)), exist_ok=True)
    try:
        os.remove(cache_filename(key))
        return True
    except FileNotFoundError:
        return False

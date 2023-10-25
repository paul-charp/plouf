"""
Module containing functions relative to versioning of files and folders

Attributes:
    BASE_VERSION_REGEX (str): Regex matching a version number (ie: 'v000') in a string.
    DEFAULT_VERSION (str): Default version number to start from.
    FULL_VERSION_REGEX (str): Regex matching the LAST version number (ie: 'v000') in a string.
"""


# Imports

import os
import re


# Constants

BASE_VERSION_REGEX = r"(?P<v_str>v(?P<v_digits>\d{3}))"
FULL_VERSION_REGEX = BASE_VERSION_REGEX + r"(?!.*v\d{3})"
DEFAULT_VERSION = "v001"


# Functions


def versionFromString(string: str, pattern="") -> int:
    """
    Extracts the version number from a string

    Args:
        string (str): the string to extract from.
        pattern (str, optional): A pattern to match the version number in a specific string at a specific place,
        the use '{}' where the version number (including the leading 'v') is supposed to be.

    Returns:
        int: The version number found in the string.
    """
    if pattern != "":
        regex = pattern.format(BASE_VERSION_REGEX)
        version = re.search(regex, string)

    else:
        print(string, FULL_VERSION_REGEX)
        version = re.search(FULL_VERSION_REGEX, string)

    if not version:
        return None

    return int(version.group("v_digits"))


def formatVersion(version: int) -> str:
    """
    Formats a integer (int) into a version string (ie: 12 -> 'v012')

    Args:
        version (int): The version integer.

    Returns:
        str: The formatted version string.
    """
    digits = str(version).zfill(3)
    return f"v{digits}"


def incrementVersion(path: str, mode="dirs", basename="") -> str:
    """
    Finds the next version number from files or directories.

    Args:
        path (str): Path to look for the files or directories
        mode (str, optional): 'dirs' (Default): Looks only for directories at the path.
                                                  'files': Looks only for files at the path.
                                                  'both': Looks for both.
        basename (str, optional): A basename to match specific files or directories agains it.

    Returns:
        str: The next version number based on the files/dirs match (ie: the greatest version number match + 1)
    """
    if not os.path.isdir(path):
        return DEFAULT_VERSION

    names = list()

    for subdir, dirs, files in os.walk(path):
        if (mode == "dirs") or (mode == "both"):
            for d in dirs:
                if os.path.isdir(os.path.join(path, d)):
                    names.append(d)

        if (mode == "files") or (mode == "both"):
            for f in files:
                if os.path.isfile(os.path.join(path, f)):
                    names.append(f)

    if not names:
        return DEFAULT_VERSION

    versions = list()

    if basename != "":
        pattern = re.sub(FULL_VERSION_REGEX, "{}", basename)

    else:
        pattern = ""

    for name in names:
        version = versionFromString(name, pattern=pattern)

        if version is not None:
            versions.append(version)

    if not versions:
        return DEFAULT_VERSION

    versions.sort()
    last_version = versions[-1]

    next_version = last_version + 1

    return formatVersion(next_version)

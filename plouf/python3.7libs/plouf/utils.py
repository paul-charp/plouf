"""
Module containing utility functions for PLOUF.

Attributes:
    DEFAULT_NODE_COLOR (hou.Color): Default node color from Houdini (light-gray).
    FRAME_SEQUENCE_REGEX (str): Regex: matches the last sequence of digits in a string.
                                  Used to assert the frame number in a filename.
    PLOUF_PROJECT_ENV (str): Houdini Environment variable name pointing to the project root path. (Usually set in the plouf_env.json)
    PLOUF_ROOT_ENV (str): Houdini Environment variable name of the project name. (Usually set in the plouf_env.json)
    PUBLISHED_COLOR (hou.Color): Color used on published node that will overwrite an existing publish.
    BLACKLISTED_WORDS (list): List of words (str) blacklisted by the syncro tool (Resilio).
    BLACKLISTED_WORDS_REPLACEMENT (list): List of words (str) to replace blacklisted words in BLACKLISTED_WORDS when auto resolving thoses. Indexes should match between the two lists.
    HIP_LIC (dict): Key: hou.licenseCategoryType object, Value: Type of hipfile (ie: 'hip', 'hipnc', 'hiplc')
"""


# Imports

import os
import re
import hou
import subprocess
from collections import defaultdict


# Constants

FRAME_SEQUENCE_REGEX = r"\d+(?!.*\d+)"

PUBLISHED_COLOR = hou.Color((0.74, 0.45, 0.91))
DEFAULT_NODE_COLOR = hou.Color((0.84, 0.84, 0.84))

PLOUF_ROOT_ENV = 'PLOUF_ROOT'
PLOUF_PROJECT_ENV = 'PLOUF_PROJECT'

BLACKLISTED_WORDS = ['work']
BLACKLISTED_WORDS_REPLACEMENT = ['wrk']

HIP_LIC = {
    hou.licenseCategoryType.Education: 'hipnc',
    hou.licenseCategoryType.ApprenticeHD: 'hipnc',
    hou.licenseCategoryType.Apprentice: 'hipnc',
    hou.licenseCategoryType.Indie: 'hiplc',
    hou.licenseCategoryType.Commercial: 'hip'
}


# Functions

def getRoot() -> str:
    """
    Gets the root path of the PLOUF project from houdini env variable.
    Uses PLOUF_ROOT_ENV const.

    Returns:
        str: Path of the project root.
    """
    return hou.getenv(PLOUF_ROOT_ENV)


def getProject() -> str:
    """
    Gets the project name of the PLOUF project from houdini env variable.
    Uses PLOUF_PROJECT_ENV const.

    Returns:
        str: Project name.
    """
    return hou.getenv(PLOUF_PROJECT_ENV)


def setRoot(path: str):
    """
    Sets the PLOUF root path environement variable.

    Args:
        path (str): Root path to set.
    """
    hou.putenv(PLOUF_ROOT_ENV, path)


def setProject(name: str):
    """
    Sets the PLOUF project name environement variable.

    Args:
        name (str): Project name to set.
    """
    hou.putenv(PLOUF_PROJECT_ENV, name)


def explore(path: str):
    """
    Opens the windows explorer at the specified path (if the path is valid).

    Args:
        path (str): Path at which the explorer will open.
    """
    if os.path.isdir(path):
        path = os.path.normpath(path)
        subprocess.Popen("explorer " + path)


def formatString(string: str) -> str:
    """
    Formats or "sanitize" a string by replacing any illegal character with '_'. Also makes it lowercase.

    Args:
        string (str): The string to format.

    Returns:
        str: The formated string.
    """
    string = string.lower()
    string = hou.text.variableName(string)

    return string


def formatPath(path: str, collaspeVariables=list()) -> str:
    """
    Formats or "sanitize" a path.
    Can also collaspe variables (hou.text.collapseCommonVars()).

    Args:
        path (str): Path to format
        collaspeVariables (list, optional): List of houdini variables (str) (ie: ['$HIP']) to collapse.

    Returns:
        str: formatted path
    """
    formatted_path = hou.text.normpath(path)
    formatted_path = hou.text.collapseCommonVars(path, vars=collaspeVariables)

    return formatted_path


def formatFileList(files: list, collapseSequences=True, collaspeVariables=list()) -> list:
    """
    Formats a list of file paths by removing duplicates, sorting it and normalizing the paths.
    Optionaly it can collapse files sequences into this format: 'path/to/file[01-99].jpg'
    Can also collaspe variables (hou.text.collapseCommonVars()).

    Args:
        files (list): List of files path (str) to operate on.
        collapseSequences (bool, optional): If True collapse file sequences. Default is False
        collaspeVariables (list, optional): List of houdini variables (str) (ie: ['$HIP']) to collapse.

    Returns:
        list: Formatted list of file paths.
    """
    files = list(dict.fromkeys(files))  # Remove duplicates
    files.sort()

    if all(isinstance(item, str) for item in files):

        for index, file in enumerate(files):
            # file = file.replace('\\', '/') Find a way to remove backslashes
            files[index] = formatPath(file, collaspeVariables)

        if collapseSequences:
            formated_files = list()
            sequences = defaultdict(list)

            for file in files:
                dirname = os.path.dirname(file)
                filename = os.path.basename(file)

                match = re.findall(FRAME_SEQUENCE_REGEX, filename)

                if not match:
                    sequences[file] = list()
                    continue

                else:
                    frame = match[-1]
                    filename = re.sub(FRAME_SEQUENCE_REGEX, '{}', filename)
                    sequence = os.path.join(dirname, filename)
                    sequences[sequence].append(frame)

            for sequence, frames in sequences.items():
                if not frames:
                    formated_files.append(sequence)
                    continue

                frames.sort()
                first_frame = frames[0]
                last_frame = frames[-1]

                if first_frame is last_frame:
                    frame_range = first_frame

                else:
                    frame_range = f'[{first_frame}-{last_frame}]'

                formated_sequence = sequence.format(frame_range)

                formated_files.append(formated_sequence)

            return formated_files
    return files


def menuFromDir(path: str) -> list:
    """
    Creates a list of valid directory found in path.
    Each directory found is writting twice in the resulting list.
    This is made for creating Python driven menu scripts in Houdini HDAs interface.

    Args:
        path (str): The path to look for directories

    Returns:
        list: The list of directories (doubled) in path.
    """
    menuitem = list()

    if os.path.isdir(path):
        dirs = os.listdir(path)
        for d in dirs:
            if not d.startswith("."):
                if os.path.isdir(os.path.join(path, d)):
                    menuitem.append(d)
                    menuitem.append(d)

    menuitem.sort()
    return menuitem


def setColorState(node: hou.Node, publish):
    """
    Changes the Node's color if the publish files exists or not.

    Args:
        node (hou.Node): Node to change the color of.
        publish (plouf.Publish): Publish object.
    """
    if publish.isPublished():
        node.setColor(PUBLISHED_COLOR)

    else:
        node.setColor(DEFAULT_NODE_COLOR)


def assetPublishState(path: str, root=getRoot()) -> tuple:
    """
    Checks if a asset at the specified path exist, and if it is published: avaible in the pipeline (In the root path, and doesn't contain blacklisted words).

    Args:
        path (str): Asset path
        root (str, optional): Pipeline/Project root, default to getRoot() value

    Returns:
        tuple: a tuple containing a bool (True: the asset is published, False: it is not)
                and a message (str) as why the asset is not published.
    """
    path = path.lower()
    root = root.lower()
    if path.startswith('op:'):
        reason_msg = "Internal OpPath, disregards"
        state = True

    elif path.startswith('anon:'):
        reason_msg = "Anonymous Layer, disregards"
        state = True

    elif '<UDIM>' in path or '<udim>' in path:
        reason_msg = "Exception : UDIM Tags"
        state = False

    elif os.path.isfile(path):
        path = os.path.abspath(path)
        root = os.path.abspath(root)

        if not path.startswith(root):
            reason_msg = "Asset not in project root"
            state = False

        elif any(word in path.lower() for word in BLACKLISTED_WORDS):
            reason_msg = f"Asset contains any of blacklisted words: {BLACKLISTED_WORDS}"
            state = False

        else:
            reason_msg = "Asset is published"
            state = True

    else:
        reason_msg = "Asset doesn't exists"
        state = False

    return (state, reason_msg)


def resolveBlacklistedWords(string: str) -> str:
    """
    Replaces blacklisted words by their replacements
    See : BLACKLISTED_WORDS, BLACKLISTED_WORDS_REPLACEMENT constant descriptions.

    Args:
        string (str): String to process.

    Returns:
        str: String with eventual blacklisted words replaced.
    """
    for word, replc in zip(BLACKLISTED_WORDS, BLACKLISTED_WORDS_REPLACEMENT):
        string.replace(word, replc)

    return string


def hipFileType() -> str:
    """
    Returns the Hip extension depending on the license type.

    Returns:
        str: 'hip', 'hipnc', 'hiplc'
    """
    license = hou.licenseCategory()

    return HIP_LIC.get(license)

"""
Module containing functions dealing with USD Layers dependency management.

Attributes:
    RESOLVE_NAME_SUFFIX (str): Suffix to use on the publish name when auto resolving dependencies.
    VAR_TO_COLLAPSE (list): Env Variables to collapse in the paths.
"""

# Imports

import os
import re
import shutil

from pxr import UsdUtils

from .utils import (
    assetPublishState,
    resolveBlacklistedWords,
    formatFileList,
    formatString,
)
from collections import defaultdict
from copy import deepcopy

# Constants

VAR_TO_COLLAPSE = ["$HIP", "$JOB", "$ASSETS", "$SHOTS", "$MS_US", "$HFIRE", "$FIREMEN"]
RESOLVE_NAME_SUFFIX = "extras"


# Functions


def checkDependencies(layer) -> tuple:
    """
    Checks the dependencies of the given USD Layer. (See plouf.utils.asseetPublishState())

    Args:
        layer (SdfLayer): UsdApi SdfLayer.

    Returns:
        tuple: (assets, reasons) Assets (str): the unpublished assets paths. Reasons (str): Why the asset isn't published.
    """
    unpublished_assets = list()
    unpublished_reason = list()

    def asset_path_check(assetPath: str) -> str:
        """
        Runs for every asset with UsdUtils.ModifyAssetPaths()
        Doesn't affect assetPath.
        Appends assetPath and the reason for all unpublished assets to unpublished_assets, unpublished_reason

        Args:
            assetPath (str): assetPath

        Returns:
            str: assetPath
        """
        state, msg = assetPublishState(assetPath)

        if not state:
            unpublished_assets.append(assetPath)
            unpublished_reason.append(msg)

        return assetPath

    UsdUtils.ModifyAssetPaths(layer, asset_path_check)

    return (unpublished_assets, unpublished_reason)


def resolveDependencies(unpublished_assets: tuple, publish) -> dict:
    """
        For each unpublished asset in the USD Layer, removes any blacklisted words, and makes a Publish instance
        based on the on provided on 'publish' with the resolved attributes for the asset to be published.

    Args:
        unpublished_assets (tuple): Result of checkDependencies() function.
        publish (Publish): The publish instance to inherit from.

    Returns:
        dict: key: original asset path, value: the Publish instance.
    """
    assets, _ = unpublished_assets

    assets_dict = defaultdict(str)

    for asset in assets:
        if os.path.isfile(asset):
            filename, ext = os.path.splitext(os.path.basename(asset))

            filename = resolveBlacklistedWords(
                formatString(filename)
            )  # Remove blacklisted words
            ext = formatString(
                ext[1:]
            )  # Remove the '.' at the begging of the extension

            asset_publish = deepcopy(publish)

            asset_publish.publish_name = f"{publish.publish_name}_{RESOLVE_NAME_SUFFIX}"  # Find a way to reduce the filename part (matching agains the base publish name)
            asset_publish.file_ext = ext
            asset_publish.extra_filename = filename

            assets_dict[asset] = asset_publish  # Resolve dependency

        del asset_publish

    print('resolveDependencies:output', assets_dict)
    return assets_dict


def publishDependencies(assets_dict: dict, overwrite=False):
    """
    Publishes on disk all the resolved assets,
    makes a copy from the original path, to the one given by the publish instance.

    Args:
        assets_dict (dict): Result of the resolveDependencies() function.
        overwrite (bool): Allow the overwrite of existing files on disk (Default to False) and should stay false for security reasons.
    """
    for original, publish in assets_dict.items():
        publish.makePublishPath()
        path = publish.getPublishPath()
        exist = os.path.isfile(path)

        if exist and overwrite:
            shutil.copy(original, path)

        elif not exist:
            shutil.copy(original, path)


def applyResolvedDependencies(layer, assets_dict: dict):
    """
    Replaces the path to unpublished assets to the published one in a USD Layer.

    Args:
        layer (SdfLayer): USD Layer.
        assets_dict (dict): Result of the resolveDependencies() function.
    """

    def asset_path_resolve(assetPath: str) -> str:
        """
        Runs for every asset with UsdUtils.ModifyAssetPaths()
        If the assetPath exist as an unpublished assets then replaces it with the resolved one.
        If not, returns the original path.

        Args:
            assetPath (str): assetPath

        Returns:
            str: original asset path or resolved one.
        """
        if assetPath in assets_dict:
            asset = assets_dict.get(assetPath)
            return asset.getPublishPath()

        else:
            return assetPath

    UsdUtils.ModifyAssetPaths(layer, asset_path_resolve)


def formatDependenciesMessage(unpublished_assets: tuple) -> str:
    """
    Formats all the unpublished assets and theirs reasons in the form of a multi line string.
    reason
    assetpath
    etc.
    Also collapses variables (VAR_TO_COLLAPSE) and sequences.

    Args:
        unpublished_assets (tuple): Result of checkDependencies() function.

    Returns:
        str: A Multiline string with all the assetPaths a their reasons.
    """
    assets, reasons = unpublished_assets

    assets = formatFileList(assets, collaspeVariables=VAR_TO_COLLAPSE)

    message = str()

    for asset, reason in zip(assets, reasons):
        message = message + f"{reason}:\n{asset}\n"

    return message

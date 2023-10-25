"""
Module containing callback functions to interact with nodes in houdini.

Attributes:
    DEPENDENCIES_INFO_PARM (str): Name of the parameter displaying the dependencies info
    LAYER_NODE (str): Name of the node flattening the layers
    PUBLISH_PATH_INFO_PARM (str): Name of the parameter displaying the publish path info
    ROP_NODE (str): Name of the rop usdrop node.
    TOGGLE_HISTORY_PARM (str): Name of the parameter toggeling the publish history.
    TOGGLE_RESOLVE_DEPENDENCIES_PARM (str): Name of the parameter toggeling the dependencies auto-resolve.
    VERSION_HISTORY_PARM (str): Name of the parameter holding the the history version number
"""


# Imports

import hou

from .utils import setColorState
from .usd_dependencies import checkDependencies, formatDependenciesMessage, resolveDependencies, publishDependencies
from .Publish import Publish
from .PublishCache import PublishCache


# Constants

ROP_NODE = 'usd_rop'
LAYER_NODE = 'flattened_layer'

TOGGLE_HISTORY_PARM = 't_history'
VERSION_HISTORY_PARM = 'history_version'

TOGGLE_RESOLVE_DEPENDENCIES_PARM = 't_resolveDependencies'

PUBLISH_PATH_INFO_PARM = 'publish_path_info'
DEPENDENCIES_INFO_PARM = 'dependencies_info'


# Callback functions.

# Publish

def cb_publish_pathUpdate(kwargs: dict, file_ext='usd'):
    """
    Callback function: When a path related parameters changes.

    Args:
        kwargs (dict): kwargs
    """
    node = kwargs.get('node')
    info_parm = node.parm(PUBLISH_PATH_INFO_PARM)
    publish = Publish(node, file_ext=file_ext)

    setColorState(node, publish)
    info_parm.set(publish.getPublishPath())

def cb_publish_cache_pathUpdate(kwargs: dict):
    """
    Callback function: When a path related parameters changes.

    Args:
        kwargs (dict): kwargs
    """
    node = kwargs.get('node')
    info_parm = node.parm(PUBLISH_PATH_INFO_PARM)

    usd_layer = bool(node.parm('t_usdlayer').eval())
    time_cache = bool(node.parm('t_frames').eval())
    if usd_layer:
        publish = Publish(node, file_ext='usd')
    elif not usd_layer and time_cache:
        publish = PublishCache(node)
    elif not time_cache:
        publish = Publish(node, file_ext='vdb')

    setColorState(node, publish)

    info_parm.set(publish.getPublishPath())


def cb_publish_execute(kwargs: dict, file_ext='usd'):
    """Summary

    Args:
        kwargs (dict): kwargs
    """
    node = kwargs.get('node')

    execute_node = hou.node(f'{node.path()}/{ROP_NODE}')  # Implement
    execute_parm = execute_node.parm('execute')

    publish = Publish(node, file_ext=file_ext)

    if node.parm(TOGGLE_HISTORY_PARM).eval():
        history_version_parm = node.parm(VERSION_HISTORY_PARM)
        history_version = publish.getHistoryVersion()
        history_version_parm.set(history_version)
        publish.makeHistoryPath(version=history_version)

    unpublished_assets = cb_publish_checkDependencies(kwargs)

    if node.parm(TOGGLE_RESOLVE_DEPENDENCIES_PARM).eval():
        resolved_assets = resolveDependencies(unpublished_assets, publish)
        overwrite_assets = bool(node.parm('t_dependencies_overwrite'))
        publishDependencies(resolved_assets, overwrite=overwrite_assets)

        #Don't forget to applyResolvedDependencies(layer, resolved_assets) either here or in a rop node

    publish.publishHipFile()
    execute_parm.pressButton()


def cb_publish_checkDependencies(kwargs: dict) -> tuple:
    """Summary

    Args:
        kwargs (dict): kwargs

    Returns:
        tuple: kwargs
    """
    node = kwargs.get('node')
    layer = node.activeLayer()
    layer.SetPermissionToEdit(True)
    dependencies_info_parm = node.parm(DEPENDENCIES_INFO_PARM)

    layer_node = hou.node(f'{node.path()}/{LAYER_NODE}')
    layer = layer_node.activeLayer()

    layer.SetPermissionToEdit(True)
    unpublished_assets = checkDependencies(layer)
    layer.SetPermissionToEdit(False)

    dependencies_info = formatDependenciesMessage(unpublished_assets)
    dependencies_info_parm.set(dependencies_info)

    return unpublished_assets

"""
Module containing the Publish class.

Attributes:
    HISTORY_DIR (str): directory in the $HIP containing publishes history.

"""


# Imports

import hou
import os
import shutil
from .utils import getRoot, getProject, formatString, resolveBlacklistedWords, hipFileType
from .versioning import incrementVersion, DEFAULT_VERSION


# Constants

HISTORY_DIR = 'publish_history'


# Classes

class Publish:
    """
    Class storing all the parameters needed for a publish.
    Also provides methods to get thoses parameters in certains formats and to publish to current hip file.

    Attributes:
        entity_name (str): asset name or shot number (ie: p010)
        entity_subtype (str): asset type (ie: 'fx, 'prop') or the sequence number (ie: s01)
        entity_type (str): 'assets' or 'shots'
        file_ext (str): Publish file extension, default to 'usd'
        project (str): Project name
        publish_name (str): Publish name, defaults to 'main'
        root (str): Project root
        task_name (str): Task name (ie: modeling_main)
    """

    def __init__(self, node, extra_filename='', file_ext="usd"):

        def get_parm(parm_name):
            return resolveBlacklistedWords(formatString(node.parm(parm_name).eval()))

        self.root = getRoot()
        self.project = resolveBlacklistedWords(formatString(getProject()))
        self.entity_type = get_parm("entity_type")
        self.entity_subtype = get_parm("entity_subtype")
        self.entity_name = get_parm("entity_name")
        self.task_name = get_parm("task_name")
        self.publish_name = get_parm("publish_name")
        self.extra_filename = resolveBlacklistedWords(formatString(extra_filename))
        self.file_ext = resolveBlacklistedWords(formatString(file_ext))

    def __repr__(self):
        """
        Class reprentation.

        Returns:
            str: Class representation.
        """
        return f"{self.root}/{self.project}/{self.entity_type}/{self.entity_subtype}/{self.entity_name}/{self.task_name}/{self.publish_name}/{self.extra_filename}/{self.file_ext}"

    def fileModeChooser(self, filename: str, path: str, mode:str) -> str:
        """
        Combines filename and path, according to the mode.

        Args:
            mode (str, optional): Mode 'full': joins the path and the filename ;
                                  Mode 'path': return only the path ;
                                  Mode 'file': return only the filename
                                  Default to 'full'
            filename (TYPE): Description
            path (TYPE): Description
            filename (str)
            path (str)

        Returns:
            str: The path, the filename, or both combined.
        """
        if mode == "full":
            return os.path.join(path, filename)

        if mode == "file":
            return filename

        if mode == "path":
            return path

    def getTaskPath(self) -> str:
        """
        Construct the path to the task name.

        Returns:
            str: Path to the task name
        """
        return os.path.join(
            self.root,
            self.project,
            self.entity_type,
            self.entity_subtype,
            self.entity_name,
            self.task_name,
        )

    def getPublishPath(self, mode="full", version='v000') -> str:
        """
        Returns an absolute path from the root to the publish file.

        Args:
            mode (str, optional): Mode 'full': joins the path and the filename ; Mode 'path': return only the path ; Mode 'file': return only the filename

        Returns:
            str: The path.
        """
        # Construct filename
        extra_filename = ''
        if self.extra_filename != '':
            extra_filename = f"_{self.extra_filename}"

        filename = f"{self.project}_{self.entity_subtype}_{self.entity_name}_{self.task_name}_publish_{version}_{self.publish_name}{extra_filename}.{self.file_ext}"
        # Construct path
        task_path = self.getTaskPath()
        path = os.path.join(
            task_path, "publish", version, self.file_ext, self.publish_name)

        return self.fileModeChooser(filename, path, mode)

    def getWorkPath(self, mode="full", version='v001') -> str:
        """
        Returns an absolute path from the root to the work file.

        Args:
            mode (str, optional): Mode 'full': joins the path and the filename ;
                                  Mode 'path': return only the path ;
                                  Mode 'file': return only the filename
                                  Default to 'full'
            version (str, optional): Default to 'DEFAULT_VERSION'

        Returns:
            str: The path.
        """
        # Construct filename
        filename = f"{self.project}_{self.entity_subtype}_{self.entity_name}_{self.task_name}_work_{version}.{hipFileType()}"

        # Construct path
        task_path = self.getTaskPath()
        path = os.path.join(task_path, "work")

        return self.fileModeChooser(filename, path, mode)

    def getHistoryPath(self, mode='full', version="v001") -> str:
        """
        Gets the history path.

        Args:
            mode (str, optional): Mode 'full': joins the path and the filename ;
                                  Mode 'path': return only the path ;
                                  Mode 'file': return only the filename
                                  Default to 'full'

        Returns:
            str: Path to the publish history file or directory (see above).
        """

        path = os.path.join(hou.getenv('HIP'),
                            HISTORY_DIR,
                            version,
                            self.file_ext,
                            self.publish_name)

        filename = self.getPublishPath(mode='file', version=version)

        return self.fileModeChooser(filename, path, mode=mode)

    def getHistoryVersion(self) -> str:
        version = DEFAULT_VERSION
        exist = True

        while exist:

            fullpath = self.getHistoryPath(mode='full', version=version)
            filename = self.getHistoryPath(mode='file', version=version)
            path = self.getHistoryPath(mode='path', version=version)

            exist = os.path.isfile(fullpath)
            if exist:
                version = incrementVersion(path, mode='files', basename=filename)

        return version

    def isPublished(self) -> bool:
        """
        Check if the file is published.

        Returns:
            bool: True if the publish exist, False if not.
        """
        return os.path.isfile(self.getPublishPath())

    def makeWorkPath(self, version="v001"):
        """
        Creates the path to the work file.

        Args:
            version (str, optional): Default to DEFAULT_VERSION
        """
        os.makedirs(self.getWorkPath(mode="path", version=version), exist_ok=True)

    def makePublishPath(self):
        """
        Creates the path to the publish file.
        """
        os.makedirs(self.getPublishPath(mode="path"), exist_ok=True)

    def makeHistoryPath(self, version="v001"):
        """
        Creates the path to the history file.

        Args:
            version (str, optional): Default to DEFAULT_VERSION
        """
        os.makedirs(self.getHistoryPath(mode="path", version=version), exist_ok=True)

    def publishHipFile(self) -> tuple:
        """
        Publish the current hip file as a sidecar publish to the main publish.
        Save the current hip as a backup, or if the houdini session hasn't ben saved yet, saves it to the correct work location.

        Returns:
            tuple: Publish instance describing the hip file that was just published.
        """
        if hou.hipFile.isNewFile():
            self.makeWorkPath()
            hip = self.getWorkPath()
            hip_name = self.getWorkPath(mode="file")
            hip_path = self.getWorkPath(mode="path")

            if os.path.isfile(hip):
                version = incrementVersion(hip_path, mode="files", basename=hip_name)
                hip = self.getWorkPath(version=version)

            hou.hipFile.save(hip)

        else:
            hip = hou.hipFile.saveAsBackup()

        hipPublish = self
        hipPublish.file_ext = hipFileType()

        hipPublish.makePublishPath()
        publish = hipPublish.getPublishPath()

        shutil.copy(hip, publish)

        return hipPublish

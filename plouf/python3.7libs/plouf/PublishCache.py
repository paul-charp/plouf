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
from .Publish import Publish


# Constants

HISTORY_DIR = 'publish_history'


# Classes

class PublishCache(Publish):
    """docstring for PublishCache"""

    def __init__(
        self,
        node,
        extra_filename='',
        file_ext='vdb',
        frame_range=(1001, 1250)
    ):
        super(PublishCache, self).__init__(node, extra_filename, file_ext)

        frame_range = (node.parm("f1").eval(), node.parm("f2").eval())

        if(frame_range[0] < frame_range[1]):
            self.frame_range = frame_range

    def __repr__(self):
        """
        Class reprentation.

        Returns:
            str: Class representation.
        """
        return f"{self.root}/{self.project}/{self.entity_type}/{self.entity_subtype}/{self.entity_name}/{self.task_name}/{self.publish_name}/{self.extra_filename}/{self.frame_range}/{self.file_ext}"

    def getPublishPath(self, mode="full", version='v000', frame_mode='placeholder', frame=0) -> str:
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

        if frame_mode == 'placeholder':
            frame_str = '$F4'
        elif frame_mode == 'specific':
            frame_str = str(frame).zfill(4)

        filename = f"{self.project}_{self.entity_subtype}_{self.entity_name}_{self.task_name}_publish_{version}_{self.publish_name}{extra_filename}.{frame_str}.{self.file_ext}"
        # Construct path
        task_path = super().getTaskPath()
        path = os.path.join(
            task_path, "publish", version, self.file_ext, self.publish_name)

        return self.fileModeChooser(filename, path, mode)

    def isPublished(self) -> bool:
        """
        Check if the file is published.

        Returns:
            bool: True if the publish exist, False if not.
        """
        start, end = self.frame_range
        for i in range(int(start), int(end)):
            frame = str(i).zfill(4)
            file = self.getPublishPath(frame_mode='specific', frame=i)

            if os.path.isfile(file):
                return True

        return False

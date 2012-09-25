"""
Copyright (c) 2012 Shotgun Software, Inc
----------------------------------------------------

Hook that loads items into the current scene.

"""

from tank import Hook

class MotionbuilderAddFileToScene(Hook):

    def execute(self, file_path, shotgun_data, **kwargs):

        from pyfbsdk import FBApplication
        app = FBApplication()
        app.FileMerge(file_path)

"""
Copyright (c) 2012 Shotgun Software, Inc
----------------------------------------------------
"""
import tempfile
import os
import platform
import sys
import uuid
import shutil
import tank

class AppHandler(object):
    """
    Handles the startup of the UIs, wrapped so that
    it works nicely in batch mode.
    """
    
    def __init__(self, app):
        self._app = app

    def show_dialog(self):
        # do the import just before so that this app can run nicely in nuke
        # command line mode,
        from .dialog import AppDialog
        
        # Need to keep the dialog object from being GC-ed
        self._dialog = tank.platform.qt.create_dialog(AppDialog)
        self._dialog.post_init(self._app)
        self._dialog.show()


        
        

"""
Copyright (c) 2012 Shotgun Software, Inc
----------------------------------------------------

Hook that loads items into the current scene.

"""

from tank import Hook

class NukeAddFileToScene(Hook):

    def execute(self, file_path, shotgun_data, **kwargs):
        
        import nuke
        
        # create the read node
        nuke.nodes.Read(file=file_path)        
        

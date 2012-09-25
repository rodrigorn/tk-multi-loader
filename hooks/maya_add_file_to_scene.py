"""
Copyright (c) 2012 Shotgun Software, Inc
----------------------------------------------------

Hook that loads items into the current scene. 

"""

from tank import Hook

class MayaAddFileToScene(Hook):
    
    def execute(self, file_path, shotgun_data, **kwargs):
        
        import pymel.core as pm

        pm.system.createReference(file_path)
        
        
    
"""
Copyright (c) 2012 Shotgun Software, Inc
----------------------------------------------------

Hook that loads items into the current scene. 

"""

from tank import Hook

class MayaAddFileToScene(Hook):
    
    def execute(self, engine_name, file_path, shotgun_data, **kwargs):
        
        if engine_name=="tk-maya":
            self.add_file_to_maya(file_path, shotgun_data)
        elif engine_name=="tk-nuke":
            self.add_file_to_nuke(file_path, shotgun_data)
        elif engine_name=="tk-motionbuilder":
            self.add_file_to_motionbuilder(file_path, shotgun_data)
        else:
            raise Exception("Don't know how to load file into unknown engine %s" % engine_name)
        
    ###############################################################################################
            
    def add_file_to_maya(self, file_path, shotgun_data):
        
        import pymel.core as pm
        
        # get the slashes right
        file_path = file_path.replace(os.path.sep, "/")
        
        pm.system.createReference(file_path)
        
    def add_file_to_nuke(self, file_path, shotgun_data):

        import nuke
        
        # get the slashes right
        file_path = file_path.replace(os.path.sep, "/")

        # create the read node
        nuke.nodes.Read(file=file_path)        



    def add_file_to_motionbuilder(self, file_path, shotgun_data):
        
        from pyfbsdk import FBApplication

        # get the slashes right
        file_path = file_path.replace(os.path.sep, "/")
        
        app = FBApplication()
        app.FileMerge(file_path)

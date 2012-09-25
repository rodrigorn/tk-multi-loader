"""
Copyright (c) 2012 Shotgun Software, Inc
----------------------------------------------------
"""
import tank
import os
import sys
import threading

from PySide import QtCore, QtGui
from .ui.dialog import Ui_Dialog

class AppDialog(QtGui.QDialog):

    
    def __init__(self, app):
        QtGui.QDialog.__init__(self)
        self._app = app
        # set up the UI
        self.ui = Ui_Dialog() 
        self.ui.setupUi(self)

        self._settings = QtCore.QSettings("Shotgun Software", "tk-multi-loader")
        
        # set up the browsers
        self.ui.left_browser.set_app(self._app)
        self.ui.middle_browser.set_app(self._app)
        self.ui.right_browser.set_app(self._app)

        # set the browser labels        
        types_to_load = self._app.get_setting("sg_entity_types", [])
        plural_types = [ "%ss" % x for x in types_to_load] # no fanciness (sheep, box, nucleus etc)
        if len(plural_types) == 1:
            # "Shots"
            types_str = plural_types[0]
        else:
            # "Shots, Assets & Sequences"
            types_str = ", ".join(plural_types[:-1])
            types_str += " & %s" % plural_types[-1]
            
        self.ui.left_browser.set_label(types_str)
        
        self.ui.middle_browser.set_label("Publishes")
        self.ui.right_browser.set_label("Versions")
        
        self.toggle_load_button_enabled()
        self.ui.load_selected.clicked.connect( self.load_item )
        
        self.ui.left_browser.selection_changed.connect( self.setup_publish_list )
        self.ui.middle_browser.selection_changed.connect( self.setup_version_list )
        self.ui.right_browser.action_requested.connect( self.load_item )
        
        self.ui.left_browser.selection_changed.connect( self.toggle_load_button_enabled )
        self.ui.middle_browser.selection_changed.connect( self.toggle_load_button_enabled )
        self.ui.right_browser.selection_changed.connect( self.toggle_load_button_enabled )
                
        # load data from shotgun
        # this qsettings stuff seems super flaky on different platforms
        prev_selection = {}
        try:            
            type_key = "%s/curr_entity_type" % self._app.get_setting("menu_name")
            id_key = "%s/curr_entity_id" % self._app.get_setting("menu_name")
            entity_id = self._settings.value(id_key).toInt()
            entity_type = str(self._settings.value(type_key))
            prev_selection = {"type": entity_type, "id": entity_id}
        except Exception, e:
            self._app.log_warning("Cannot restore previous task state: %s" % e)
        
        self.setup_entity_list(prev_selection)
        
    ########################################################################################
    # make sure we trap when the dialog is closed so that we can shut down 
    # our threads. Nuke does not do proper cleanup on exit.
    
    def _cleanup(self):
        self.ui.left_browser.destroy()
        self.ui.middle_browser.destroy()
        self.ui.right_browser.destroy()
        
    def closeEvent(self, event):
        self._cleanup()
        # okay to close!
        event.accept()
        
    def accept(self):
        self._cleanup()
        QtGui.QDialog.accept(self)
        
    def reject(self):
        self._cleanup()
        QtGui.QDialog.reject(self)
        
    def done(self, status):
        self._cleanup()
        QtGui.QDialog.done(self, status)
        
    ########################################################################################
    # basic business logic        
        
    def toggle_load_button_enabled(self):
        """
        Control the enabled state of the load button
        """
        curr_selection = self.ui.right_browser.get_selected_item()
        if curr_selection is None:
            self.ui.load_selected.setEnabled(False)
        else:
            self.ui.load_selected.setEnabled(True)
        
        
    def setup_entity_list(self, prev_selection): 
        self.ui.left_browser.clear()
        self.ui.middle_browser.clear()
        self.ui.right_browser.clear()
        d = { "prev_selection": prev_selection}
        self.ui.left_browser.load(d)
        
    def setup_publish_list(self):
        
        self.ui.middle_browser.clear()
        self.ui.right_browser.clear()
        
        curr_selection = self.ui.left_browser.get_selected_item()
        if curr_selection is None:
            return
        
        # save selection
        type_key = "%s/curr_entity_type" % self._app.get_setting("menu_name")
        id_key = "%s/curr_entity_id" % self._app.get_setting("menu_name")
        self._settings.setValue(type_key, curr_selection.sg_data["type"])
        self._settings.setValue(id_key, curr_selection.sg_data["id"])
        
        d = {}
        d["entity"] = curr_selection.sg_data
        self.ui.middle_browser.load(d)
        
    def setup_version_list(self):
        
        self.ui.right_browser.clear()
        
        entity_selection = self.ui.left_browser.get_selected_item()
        if entity_selection is None:
            return
        
        publish_selection = self.ui.middle_browser.get_selected_item()
        if publish_selection is None:
            return
        
        d = {}
        d["entity"] = entity_selection.sg_data
        d["publish"] = publish_selection.sg_data
        self.ui.right_browser.load(d)
        
    def load_item(self):
        """
        Load something into the scene
        """
        curr_selection = self.ui.right_browser.get_selected_item()
        if curr_selection is None:
            return
        
        local_path = curr_selection.sg_data.get("path").get("local_path")

        if local_path is None:
            QtGui.QMessageBox.critical(self, 
                                       "No path!", 
                                       "This publish does not have a path associated!")
            return
        
        # call out to our hook for loading.
        self._app.execute_hook("hook_add_file_to_scene", 
                               engine_name=self.engine.name, 
                               file_path=local_path, 
                               shotgun_data=curr_selection.sg_data)


        
        
"""
Copyright (c) 2012 Shotgun Software, Inc
----------------------------------------------------
"""
import tank
import os
import sys
import threading

from tank.platform.qt import QtCore, QtGui

browser_widget = tank.platform.import_framework("tk-framework-widget", "browser_widget")

class VersionBrowserWidget(browser_widget.BrowserWidget):

    
    def __init__(self, parent=None):
        browser_widget.BrowserWidget.__init__(self, parent)        
        

    def get_data(self, data):

        current_entity = data["entity"]
        current_publish = data["publish"]
        publish_name = current_publish.get("name")
        publish_type = current_publish.get("tank_type")

        # load publishes with the same name, entity and type 
        data = self._app.shotgun.find("TankPublishedFile", 
                                      [ ["project", "is", self._app.context.project],
                                        ["entity", "is", current_entity],
                                        ["tank_type", "is", publish_type],
                                        ["name", "is", publish_name] ], 
                                      ["description", 
                                       "version_number", 
                                       "image", 
                                       "created_at",
                                       "created_by",
                                       "path",
                                       "name"],
                                      [{"field_name": "created_at", "direction": "desc"}]
                                      )
        
            
        return {"data": data }
            
    def process_result(self, result):

        # select the first version we render (the latest version)
        selected = False

        for d in result.get("data"):
            
            i = self.add_item(browser_widget.ListItem)
            if not selected:
                self.select(i)
                selected = True
            
            details = []
            details.append("<b>Version %s</b>" % d.get("version_number") )
            details.append("<i><small>%s, %s</small></i>" % (d.get("created_by", {}).get("name"), 
                                                             d.get("created_at")) )
            details.append("%s" % d.get("description", "No Comments") )
            
            i.set_details("<br>".join(details))
            i.sg_data = d
            if d.get("image"):
                i.set_thumbnail(d.get("image"))                

        
        
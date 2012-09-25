"""
Copyright (c) 2012 Shotgun Software, Inc
----------------------------------------------------
"""
import tank
import os
import sys
import threading

from PySide import QtCore, QtGui
from .browser_widget import BrowserWidget
from .browser_widget import ListItem
from .browser_widget import ListHeader

class EntityBrowserWidget(BrowserWidget):

    
    def __init__(self, parent=None):
        BrowserWidget.__init__(self, parent)

    def get_data(self, data):
            
        previous_selection = data["prev_selection"]
            
            
        entity_cfg = self._app.get_setting("sg_entity_types", {})
        # example: {"Shot": [["desc", "startswith", "foo"]] }        
        types_to_load = entity_cfg.keys()
                    
        sg_data = []

        # load all entities
        for et in types_to_load:            
            item = {}
            item["type"] = et
            
            filters = []
            # add any custom filters
            filters.extend(entity_cfg[et])
            # and project of course
            filters.append(["project", "is", self._app.context.project])
            
            item["data"] = self._app.shotgun.find(et, filters, ["code", "description", "image"])
            
            sg_data.append(item)
            
        
        return {"previous_selection": previous_selection, "sg_data": sg_data}


    def process_result(self, result):

        previous_selection = result.get("previous_selection") 
        sg_data = result.get("sg_data")

        prev_selection_item = None

        for item in sg_data:
            i = self.add_item(ListHeader)
            i.set_title("%ss" % item["type"])
            for d in item["data"]:
                i = self.add_item(ListItem)
                
                details = "<b>%s %s</b><br>%s" % (d.get("type"), 
                                                  d.get("code"), 
                                                  d.get("description"))
                
                i.set_details(details)
                i.sg_data = d
                if d.get("image"):
                    i.set_thumbnail(d.get("image"))

                # is this previous selection?
                if previous_selection:
                    if previous_selection["type"] == d["type"] and previous_selection["id"] == d["id"]:
                        prev_selection_item = i
        
        # once the list is completely built, select prev item if there is one.
        if prev_selection_item:
            self.select(prev_selection_item)
            
            
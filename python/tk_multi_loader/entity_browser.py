"""
Copyright (c) 2012 Shotgun Software, Inc
----------------------------------------------------
"""
import tank
import os
import sys
import threading

from PySide import QtCore, QtGui

browser_widget = tank.platform.import_framework("tk-framework-widget", "browser_widget")

class EntityBrowserWidget(browser_widget.BrowserWidget):

    
    def __init__(self, parent=None):
        browser_widget.BrowserWidget.__init__(self, parent)
        self.__show_only_current = False

    def get_data(self, data):
            
        previous_selection = data["prev_selection"]
            
            
        entity_cfg = self._app.get_setting("sg_entity_types", {})
        # example: {"Shot": [["desc", "startswith", "foo"]] }        
        types_to_load = entity_cfg.keys()
                    
        sg_data = []

        # load all entities
        for et in types_to_load:
            # only load the context entity type if show only current is checked
            if self.__show_only_current and (et != self._app.context.entity["type"]):
                continue

            item = {}
            item["type"] = et
            
            filters = []
            # add any custom filters
            filters.extend(entity_cfg[et])

            # and limit results to current is show only current is checked
            if self.__show_only_current:
                filters.append(["id", "is", self._app.context.entity["id"]])

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
            i = self.add_item(browser_widget.ListHeader)
            i.set_title("%ss" % item["type"])
            for d in item["data"]:
                i = self.add_item(browser_widget.ListItem)
                
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
            
    def set_show_only_current(self, value):
        self.__show_only_current = value


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


class PublishBrowserWidget(browser_widget.BrowserWidget):
    """
    Middle pane
    """
    
    def __init__(self, parent=None):
        browser_widget.BrowserWidget.__init__(self, parent)        

    def get_data(self, data):
            
        sg_data = []
        current_entity = data["entity"]

        types_to_load = self._app.get_setting("tank_types", [])
        filters = self._app.get_setting("publish_filters", [])

        # resolve any template fields in the filters:
        filters = self._app.resolve_filter_template_fields(filters)

        # always limit to project and entity:
        filters.extend([["entity", "is", current_entity]])             
        
        order_by = [{"field_name": "name", "direction": "asc"},
                    {"field_name": "version_number", "direction": "desc"}]
        
        fields = [ "description", 
                   "version_number", 
                   "created_by",
                   "image", 
                   "entity",
                   "created_at",
                   "tank_type",
                   "name"]
        
        if len(types_to_load) == 0:
            # get all publishes for this entity
            data = self._app.shotgun.find("TankPublishedFile", filters, fields, order_by)
                        
            # now group this into sections based on the tank type
            tank_type_dict = {}
            for d in data:
                tank_type_link = d.get("tank_type")
                if tank_type_link is None:
                    tank_type = "No type associated"
                else:
                    tank_type = tank_type_link.get("name")
                if tank_type not in tank_type_dict:
                    tank_type_dict[tank_type] = []
                tank_type_dict[tank_type].append(d)
             
            # and attach the raw data to the output
            for tank_type in tank_type_dict:
                item = {}
                item["type"] = tank_type
                item["raw_data"] = tank_type_dict[tank_type]
                sg_data.append(item)
            
            
            
        else:
            # get list of specific tank types            
            for tank_type in types_to_load:            
                item = {}
                item["type"] = tank_type
                tank_type_entity = self._app.shotgun.find_one("TankType", 
                                                              [["code", "is", tank_type],
                                                               ["project", "is", self._app.context.project]],
                                                              ["code", "id"])
                if tank_type_entity is None:
                    # unknown tank type!
                    item["raw_data"] = []
                else:
                    extended_filters = filters + [["tank_type", "is", tank_type_entity ]]
                    item["raw_data"] = self._app.shotgun.find("TankPublishedFile", extended_filters, fields, order_by)
                sg_data.append(item)
            
        if self._app.get_setting("dependency_mode"):
            # in dependency mode, the right most column will show file contents.
            # in the middle column, show all versions
            for item in sg_data:
                
                # the data list to display matches the raw dump of all versions
                # we got from shtogun
                item["data"] = item["raw_data"]
        
        else:
            # this is std mode
            # post process the list - we just want one item per "publish group"
            for item in sg_data:
                    
                # now group these into chunks based on their name
                groups = {}
                for d in item["raw_data"]:
                    name = str(d["name"]) # to handle None
                    if name not in groups:
                        groups[name] = []
                    groups[name].append(d)  
                
                # now choose one item out of each group - pick the one
                # with the highest version number
    
                # now get list of items, pick one item per group, using max()
                item["data"] = [max(d, key=lambda x:x["version_number"]) for d in groups.values()]

        
        # pass on the list to the result processor 
        return {"sg_data": sg_data }


    def process_result(self, result):

        sg_data = result.get("sg_data")

        # first check if we have results at all
        results = 0
        for item in sg_data:
            results += len(item["data"])
        if results == 0:
            self.set_message("Sorry, no publishes found!")
            return

        for item in sg_data:
            i = self.add_item(browser_widget.ListHeader)
            i.set_title(item["type"])
            for d in item["data"]:
                i = self.add_item(browser_widget.ListItem)
                
                desc = "No Comments"
                if d.get("description") is not None:
                     desc = d.get("description")
                
                if self._app.get_setting("dependency_mode"):
                    
                    # snow name and version
                    details = ("<b>%s v%s</b><br>"
                               "<small><i>%s, %s</i></small><br>"
                               "%s" % (d.get("name"), 
                                       d.get("version_number"),
                                       d.get("created_by", {}).get("name"),
                                       d.get("created_at"), 
                                       desc))
                
                else:
                
                    # show just version
                    details = ("<b>%s</b><br>"
                               "<small><i>Latest publish %s</i></small><br>"
                               "Latest change: %s" % (d.get("name"), d.get("created_at"), desc))
                
                i.set_details(details)
                i.sg_data = d
                if d.get("image"):
                    i.set_thumbnail(d.get("image"))                

        
        

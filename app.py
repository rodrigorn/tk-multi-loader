"""
Copyright (c) 2012 Shotgun Software, Inc
----------------------------------------------------

A loader application that lets you add new items to the scene.

"""

import tank
import sys
import os

class MultiLoader(tank.platform.Application):
    
    def init_app(self):
        """
        Called as the application is being initialized
        """
        import tk_multi_loader
        self.app_handler = tk_multi_loader.AppHandler(self)
        
        menu_caption = self.get_setting("menu_name")
        
        # add stuff to main menu
        self.engine.register_command(menu_caption, self.app_handler.show_dialog)



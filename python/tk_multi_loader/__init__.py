"""
Copyright (c) 2012 Shotgun Software, Inc
----------------------------------------------------

"""

def show_dialog(app):
    # defer imports so that the app works gracefully in batch modes
    from .dialog import AppDialog
    ui_title = app.get_setting("title_name")
    app.engine.show_dialog(ui_title, app, AppDialog, app)
    
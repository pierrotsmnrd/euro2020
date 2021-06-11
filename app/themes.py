import param

from panel.template.theme import Theme
from bokeh.themes import DARK_MINIMAL

class DarkTheme(Theme):
    """
    The DarkTheme provides a dark color palette
    """

    bokeh_theme = param.ClassSelector(class_=(Theme, str), default=DARK_MINIMAL)

class MaterialDarkTheme(DarkTheme):

    # css = param.Filename() Here we could declare some custom CSS to apply
    
    # This tells Panel to use this implementation
    _template = pn.template.MaterialTemplate
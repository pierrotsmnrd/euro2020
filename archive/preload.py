
from datetime import datetime as dt
from threading import main_thread
from bokeh.models.layouts import Column, Spacer
from holoviews.core.util import one_to_one

import random 
import pandas as pd
import numpy as np

from pprint import pprint

import panel as pn
import hvplot.pandas  # noqa
import holoviews as hv
from bokeh.models import HoverTool
import param

import i18n
from i18n import _
from menu import menu

from panel.template import DefaultTheme

from pdb import set_trace as bp


pd.options.plotting.backend = 'holoviews'



from panel.template import DarkTheme






class PreloadPage(param.Parameterized):

    def __init__(self, ** params):

        super(PreloadPage, self).__init__(**params)

    
    def view(self):
        return pn.pane.HTML('''
<script type="text/javascript">
        var fontLoader = new FontLoader(["noto"], {
            "fontLoaded": function(font) {
                // One of the fonts was loaded
                console.log("font loaded: " + font.family);
            },
            "complete": function(error) {
                if (error !== null) {
                    // Reached the timeout but not all fonts were loaded
                    console.log(error.message);
                    console.log(error.notLoadedFonts);
                } else {
                    // All fonts were loaded
                    console.log("all fonts were loaded");
                    location.href = "/?go";
                }
            }
        }, 3000);
        fontLoader.loadFonts();
    </script>
    
         
         ''')

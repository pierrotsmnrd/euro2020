
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
from pages.menu import menu
from blocks.common import uses_shitdows
from panel.template import DefaultTheme

from pdb import set_trace as bp


pd.options.plotting.backend = 'holoviews'



from panel.template import DarkTheme




class TestPage(param.Parameterized):

    languages_dict = { 'fr':'🇫🇷', 'en':'🇬🇧/🇺🇸'}
    selected_flag = param.ObjectSelector(objects=list(languages_dict.values()), 
                                         default=languages_dict['en'])

    lang_id = param.ObjectSelector(objects=list(languages_dict.keys()), 
                                         default='en')

    theme = param.ObjectSelector(default="dark", objects=['light', 'dark'])

    def __init__(self, lang_id, theme='dark', go=True, ** params):

        super(TestPage, self).__init__(**params)

        # Params widgets
        self.theme = theme
        
        self.lang_id = lang_id

        self.go = go

        self.flag_selector = pn.widgets.Select.from_param(
            self.param.selected_flag,
            name="", #_('Language'),
            value=self.languages_dict[lang_id],
            width=80,
            css_classes=[ 'fix_shitdows'] if uses_shitdows() else []
            )

        self.flag_selector_watcher = self.flag_selector.param.watch(self.update_lang_id, ['value'], onlychanged=False)


       
    def update_lang_id(self, event):
        #print(self.selected_flag, flush=True)
        new_lang_id = dict((v,k) for k,v in self.languages_dict.items())[self.selected_flag]
        
        print("%s -> %s"%(self.lang_id, new_lang_id) , flush=True)

        i18n.set_lang_id(new_lang_id)
        self.lang_id = new_lang_id
        
        
    @param.depends("lang_id")
    def menu(self):
        return menu('about')


    @param.depends("lang_id")
    def header(self):
        return  pn.Row(pn.layout.spacer.HSpacer(),
                        pn.Row( pn.pane.Markdown(_("last_update") ),
                               
                                pn.Column(pn.layout.spacer.VSpacer(height=1), 
                                         self.flag_selector) , 

                                #self.theme_selector, 
                                
                                width=400)
                     )




    def fix_flags_hook(self, plot, element):
        plot.handles['yaxis'].major_label_text_font = "noto"
        
    def main_stuff(self):

        data = {
        'AUT 🇦🇹':  { f"_{i}" :  random.randint(0,99) for i in range(10) }   ,
        'BEL 🇧🇪':  { f"_{i}" :  random.randint(0,99) for i in range(10) }   ,
        'CRO 🇭🇷':  { f"_{i}" :  random.randint(0,99) for i in range(10) }   ,
        'CZE 🇨🇿':  { f"_{i}" :  random.randint(0,99) for i in range(10) }   ,
        'DEN 🇩🇰':  { f"_{i}" :  random.randint(0,99) for i in range(10) }   ,
        'ENG 🏴󠁧󠁢󠁥󠁮󠁧󠁿':  { f"_{i}" :  random.randint(0,99) for i in range(10) }   ,
        'ESP 🇪🇸':  { f"_{i}" :  random.randint(0,99) for i in range(10) }   ,
        'FIN 🇫🇮':  { f"_{i}" :  random.randint(0,99) for i in range(10) }   ,
        'FRA 🇫🇷':  { f"_{i}" :  random.randint(0,99) for i in range(10) }   ,
        'GER 🇩🇪':  { f"_{i}" :  random.randint(0,99) for i in range(10) }   ,
        'HUN 🇭🇺':  { f"_{i}" :  random.randint(0,99) for i in range(10) }   ,
        'ITA 🇮🇹':  { f"_{i}" :  random.randint(0,99) for i in range(10) }   ,
        'MKD 🇲🇰':  { f"_{i}" :  random.randint(0,99) for i in range(10) }   ,
        'NED 🇳🇱':  { f"_{i}" :  random.randint(0,99) for i in range(10) }   ,
        'POL 🇵🇱':  { f"_{i}" :  random.randint(0,99) for i in range(10) }   ,
        'POR 🇵🇹':  { f"_{i}" :  random.randint(0,99) for i in range(10) }   ,
        'RUS 🇷🇺':  { f"_{i}" :  random.randint(0,99) for i in range(10) }   ,
        'SCO 🏴󠁧󠁢󠁳󠁣󠁴󠁿':  { f"_{i}" :  random.randint(0,99) for i in range(10) }   ,
        'SUI 🇨🇭':  { f"_{i}" :  random.randint(0,99) for i in range(10) }   ,
        'SVK 🇸🇰':  { f"_{i}" :  random.randint(0,99) for i in range(10) }   ,
        'SWE 🇸🇪':  { f"_{i}" :  random.randint(0,99) for i in range(10) }   ,
        'TUR 🇹🇷':  { f"_{i}" :  random.randint(0,99) for i in range(10) }   ,
        'UKR 🇺🇦':  { f"_{i}" :  random.randint(0,99) for i in range(10) }   ,
        'WAL 🏴󠁧󠁢󠁷󠁬󠁳󠁿':  { f"_{i}" :  random.randint(0,99) for i in range(10) }   ,
        }

        df = pd.DataFrame(data)
        
        # pn.pane.HTML('''<span style="font-size:42pt;">🇸🇪</span><br />'''),
        # pn.pane.HTML('''<span style="font-family:'noto';font-size:42pt;">🇸🇪</span><br />'''),
        # pn.pane.HTML('''<span style="font-family:'opensans';font-size:42pt;">🇸🇪</span><br />'''),

        return pn.Column(  
pn.pane.HTML('''<br /><br />'''),
                        df.hvplot.barh(height=500, 
                        stacked=True)\
                            .opts(show_legend=False, 
                            hooks=[self.fix_flags_hook]
                            )\
                            .redim.values(index=list(data.keys()))
                            
                    )



    
    def main_view(self):
        
        if self.theme =='light':
            theme = pn.template.MaterialTemplate(title=_("main_title") , )
        else:
            theme = pn.template.MaterialTemplate(title=_("main_title")  , 
                                                theme=DarkTheme,
                                                #main_max_width="1200px"
                                                )


        theme.header.append(self.header)
        theme.sidebar.append(self.menu)

        theme.main.append(self.main_stuff)
        
        theme.main.append(pn.Spacer(height=30))

        if not self.go:
            theme.main.append(pn.pane.HTML('''
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
                    location.href = "/cacaprout?go";
                }
            }
        }, 3000);
        fontLoader.loadFonts();
    </script>
    
         
         '''))

        return theme


    def view(self):
        return self.main_view()
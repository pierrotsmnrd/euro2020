
from datetime import datetime as dt
from threading import main_thread
from bokeh.models.layouts import Column, Spacer
from holoviews.core.util import one_to_one

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




class AboutPage(param.Parameterized):

    languages_dict = { 'fr':'🇫🇷', 'en':'🇬🇧/🇺🇸'}
    selected_flag = param.ObjectSelector(objects=list(languages_dict.values()), 
                                         default=languages_dict['en'])

    lang_id = param.ObjectSelector(objects=list(languages_dict.keys()), 
                                         default='en')

    theme = param.ObjectSelector(default="dark", objects=['light', 'dark'])

    def __init__(self, lang_id, theme='dark', ** params):

        super(AboutPage, self).__init__(**params)

        # Params widgets
        self.theme = theme
        
        self.lang_id = lang_id

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


    @param.depends("lang_id", "theme")
    def main_chapter(self):

        filepath = '../i18n/about_%s.md'%(self.lang_id)
        f = open(filepath, 'r')
        content = f.read()

        return  pn.pane.Markdown(content, sizing_mode='stretch_width')
        
        

    @param.depends("lang_id")
    def header(self):
        return  pn.Row(pn.layout.spacer.HSpacer(),
                        pn.Row( pn.pane.Markdown(_("last_update") ),
                               
                                pn.Column(pn.layout.spacer.VSpacer(height=1), 
                                         self.flag_selector) , 

                                #self.theme_selector, 
                                
                                width=400)
                     )


    
    def main_view(self):
        
        if self.theme =='light':
            theme = pn.template.MaterialTemplate(title="UEFA Euro 2020" , )
        else:
            theme = pn.template.MaterialTemplate(title="UEFA Euro 2020"  , 
                                                theme=DarkTheme,
                                                #main_max_width="1200px"
                                                )


        theme.header.append(self.header)
        theme.sidebar.append(self.menu)
        theme.main.append(self.main_chapter)
        
        theme.main.append(pn.Spacer(height=30))

        theme.sidebar.append(pn.pane.HTML('''<script>
         document.getElementById('sidebar').classList.remove('mdc-drawer--open') 
         </script>'''))

        return theme


    def view(self):
        return self.main_view()
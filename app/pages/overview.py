
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
from panel.pane.markup import Markdown
import param

import i18n
from i18n import _
from pages.menu import menu

from panel.template import DefaultTheme

from pdb import set_trace as bp


pd.options.plotting.backend = 'holoviews'


from panel.template import DarkTheme


import blocks
from blocks.common import br

class OverviewPage(param.Parameterized):

    languages_dict = { 'fr':'🇫🇷', 'en':'🇬🇧/🇺🇸'}
    selected_flag = param.ObjectSelector(objects=list(languages_dict.values()), 
                                         default=languages_dict['en'])

    lang_id = param.ObjectSelector(objects=list(languages_dict.keys()), 
                                         default='en')

    theme = param.ObjectSelector(default="dark", objects=['light', 'dark'])

    def __init__(self, full_df,  lang_id, theme='dark', ** params):

        super(OverviewPage, self).__init__(**params)

        self.full_df = full_df

        # Params widgets

        
        
        self.lang_id = lang_id

        self.flag_selector = pn.widgets.Select.from_param(
            self.param.selected_flag,
            name="", #_('Language'),
            value=self.languages_dict[lang_id],
            width=80
            )

        self.flag_selector_watcher = self.flag_selector.param.watch(self.update_lang_id, ['value'], onlychanged=False)

        # self.flag_selector.jscallback(value='''
        #     window.location = location.href.split("?")[0] + "?lg=" + languages_dict[select.value] 
        # ''', args={"select": self.flag_selector,
        #            "languages_dict": {v: k for (k, v) in languages_dict.items()}
        #            }
        # )



        self.theme_selector = pn.widgets.Select.from_param(
            self.param.theme,
            name='Display mode',
            value=theme, 
            width=80
        )

    def update_lang_id(self, event):
        #print(self.selected_flag, flush=True)
        new_lang_id = dict((v,k) for k,v in self.languages_dict.items())[self.selected_flag]
        
        print("%s -> %s"%(self.lang_id, new_lang_id) , flush=True)

        i18n.set_lang_id(new_lang_id)
        self.lang_id = new_lang_id
        
        
    @param.depends("lang_id")
    def test_markdown(self):
        return pn.pane.Markdown(f" ** this is a test in _markdown_ ** : {self.lang_id} {self.selected_flag}  {self.theme}")


    @param.depends("lang_id")
    def menu(self):
        return menu('overview')



    @param.depends("lang_id", "theme")
    def teams_chapter(self):
        
        result = pn.Column( 
                    pn.layout.spacer.VSpacer(height=15),
                    pn.Row(
                            pn.pane.PNG('https://upload.wikimedia.org/wikipedia/fr/3/32/UEFA_Euro_2020_logo.png', width=150),
                            pn.layout.spacer.Spacer(width=1),
                            br(2),
                            pn.pane.Markdown(f'''## {_('title_overview')} 

{_('intro_overview')}
''', sizing_mode='stretch_width', min_height=200),

                            
                            
                        ),
                        #pn.layout.spacer.Spacer(height=1),
                        sizing_mode='stretch_width',
            )
                    
        return pn.Row(result,  sizing_mode='stretch_width')

    @param.depends("lang_id", "theme")
    def players_chapter(self):

        items = []


        items += blocks.positions_distribution.items(self.full_df, self.theme)
        # items += blocks.countries_local_leagues.items(self.full_df, self.theme)
        # items+= blocks.leagues_distribution_per_team.items(self.full_df, self.theme)
        # items+= blocks.leagues_distribution.items(self.full_df, self.theme)
        # items+= blocks.countries_clubs.items(self.full_df, self.theme)
        # items+= blocks.clubs_distribution.items(self.full_df, self.theme)
        # items+= blocks.clubs_distribution_per_team.items(self.full_df, self.theme)
        # items+= blocks.players_max_selections_per_country.items(self.full_df, self.theme)
        # items+= blocks.players_age_nbr_selections.items(self.full_df, self.theme)
        # items+= blocks.summed_selections_per_country.items(self.full_df, self.theme)


       
        items += [
           
            br(3),
            pn.layout.Divider(),
            pn.Row(pn.Spacer(width=50), 
                
                pn.Column(
                    pn.pane.Markdown(i18n.explanations(f'overview_footer'), sizing_mode='stretch_width'),
                    br(), 
                    
                    sizing_mode='stretch_width'
                )
                
                , sizing_mode='stretch_width'
            )               
        ]

        result = pn.Column(objects=items, sizing_mode='stretch_width')
        return result
       


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

        #theme = pn.template.BootstrapTemplate(theme=DarkTheme)

        theme.header.append(self.header)

        
        theme.sidebar.append(self.menu)

        #theme.main.append(self.test_markdown)
        theme.main.append(self.teams_chapter)
        theme.main.append(self.players_chapter)
          
        theme.main.append(pn.Spacer(height=30))

        theme.sidebar.append(pn.pane.HTML('''<script>
         document.getElementById('sidebar').classList.remove('mdc-drawer--open') 
         </script>'''))

       
        return theme


    def view(self):
        return self.main_view()
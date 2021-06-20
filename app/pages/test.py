
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
from blocks.common import uses_shitdows

from panel.template import DefaultTheme

from pdb import set_trace as bp


pd.options.plotting.backend = 'holoviews'


from panel.template import DarkTheme


import blocks
from blocks.common import br

class TestPage(param.Parameterized):

    received_gotit = param.Boolean(default=False)

    languages_dict = { 'fr':'🇫🇷', 'en':'🇬🇧/🇺🇸'}
    selected_flag = param.ObjectSelector(objects=list(languages_dict.values()), 
                                         default=languages_dict['en'])

    lang_id = param.ObjectSelector(objects=list(languages_dict.keys()), 
                                         default='en')

    theme = param.ObjectSelector(default="dark", objects=['light', 'dark'])

    def __init__(self, full_df, lang_id, theme='dark', ** params):

        super(TestPage, self).__init__(**params)

        self.full_df = full_df

        # Params widgets

        self.lang_id = lang_id

        self.flag_selector = pn.widgets.Select.from_param(
            self.param.selected_flag,
            name="", #_('Language'),
            value=self.languages_dict[lang_id],
            width=80,
            css_classes=[ 'fix_shitdows'] if uses_shitdows() else []
            )

        self.flag_selector_watcher = self.flag_selector.param.watch(self.update_lang_id, ['value'], 
                                        onlychanged=False,

        )

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
        return menu('test')



    @param.depends("lang_id", "theme", "received_gotit")
    def teams_chapter(self):
        
        gspec = pn.GridSpec(  sizing_mode='stretch_width', 
                              height=80, 
                              
                                )

        
        gspec[0  , : ] = pn.Column( pn.pane.Markdown(f'''## Test page '''),  )


        if not self.received_gotit:

            checkbox =  pn.widgets.Checkbox.from_param(self.param.received_gotit, 
                                name="gotit",
                                css_classes=['gotit-hide']
                            )


            trigger_on_fonts_loaded = pn.pane.HTML(''' <script> 
                                            
                                var fired = false;

                                var fontLoader = new FontLoader(["babelstone"], {
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

                                            if ( !fired) {

                                                Array.from(document.getElementsByTagName('input')).forEach(function(item) {
                                                    if (item.nextSibling.innerHTML == 'gotit' ){
                                                        item.click()
                                                        item.remove();
                                                        fired = true;
                                                    }
                                                });


                                            }
                                            

                                        }
                                    }
                                }, 10000);
                                fontLoader.loadFonts();
                                            
                                            
                                            </script>''' )

        
            gspec[1   , :] = pn.Row( pn.pane.HTML( width=100, height=100, loading=True),
                            checkbox, 
                            trigger_on_fonts_loaded,
                            
                    )
            
            return gspec
             

        return gspec
    

    @param.depends("lang_id", "theme", "received_gotit")
    def players_chapter(self):

        if not self.received_gotit:
            #print("Chapter -> NOT got it ... ")
            return pn.pane.HTML("")
        

        items = []

        countries_local_leagues = blocks.countries_local_leagues.CountriesLocalLeagues(self.full_df, self.theme)
        items+= [  br(2), countries_local_leagues.render ]

        leagues_distribution_per_team = blocks.leagues_distribution_per_team.LeaguesDistributionPerTeam(self.full_df, self.theme)
        items+= [ br(), leagues_distribution_per_team.render]

        leagues_distribution = blocks.leagues_distribution.LeaguesDistribution(self.full_df, self.theme)
        items += [ leagues_distribution.render ]

        countries_clubs = blocks.countries_clubs.ConutriesClubs(self.full_df, self.theme)
        items+= [ br(), countries_clubs.render ]

        clubs_distribution = blocks.clubs_distribution.ClubsDistribution(self.full_df, self.theme)
        items += [ clubs_distribution.render ]

        # # Sankey, flags to fix on Windows
        clubs_distribution_per_team = blocks.clubs_distribution_per_team.ClubsDistributionPerTeam(self.full_df, self.theme) 
        items += [ clubs_distribution_per_team.render ]

        # flags to fix on Windows
        players_max_selections_per_country = blocks.players_max_selections_per_country.PlayersMaxSelectionsPerCountry(self.full_df, self.theme) 
        items += [ br(2), players_max_selections_per_country.render ]

        players_age_nbr_selections = blocks.players_age_nbr_selections.PlayersAgeNbrSelections(self.full_df, self.theme)
        items += [ players_age_nbr_selections.render ]

        summed_selections_per_country = blocks.summed_selections_per_country.SummedSelectionsPerCountry(self.full_df, self.theme)
        items += [ summed_selections_per_country.render ]


        

        # items += [
        
        #     br(3),
        #     pn.layout.Divider(),
        #     pn.Row(pn.Spacer(width=50), 
                
        #         pn.Column(
        #             pn.pane.Markdown(i18n.explanations(f'overview_footer'), sizing_mode='stretch_width'),
        #             br(), 
                    
        #             sizing_mode='stretch_width'
        #         )
                
        #         , sizing_mode='stretch_width'
        #     )               
        # ]

        result = pn.Column(objects=items, sizing_mode='stretch_width')
        return result
    


    @param.depends("lang_id", "received_gotit")
    def header(self):

        if not self.received_gotit:
            return  pn.Row(pn.layout.spacer.HSpacer(),
                            pn.Row( pn.pane.Markdown(_("last_update") ),
                                 pn.Column(pn.layout.spacer.VSpacer(height=1), 
                         ) , 
                                    width=400)
                        )

        
        return  pn.Row(pn.layout.spacer.HSpacer(),
                        pn.Row( pn.pane.Markdown(_("last_update") ),
                                pn.Column(pn.layout.spacer.VSpacer(height=1), 
                                        self.flag_selector) , 

                                width=400)
                    )



    
    def view(self):
          
        if self.theme =='light':
            theme = pn.template.MaterialTemplate(title=_("main_title")  )
        else:
            theme = pn.template.MaterialTemplate(title=_("main_title") , 
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
        
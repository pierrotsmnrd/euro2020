
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
from menu import menu

from panel.template import DefaultTheme

from pdb import set_trace as bp


pd.options.plotting.backend = 'holoviews'


from panel.template import DarkTheme

from plots import *
from explanations import *


# helper
def br(n=1):
    return pn.pane.HTML("<br />"*n) 


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

        #bla = pn.pane.Markdown(''' blablablablabla blablablablablabla bla bla bla bla bla   
        #                        ''' * 20, sizing_mode='stretch_width'
        #                        )

        
        items = [   pn.pane.Markdown(f'''## {_('positions_distribution_title')} '''),
                    pn.pane.Markdown(_('intro_positions_distribution'), ),

                    pn.Row(pn.Spacer(width=50),
                        positions_distribution(self.full_df, self.lang_id, self.theme),
                        positions_distribution_txt()
                    )
                ]


        items += [
            br(3),
            pn.pane.Markdown(f'''### {_('countries_local_leagues_title')} '''),
                # Seulement 5 teams over 24 have more than 50% of their players coming from their own league
            pn.Row(pn.Spacer(width=50), 
                    pn.pane.Markdown(f''' {_('countries_local_leagues_subtitle')} ''', 
                    sizing_mode='stretch_width'),
            ),
            pn.Row(pn.Spacer(width=50),
                countries_local_leagues_txt(),
                countries_local_leagues(self.full_df, self.lang_id, self.theme),
             
            ),
            br(2),
            pn.pane.Markdown(f''' {_('countries_local_leagues_footer')}  '''),
           
        ]


        items += [
            br(),
            
            pn.pane.Markdown(f'''### {_('leagues_distribution_per_team_title')} '''),
            pn.Row(pn.Spacer(width=50), 
                    pn.pane.Markdown(f'''{_('leagues_distribution_per_team_subtitle')} ''',
                    sizing_mode='stretch_width',
                    height=50),                    
            ),
            pn.Row(
                leagues_distribution_per_team(self.full_df, self.lang_id, self.theme),
                leagues_distribution_per_team_txt()
            ),

            br(),
            pn.pane.Markdown(f'''{_('leagues_distribution_title')} '''),
            pn.Row(
                pn.Spacer(width=50), 
                leagues_distribution_txt(),
                leagues_distribution(self.full_df, self.theme),
                
            )
        ]

        items += [
            br(3),
            pn.pane.Markdown(f'''### {_('countries_clubs_title')} '''),

            pn.Row(pn.Spacer(width=50), 
                    pn.pane.Markdown(f''' {_('countries_clubs_subtitle')} ''', sizing_mode='stretch_width'),
                    
            ),
            pn.Row(pn.Spacer(width=50),
                pn.Column(countries_clubs(self.full_df, self.lang_id, self.theme),
                countries_clubs_txt())
            ),
            
            br(),
            pn.pane.Markdown(f'''{_('clubs_distribution_title')} '''),
            pn.Row(pn.Spacer(width=50),
                clubs_distribution_txt(),
                clubs_distribution(self.full_df, self.theme)
            )
        ]


        items += [
            br(3),
            pn.Row(pn.Spacer(width=50), 
                    pn.pane.Markdown(f''' {_('sankey_title')} ''')
            ),
            pn.Row(pn.Spacer(width=50),
                sankey_ui(self.full_df, self.lang_id, self.theme)
            )

        ]


        items += [
           
            br(3),
            pn.Row(pn.Spacer(width=50), 
                
                pn.Column(
                    pn.pane.Markdown(f'''## {_('selections_title')} '''),
                    br(),
                    pn.pane.Markdown(f''' {_('selections_subtitle_1')} ''', sizing_mode='stretch_width'),
                    br(),
                    pn.Row(players_max_selections_per_country_txt("max"), players_max_selections_per_country(self.full_df,  self.theme)),
                    
                    br(),
                    pn.pane.Markdown(f''' {_('selections_subtitle_2')} ''', sizing_mode='stretch_width'),
                    
                    pn.Row(players_age_nbr_selections_ui(self.full_df,  self.theme, dim="nbr_selections" ), 
                        
                        pn.Column(
                                br(3),
                                players_max_selections_per_country_txt("all")
                                )
                        
                        
                        ),
                    
                    br(2),
                    pn.pane.Markdown(f''' {_('selections_subtitle_3')} ''', sizing_mode='stretch_width'),
                    br(),
                    summed_selections_per_country(self.full_df, self.theme),
                    br(),
                    pn.pane.Markdown(f''' {_('selections_conclusion')} ''', sizing_mode='stretch_width'),

                    

                )
            ),
           
        ]



        items += [
           
            br(3),
            pn.layout.Divider(),
            pn.Row(pn.Spacer(width=50), 
                
                pn.Column(
                    overview_footer(),
                    br(), 
                    
                    sizing_mode='stretch_width'
                )
                
                , sizing_mode='stretch_width'
            )               
        ]


        result = pn.Column(objects=items, sizing_mode='stretch_width')

        return result

        #------------

        #players_selections_title
        #players_selections_subtitle


        items += [
            br(3),
            pn.pane.Markdown(f'''### {_('players_selections_title')} '''),

            pn.Row(pn.Spacer(width=50), 
                    pn.pane.Markdown(f''' {_('players_selections_subtitle')} ''', sizing_mode='stretch_width'),
                    
            ),
            
           
            pn.Tabs( 
                    ('All championships', pn.Row(  players_age_nbr_selections(self.full_df,  self.theme, dim="nbr_selections" ),
                                                  players_age_nbr_selections_txt("total")
                                    ) 
                    ),
                    ('UEFA Euro', pn.Row(  players_age_nbr_selections(self.full_df,  self.theme, dim="nbr_selections_euro"),
                                            players_age_nbr_selections_txt("euro")
                                    ) 
                    ),
                    ('FIFA World Cup', pn.Row(  players_age_nbr_selections(self.full_df,  self.theme, dim="nbr_selections_wcup"),
                                                 players_age_nbr_selections_txt("worldcup")
                                        ) 
                    ),
                    tabs_location='left'             
                )
        
        
           ]



        #------------

        items += [
            br(3),
            pn.pane.Markdown(f'''### {_('title_players_funfacts')}'''),

             pn.Row(pn.Spacer(width=50), 
                    pn.pane.Markdown(f'''Le physique des joueurs varient beaucoup d'un poste à l'autre. Regardons la répartition du poids et des taille selon leur position''')
            ),
            pn.Row(pn.Spacer(width=50),
                pn.Tabs( 
                    ('per country', pn.Row(players_height_weight_per_country(self.full_df, self.lang_id, self.theme))),
                    ('per position', pn.Row(players_height_weight(self.full_df, self.lang_id, self.theme) )),
                 tabs_location='left'
                )
            ),

            pn.Row(pn.Spacer(width=50), 
                    pn.pane.Markdown(f''' Nbr selections ''')
            ),
            pn.Row(pn.Spacer(width=50),
            #  pn.Tabs( 
            #         ('Total', players_age_nbr_selections(self.full_df, self.lang_id, self.theme, dim="nbr_selections" ) ),
            #         ('Euro', players_age_nbr_selections(self.full_df, self.lang_id, self.theme, dim="nbr_selections_euro") ),
            #         ('World Cup', players_age_nbr_selections(self.full_df, self.lang_id, self.theme, dim="nbr_selections_wcup") ),
                    
            #      tabs_location='left'
            #     )
            )
            
        ]




        items += [
            br(3),
            pn.pane.Markdown(f'''### {_('title_players_funfacts')}'''),

             pn.Row(pn.Spacer(width=50), 
                    pn.pane.Markdown(f'''Le physique des joueurs varient beaucoup d'un poste à l'autre. Regardons la répartition du poids et des taille selon leur position''')
            ),
            pn.Row(
                pn.Tabs( 
                    ('age',    pn.Row(players_dim_per_country_per_position(self.full_df, self.lang_id, self.theme, 'age'))),
                    ('height', pn.Row(players_dim_per_country_per_position(self.full_df, self.lang_id, self.theme, 'height') )),
                    ('weight', pn.Row(players_dim_per_country_per_position(self.full_df, self.lang_id, self.theme, 'weight') )),
                    ('selections', pn.Row(players_dim_per_country_per_position(self.full_df, self.lang_id, self.theme, 'nbr_selections') )),
                    
                 tabs_location='left'
                )
            ),
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
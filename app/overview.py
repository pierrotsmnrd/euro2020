from datetime import datetime as dt
from threading import main_thread

import pandas as pd
import numpy as np

from pprint import pprint

import panel as pn
import hvplot.pandas  # noqa
import holoviews as hv
from bokeh.models import HoverTool
import param

from i18n import _
from panel.template import DefaultTheme

from pdb import set_trace as bp


pd.options.plotting.backend = 'holoviews'
#pn.config.sizing_mode = 'stretch_width'


from panel.template import DarkTheme

from plots import *

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
            name=_('Language'),
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
        print(self.selected_flag, flush=True)
        self.lang_id = dict((v,k) for k,v in self.languages_dict.items())[self.selected_flag]
        print(self.lang_id, flush=True)
        
    @param.depends("lang_id")
    def test_markdown(self):
        return pn.pane.Markdown(f" ** this is a test in _markdown_ ** : {self.lang_id} {self.selected_flag}  {self.theme}")

    @param.depends("lang_id")
    def menu(self):

        # return pn.pane.HTML("""<a href='/overview'>Overview</a><br />
        # <a href='/page2'>Page 2</a><br />
        # <a href='/page3'>Page 3</a><br />
        # """)

        # result = pn.Column(
        #         pn.widgets.Button(name='Overview', button_type='primary', color='red'),
        #         pn.widgets.Button(name='Page 2 ', button_type='primary', color='red'),
        #         pn.widgets.Button(name='Page 3', button_type='primary', color='red'),                                
        # )

        result = pn.pane.HTML('''
      <button class="mdc-button mdc-button--outlined">
        <span class="mdc-button__ripple"></span>
            <i class="material-icons mdc-button__icon" aria-hidden="true">bookmark</i>
        <span class="mdc-button__label">Overview</span>
        </button>
''')

        return result



    @param.depends("lang_id", "theme")
    def teams_chapter(self):
        if self.lang_id == 'fr':
            title = pn.pane.Markdown('''## Présentation des équipes ''')
        else:
            title = pn.pane.Markdown('''## Teams' presentation ''')

        return pn.Column(title, 
                            pn.pane.Markdown('''TODO '''),
                            pn.pane.Markdown('''TODO '''),
                    )

    @param.depends("lang_id", "theme")
    def players_chapter(self):

        bla = pn.pane.Markdown(''' blablablablabla blablablablablabla bla bla bla bla bla   
                                ''' * 20, sizing_mode='stretch_width'
                                )


        items = [  pn.layout.Divider(),
                    pn.pane.Markdown('''## Présentation des Joueurs '''),
                    pn.pane.Markdown('''Each team is allowed to select 26 players.  
The way they have been selected is informative.  
Let's see how each country has built more _offensive_ or _defensive_ teams.'''),
        
                    pn.pane.Markdown(f'''### {_('title_positions_distribution')}'''),
                    pn.Row(pn.Spacer(width=50),
                        positions_distribution(self.full_df, self.lang_id, self.theme),
                        bla
                    )
                ]

        items += [
            pn.pane.HTML("<br />"*3),
            pn.pane.Markdown(f'''### Dans quels championnats évoluent les joueurs sélectionnés ? '''),

            pn.Row(pn.Spacer(width=50), 
                    pn.pane.Markdown(f'''Tout d'abord, regardons **quels pays** ont sélectionné principalement des joueurs **de leur propre ligue** ''')
            ),
            pn.Row(pn.Spacer(width=50),
                countries_local_leagues(self.full_df, self.lang_id, self.theme),
                bla
            )
        ]


        items += [
            pn.pane.HTML("<br />"*3),
            
            pn.Row(pn.Spacer(width=50), 
                    pn.pane.Markdown(f''' Maintenant regardons la répartition des ligues selon les équipes ''')
            ),
            pn.Row(pn.Spacer(width=50),
                leagues_distribution(self.full_df, self.lang_id, self.theme),
                bla
            )
        ]

        items += [
            pn.pane.HTML("<br />"*3),
            pn.pane.Markdown(f'''### Clubs des joueurs sélectionnés ? '''),

            pn.Row(pn.Spacer(width=50), 
                    pn.pane.Markdown(f'''Plus précis que les ligues, regardons dans quels **clubs** les joueurs sélectionnés évoluent''')
            ),
            pn.Row(pn.Spacer(width=50),
                countries_clubs(self.full_df, self.lang_id, self.theme),
                #countries_clubs(self.full_df, self.lang_id, self.theme, False),
            )

        ]


        items += [
            pn.pane.HTML("<br />"*3),
            pn.Row(pn.Spacer(width=50), 
                    pn.pane.Markdown(f'''Pour avoir une meilleure vision de la répartition des clubs, sélectionnez votre équipe préférée''')
            ),
            pn.Row(pn.Spacer(width=50),
                sankey_ui(self.full_df, self.lang_id, self.theme)
            )

        ]


        items += [
            pn.pane.HTML("<br />"*3),
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
        ]

        items += [
            pn.pane.HTML("<br />"*3),
            pn.pane.Markdown(f'''### {_('title_players_funfacts')}'''),

             pn.Row(pn.Spacer(width=50), 
                    pn.pane.Markdown(f'''Le physique des joueurs varient beaucoup d'un poste à l'autre. Regardons la répartition du poids et des taille selon leur position''')
            ),
            pn.Row(
                pn.Tabs( 
                    ('per age',    pn.Row(players_dim_per_country_per_position(self.full_df, self.lang_id, self.theme, 'age'))),
                    ('per height', pn.Row(players_dim_per_country_per_position(self.full_df, self.lang_id, self.theme, 'height') )),
                    ('per weight', pn.Row(players_dim_per_country_per_position(self.full_df, self.lang_id, self.theme, 'weight') )),
                 tabs_location='left'
                )
            ),
        ]

            


        #     pn.pane.HTML("<br />"*3),
        #      pn.Row(pn.Spacer(width=50),
        #         teams_average_age(self.full_df, self.lang_id, self.theme)
        #     )
        
        # ] 
        # - Joueurs : quelque fun facts
        #     -  (06)
        #     - Age (selon le poste ?)
            
        #     - Joueurs qui évoluent ensemble en club et qui s'affronteront en matchs
        #     - Sankey reversed


        result = pn.Column(objects=items)

        return result



    def main_view(self):
        
        if self.theme =='light':
            theme = pn.template.MaterialTemplate(title='Euro 2020', )
        else:
            theme = pn.template.MaterialTemplate(title='Euro 2020', 
                                                theme=DarkTheme,
                                                #main_max_width="1200px"
                                                )

        #theme = pn.template.BootstrapTemplate(theme=DarkTheme)

        theme.header.append(
                pn.Row(pn.layout.spacer.HSpacer(),
                        pn.Row(self.flag_selector, 
                                self.theme_selector, width=400)
                     )
                      
        )

        
        theme.sidebar.append(self.menu)

        theme.main.append(self.test_markdown)
        theme.main.append(self.teams_chapter)
        theme.main.append(self.players_chapter)
          
        theme.main.append(pn.Spacer(height=30))

        theme.sidebar.append(pn.pane.HTML('''<script>
          document.getElementById('sidebar').classList.remove('mdc-drawer--open') 
          </script>'''))

        return theme


    def view(self):
        return self.main_view()
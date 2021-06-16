import panel as pn
from param import Composite
from overview import OverviewPage
from about import AboutPage
from matches import MatchesPage
import pandas as pd
import i18n
import os

from i18n import _
i18n.set_lang_id('en')


root_dname = os.path.dirname(os.path.abspath(__file__))
os.chdir(root_dname)

import holoviews as hv

lang_id = None
full_df = None
selections_df = None

def load_data():

    global full_df
    global selections

    players_df = pd.read_csv("../data/players.csv")
    clubs_df = pd.read_csv("../data/clubs.csv")


    full_df = pd.merge(players_df, 
                    clubs_df,
                    how='left', 
                    on='club_id',
                    suffixes=(None, '_club'))

    # HR like "Human Readable"
    full_df['field_position_hr'] = full_df['field_position'].transform(lambda x:_(x))
    full_df['field_position_color'] = full_df['field_position'].transform(lambda x: i18n.field_positions_colors()[x] )

    full_df['country_name'] = full_df['country_code'].transform(lambda x:_(x, i18n.countries_translations() ) )
    full_df['country_flag'] = full_df['country_code'].transform(lambda x:_(x, i18n.countries_translations() , 'flag') )

    full_df['country_name_club'] = full_df['country_code_club'].transform(lambda x:_(x, i18n.countries_translations() ) )
    full_df['country_flag_club'] = full_df['country_code_club'].transform(lambda x: _(x, i18n.countries_translations() , 'flag') )

    full_df['league_name'] = full_df['country_code_club'].transform(lambda x:"%s %s" %(_(x, i18n.countries_translations(), 'league'), 
                                                                                       _(x, i18n.countries_translations(), 'flag')) )


    full_df['group_hr'] = full_df['group'].transform(lambda x:"%s %s"%(_("dim_group"), x) )


    selections_df = pd.read_csv("../data/selections.csv")

    totals_df = selections_df[ selections_df['competition_name']=='total' ][['id', 'count']].rename(columns={'count':'nbr_selections'})
    full_df = pd.merge(full_df, totals_df, on='id', how='outer')

    totals_df_euro = selections_df[ selections_df['competition_name']=='European Championship' ][['id', 'count']].rename(columns={'count':'nbr_selections_euro'})
    full_df = pd.merge(full_df, totals_df_euro, on='id', how='outer')

    totals_df_wcup = selections_df[ selections_df['competition_name']=='FIFA World Cup' ][['id', 'count']].rename(columns={'count':'nbr_selections_wcup'})
    full_df = pd.merge(full_df, totals_df_wcup, on='id', how='outer')

    totals_df_friendly = selections_df[ selections_df['competition_name']=='Friendly Matches' ][['id', 'count']].rename(columns={'count':'nbr_selections_friendly'})
    full_df = pd.merge(full_df, totals_df_friendly, on='id', how='outer')



def get_lang_id():

    global lang_id

    if 'lg' in pn.state.session_args.keys():
        try:
            lang_id = pn.state.session_args.get('lg')[0].decode('utf-8')
        except:
            pass

    if lang_id is None:
        lang_id = 'en'

    return lang_id

def overview_page(**kwargs):
    component = OverviewPage(full_df=full_df, lang_id=get_lang_id())
    return component.view()
    

def about_page(**kwargs):
    component = AboutPage(lang_id=get_lang_id())
    return component.view()

def matches_page(**kwargs):
    component = MatchesPage(lang_id=get_lang_id())
    return component.view()



def linkedin_page(**kwargs):

    component = pn.pane.HTML("""
<script src="https://platform.linkedin.com/badges/js/profile.js" async defer type="text/javascript"></script>
<div class="badge-base LI-profile-badge" data-locale="en_US" data-size="large" data-theme="dark" data-type="HORIZONTAL" data-vanity="pierreoliviersimonard" data-version="v1"><a class="badge-base__link LI-simple-link" href="https://fr.linkedin.com/in/pierreoliviersimonard?trk=profile-badge">Pierre-Olivier Simonard</a></div>
    """)
    return component


if __name__ == "__main__":

    load_data()
    

    server = pn.serve({ '/':overview_page,
                        '/overview': overview_page, 
                        '/linkedin':linkedin_page,
                        '/about':about_page, 
                        '/matches':matches_page
                    },
                      title={'/overview': 'UEFA Euro 2020 Statistics',
                            '/':'UEFA Euro 2020 Statistics',
                            '/linkedin':'LinkedIn Profile Pierre-Olivier Simonard',
                            '/about':'About',
                            '/matches':'Matches'

                            
                      },
                      websocket_origin=["uefaeuro2020.herokuapp.com"],
                      #websocket_origin=["*"],
                      #autoreload=True,
                      port=80,
                      threaded=True,
                      # check_unused_sessions=3,
                      # unused_session_lifetime=3
                      )

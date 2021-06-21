import panel as pn
from param import Composite
from pages.overview import OverviewPage
from pages.teams import TeamsPage
from pages.about import AboutPage
from pages.matches import MatchesPage
from pages.test import TestPage
import cache_manager

import pandas as pd
pd.options.plotting.backend

import i18n
import os

from pdb import set_trace as bp

from i18n import _
i18n.set_lang_id( i18n.available_languages()[0]  )


root_dname = os.path.dirname(os.path.abspath(__file__))
os.chdir(root_dname)

import holoviews as hv


# ---
import pandas as pd
import random
import hvplot.pandas # noqa

css = '''
.bk-root {
    font-size:14px;
}

.main-content {
    overflow-x: scroll !important;
}


.gotit-hide {
    visibility:hidden;
}

@font-face {
  font-family: 'babelstone';

  src: url('/resources/BabelStoneFlags.woff2') format('woff2'),
       url('/resources/BabelStoneFlags.woff') format('woff'),
       url('/resources/BabelStoneFlags.ttf') format('truetype');

}

/*
@font-face {
    font-family: 'noto';
    src: url("resources/NotoEmoji-Regular.ttf") format("truetype");
}*/


.fix_shitdows {
    font-family: babelstone !important;
}

.fix_shitdows select {
    font-family: babelstone !important;
}

.fix_shitdows option {
    font-family: babelstone !important;
}



'''


pn.extension(raw_css=[css], 
            #raw_js=[tracker],
            js_modules={"fontloader":'resources/FontLoader.js',     #https://github.com/smnh/FontLoader 
                        },
            js_files={"OWA":"resources/OWA.js"},
            loading_spinner='bar', 
            loading_color='#00aa41')

#pn.param.ParamMethod.loading_indicator = True


#----

full_df = None
selections_df = None


def load_data():
    global full_df 

    full_df = pd.read_csv("../app_data/full_df.csv")

def build_full_data():

    global full_df
    if full_df is not None:
        raise Exception("WTF ?!")

    players_df = pd.read_csv("../data/players.csv")
    clubs_df = pd.read_csv("../data/clubs.csv")
    selections_df = pd.read_csv("../data/selections.csv")

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



    totals_df = selections_df[ selections_df['competition_name']=='total' ][['id', 'count']].rename(columns={'count':'nbr_selections'})
    full_df = pd.merge(full_df, totals_df, on='id', how='outer')

    totals_df_euro = selections_df[ selections_df['competition_name']=='European Championship' ][['id', 'count']].rename(columns={'count':'nbr_selections_euro'})
    full_df = pd.merge(full_df, totals_df_euro, on='id', how='outer')

    totals_df_wcup = selections_df[ selections_df['competition_name']=='FIFA World Cup' ][['id', 'count']].rename(columns={'count':'nbr_selections_wcup'})
    full_df = pd.merge(full_df, totals_df_wcup, on='id', how='outer')

    totals_df_friendly = selections_df[ selections_df['competition_name']=='Friendly Matches' ][['id', 'count']].rename(columns={'count':'nbr_selections_friendly'})
    full_df = pd.merge(full_df, totals_df_friendly, on='id', how='outer')


    full_df.to_csv("../app_data/full_df.csv", index=False)

# ---- Helpers ---- 

def get_lang_id():

    params_lg = pn.state.session_args.get('lg')[0].decode('utf-8') if  'lg' in pn.state.session_args.keys() else None

    if params_lg in ['fr', 'en']:
        lang = params_lg

    else:
        lang =  'en'

    i18n.set_lang_id(lang)

    return lang


# ---- Pages ---- 


def overview_page(**kwargs):
    component = OverviewPage(full_df=full_df, lang_id=get_lang_id())
    return component.view()

def teams_page (**kwargs):

    country_code = pn.state.session_args.get('team_id')[0].decode('utf-8') if 'team_id' in pn.state.session_args else None

    component = TeamsPage(full_df=full_df, lang_id=get_lang_id(), country_code=country_code)
    return component.view()

def about_page(**kwargs):
    component = AboutPage(lang_id=get_lang_id())
    return component.view()

def matches_page(**kwargs):
    component = MatchesPage(lang_id=get_lang_id())
    return component.view()


def clear_page(**kwargs):
    pn.state.cache = {}

    print("cache cleared ", pn.state.cache)
    return ""

def dump_page(**kwargs):

    cache_manager.dump_data()



def test_page(**kwargs):
    component = TestPage(full_df=full_df, lang_id=get_lang_id())
    return component.view()
    

def linkedin_page(**kwargs):

    component = pn.pane.HTML("""
<script src="https://platform.linkedin.com/badges/js/profile.js" async type="text/javascript"></script>
<div class="badge-base LI-profile-badge" data-locale="en_US" data-size="large" data-theme="dark" data-type="HORIZONTAL" data-vanity="pierreoliviersimonard" data-version="v1">
<a class="badge-base__link LI-simple-link" href="https://fr.linkedin.com/in/pierreoliviersimonard?trk=profile-badge">Pierre-Olivier Simonard</a>
</div>
    """)
    return component


if __name__ == "__main__":

    # build_full_data()
    load_data()
    
    server = pn.serve({ '/':overview_page,
                        '/overview': overview_page, 
                        '/teams': teams_page, 
                        '/linkedin':linkedin_page,
                        '/about':about_page, 
                        '/matches':matches_page,
                        '/test':test_page,
                        '/clear':clear_page,
                        '/dump':dump_page
                    },
                      title={'/overview': 'Stats Euro 2020 ⚽️',
                            '/':'Stats Euro 2020 ⚽️',
                            '/teams':'Teams',
                            '/linkedin':'LinkedIn Profile Pierre-Olivier Simonard',
                            '/about':'About',
                            '/matches':'Matches',
                            '/test':'test',
                            '/clear':'clear',
                            '/dump':'dump',
                            
                      },
                      #websocket_origin=["uefaeuro2020.herokuapp.com"],
                      websocket_origin=[ "statseuro2020.com",
                                         "www.statseuro2020.com", 
                                         "uefaeuro2020.herokuapp.com",
                                         "localhost", 
                                         ],
                      autoreload=True,
                      port=int(os.getenv("PORT", 80)),
                      threaded=True,
                      static_dirs={'resources': '../resources'},
                      # check_unused_sessions=3,
                      # unused_session_lifetime=3
                      )

import panel as pn
from param import Composite
from pages.overview import OverviewPage
from pages.about import AboutPage
from pages.matches import MatchesPage
from pages.test import TestPage
# from pages.preload import PreloadPage
import pandas as pd
import i18n
import os

from pdb import set_trace as bp

from i18n import _
i18n.set_lang_id('en')


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


@font-face {
  font-family: 'babelstone';

  src: url('/resources/BabelStoneFlags.woff2') format('woff2'),
       url('/resources/BabelStoneFlags.woff') format('woff'),
       url('/resources/BabelStoneFlags.ttf') format('truetype');

}

'''


# @font-face {
#   font-family: 'noto';
#   src: url("resources/NotoColorEmoji.ttf") format("truetype");
# }


pn.extension(raw_css=[css], 
#js_modules={"fontloader":'resources/FontLoader.js'},
loading_spinner='dots', loading_color='#00aa41')

pn.param.ParamMethod.loading_indicator = True
#----


full_df = None
selections_df = None


def load_data():
    global full_df 

    full_df = pd.read_csv("../app_data/full_df.csv")

def build_full_data():


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


    cache_lg = pn.state.cache['lg'] if 'lg' in pn.state.cache else None 
    params_lg = pn.state.session_args.get('lg')[0].decode('utf-8') if  'lg' in pn.state.session_args.keys() else None

    print(f"cache : {cache_lg} \t params _lg : {params_lg}")

    if cache_lg is not None and params_lg is None:
        i18n.set_lang_id(pn.state.cache['lg'])
        return pn.state.cache['lg']


    if cache_lg is None and params_lg is None:
        pn.state.cache['lg'] = 'en'

    elif params_lg in ['fr', 'en']:
        pn.state.cache['lg'] = params_lg

    else:
        pn.state.cache['lg'] = 'en'

    i18n.set_lang_id(pn.state.cache['lg'])

    return pn.state.cache['lg']


def uses_noto():
    return ("Windows" in pn.state.headers['User-Agent']) or ('windows' in pn.state.headers['User-Agent'])

# ---- Pages ---- 

def session_create(p):

    print('session created : ', p.id)
    #pn.state.cookies['sid'] = p.id
    #bp()

def gotit(**kwargs):
    print("GOTIT PAGE", pn.state.session_args)
    pn.state.session_args['gotit'] = True
    print("GOTIT DONE", pn.state.session_args)

def overview_page(**kwargs):

    print("OVERVIEW PAGE : ", pn.state.curdoc.session_context.id)
    # bp()
    

    # print("session_info : ", pn.state.session_info, "\n")
    # print("session_args : ", pn.state.session_args, "\n")
    # print("cookies : ", pn.state.cookies, "\n")
    # print("curdoc : ", pn.state.curdoc, "\n")

    #bp()

    if 'gotit' in pn.state.session_args:
        del pn.state.session_args['gotit'] 

    """
    1) store in cache the asked page, 
        delete the "gotit" key from cache

    2) load page

            

            3) on callback of font loaded, 
                    load("/gotit") -> stores {"gotit":True} in cache

        

    """

    component = OverviewPage(full_df=full_df, lang_id=get_lang_id())
    return component.view()
    
def about_page(**kwargs):
    component = AboutPage(lang_id=get_lang_id())
    return component.view()

def matches_page(**kwargs):
    component = MatchesPage(lang_id=get_lang_id())
    return component.view()



def test_page(**kwargs):
    component = TestPage(lang_id=get_lang_id(), go='go' in pn.state.session_args)
    return component.view()
    

def linkedin_page(**kwargs):

    component = pn.pane.HTML("""
<script src="https://platform.linkedin.com/badges/js/profile.js" async defer type="text/javascript"></script>
<div class="badge-base LI-profile-badge" data-locale="en_US" data-size="large" data-theme="dark" data-type="HORIZONTAL" data-vanity="pierreoliviersimonard" data-version="v1"><a class="badge-base__link LI-simple-link" href="https://fr.linkedin.com/in/pierreoliviersimonard?trk=profile-badge">Pierre-Olivier Simonard</a></div>
    """)
    return component


# def preload_page(**kwargs):
#     if not uses_noto() or 'go' in pn.state.session_args:
#         component = OverviewPage(full_df=full_df, lang_id=get_lang_id())
#         return component.view()
#     else:
#         component = PreloadPage()
#         return component.view()
    

if __name__ == "__main__":

    # pprint(  [ (t, getattr( pn.state, t), ) for t in dir( pn.state) if  t.startswith("_") ])

    # build_full_data()
    load_data()
    
    pn.state.on_session_created(session_create)

    server = pn.serve({ '/':overview_page,
                        '/overview': overview_page, 
                        '/linkedin':linkedin_page,
                        '/about':about_page, 
                        '/matches':matches_page,
                        '/test':test_page,
                        '/gotit':gotit,
                    },
                      title={'/overview': 'UEFA Euro 2020 Statistics',
                            '/':'UEFA Euro 2020 Statistics',
                            '/linkedin':'LinkedIn Profile Pierre-Olivier Simonard',
                            '/about':'About',
                            '/matches':'Matches',
                            '/test':'test',
                            '/gotit':'Nothing to seen here'

                            
                      },
                      #websocket_origin=["uefaeuro2020.herokuapp.com"],
                      websocket_origin=["*"],
                      autoreload=True,
                      port=int(os.getenv("PORT", 80)),
                      threaded=True,
                      static_dirs={'resources': '../resources'},
                      # check_unused_sessions=3,
                      # unused_session_lifetime=3
                      )

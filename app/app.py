import panel as pn
from overview import OverviewPage
import pandas as pd
import i18n
from i18n import _

i18n.set_lang_id('en')


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

    selections_df = pd.read_csv("../data/selections.csv")

    totals_df = selections_df[ selections_df['competition_name']=='total' ][['id', 'count']].rename(columns={'count':'nbr_selections'})
    full_df = pd.merge(full_df, totals_df, on='id', how='outer')

    totals_df_euro = selections_df[ selections_df['competition_name']=='European Championship' ][['id', 'count']].rename(columns={'count':'nbr_selections_euro'})
    full_df = pd.merge(full_df, totals_df_euro, on='id', how='outer')

    totals_df_wcup = selections_df[ selections_df['competition_name']=='FIFA World Cup' ][['id', 'count']].rename(columns={'count':'nbr_selections_wcup'})
    full_df = pd.merge(full_df, totals_df_wcup, on='id', how='outer')





def overview_page(**kwargs):

    print("overview page", flush=True)

    lang_id = None
    if 'lg' in pn.state.session_args.keys():
        try:
            lang_id = pn.state.session_args.get('lg')[0].decode('utf-8')
        except:
            pass

    if lang_id is None:
        lang_id = 'en'

    component = OverviewPage(full_df=full_df, lang_id=lang_id)
    return component.view()
    


if __name__ == "__main__":

    load_data()
    

    server = pn.serve({'/overview': overview_page, },
                      title={'/overview': 'UEFA Euro 2020 Statistics'},
                      websocket_origin=["*"],
                      autoreload=True,
                      port=80,
                      threaded=True,
                      # check_unused_sessions=3,
                      # unused_session_lifetime=3
                      )

import panel as pn
from overview import OverviewPage
import pandas as pd
import i18n
from i18n import _

i18n.set_lang_id('en')


full_df = None

def load_full_df():

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

    full_df['group_hr'] = full_df['group'].transform(lambda x:"%s %s"%(_("dim_group"), x) )

    return full_df


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

    full_df = load_full_df()

    server = pn.serve({'/overview': overview_page, },
                      title={'/overview': 'Euro 2020 : Overview'},
                      websocket_origin=["*"],
                      autoreload=True,
                      port=80,
                      threaded=True,
                      # check_unused_sessions=3,
                      # unused_session_lifetime=3
                      )

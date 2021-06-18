import panel as pn
from i18n import _, countries_translations, field_positions_colors, explanations
from bokeh.models import HoverTool

from .common import fix_flags_hook, br
import pandas as pd


def countries_local_leagues_main(full_df, theme='light'):

    total_counts = full_df.groupby(["country_code"]).size().to_dict()

    # Which national teams rely the most on their local leagues?

    #count_per_country_club = full_df.groupby(["country_code", "country_code_club"]).count()['jersey_number'].reset_index().rename(columns={"jersey_number":"count"})
    count_per_country_club = full_df.groupby(
        ["country_code", "country_code_club"]).size().reset_index(name="count")

    count_per_country_club = count_per_country_club.loc[count_per_country_club['country_code'] == count_per_country_club['country_code_club'], [
        "country_code", "count"]].sort_values(by="count", ascending=True)

    count_per_country_club['percentage'] = count_per_country_club.apply(
        lambda x: round(x['count'] / total_counts[x['country_code']] * 100, 1), axis=1)

    count_per_country_club['country_name'] = count_per_country_club['country_code'] \
        .transform(lambda x: "%s %s" % (_(x, countries_translations()), _(x, countries_translations(), 'flag')))

    count_per_country_club = count_per_country_club.set_index('country_name')

    chart = count_per_country_club.hvplot.barh("country_name", "count", height=600, color='count', cmap='kgy') \
        .opts(labelled=[],
              title=_('countries_local_leagues_plot_title'),
              fontsize={'yticks': 10, 'xticks': 10},
              shared_axes=False,
              toolbar=None,
              default_tools=[],
              hooks=[fix_flags_hook],
              ) \
        .redim.label(count=_('dim_number_selected_players'), country_name=_("dim_country_code"))

    return chart

def countries_local_leagues_txt():
    return pn.pane.Markdown(explanations('countries_local_leagues'),
                                width=450) 


def items(full_df, theme):

    items = [  
         pn.pane.Markdown(f'''### {_('countries_local_leagues_title')} '''),
                # Seulement 5 teams over 24 have more than 50% of their players coming from their own league
            pn.Row(pn.Spacer(width=50), 
                    pn.pane.Markdown(f''' {_('countries_local_leagues_subtitle')} ''', 
                    sizing_mode='stretch_width'),
            ),
            pn.Row(pn.Spacer(width=50),
                countries_local_leagues_txt(),
                countries_local_leagues_main(full_df, theme),
             
            ),
            br(2),
            pn.pane.Markdown(f''' {_('countries_local_leagues_footer')}  '''),
        
            ]

    return items
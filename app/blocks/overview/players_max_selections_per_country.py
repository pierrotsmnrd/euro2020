from functools import cache
import panel as pn
from i18n import _, countries_translations, field_positions_colors, explanations
from bokeh.models import HoverTool

from ..common import fix_flags_hook, br, default_hovertool, uses_shitdows
import pandas as pd

import holoviews as hv

import os
import cache_manager 


def players_max_selections_per_country_main(full_df, theme='light'):


    plot_name = os.path.basename(__file__)[:-3] + f"_{theme}"

    plot_data = cache_manager.get_data(plot_name)
    if plot_data is None : 

        subdf = full_df.loc[full_df.groupby(['country_code'])[
            "nbr_selections"].idxmax()]

        cache_manager.cache_data(plot_name, subdf)
    else:
        subdf = plot_data

    scatter = subdf.hvplot.scatter(x='age_float',
                                   y='nbr_selections',
                                   c='field_position_color',
                                   by='field_position_hr',
                                   hover_cols=["international_name",
                                               "field_position_hr",
                                               "age",
                                               "country_name",
                                               "country_flag",
                                               "country_name_club",
                                               "country_flag_club",
                                               "weight",
                                               "height",
                                               "international_name_club",
                                               "nbr_selections",
                                               "nbr_selections_euro",
                                               "nbr_selections_wcup", "league_name"],
                                   height=600,
                                   width=800,
                                   muted_alpha=0.1,
                                   tools=[default_hovertool()],
                                   ylim=(
                                       0, int(full_df['nbr_selections'].max() * 1.1)),
                                   xlim=(full_df['age'].min()-1,
                                         full_df["age"].max()+1)
                                   ) \
        .opts(
        legend_position='bottom_right',
        legend_opts={"title": None},
        shared_axes=False,
        show_grid=True,
        toolbar="above",
        default_tools=[],
        #hooks=[fix_flags_hook],

    ) \
        .redim.label(
        age_float=_('dim_age'),
        nbr_selections=_('dim_nbr_selections'),
        field_position_hr=_('dim_field_position_hr'),
        international_name=_('dim_international_name'),
        age=_('dim_age'),
        country_code=_('dim_country_code'),
        international_name_club=_('dim_international_name_club'),
    )

    subdf['age_offset'] = subdf['age']
    subdf['nbr_selections_offset'] = subdf['nbr_selections']

    # on-demand offset for some countries
    subdf.loc[subdf['country_code'] == 'FRA', "age_offset"] -= 0.5
    subdf.loc[subdf['country_code'] == 'CRO', "age_offset"] -= 0.5
    subdf.loc[subdf['country_code'] == 'SVK', "age_offset"] -= 0.3

    subdf.loc[subdf['country_code'] == 'SWE', "age_offset"] += 0.5
    subdf.loc[subdf['country_code'] == 'BEL', "age_offset"] += 0.5
    subdf.loc[subdf['country_code'] == 'DEN', "age_offset"] += 0.7
    subdf.loc[subdf['country_code'] == 'FIN', "age_offset"] += 0.5
    subdf.loc[subdf['country_code'] == 'CZE', "age_offset"] += 0.5

    subdf.loc[subdf['country_code'] == 'RUS', "age_offset"] += 0.5
    subdf.loc[subdf['country_code'] == 'RUS', "nbr_selections_offset"] -= 7

    subdf.loc[subdf['country_code'] == 'UKR', "age_offset"] -= 0.5
    subdf.loc[subdf['country_code'] == 'UKR', "nbr_selections_offset"] -= 3

    subdf.loc[subdf['country_code'] == 'ENG', "age_offset"] += 0.7
    subdf.loc[subdf['country_code'] == 'ENG', "nbr_selections_offset"] -= 5

    labels = hv.Labels(subdf, ['age_offset', 'nbr_selections_offset'], 'country_flag').opts( text_font='babelstone' if uses_shitdows() else '', 
                                                                                    text_baseline='bottom', 
                                                                                    hooks=[fix_flags_hook]
                                                                                    )

    return scatter * labels



def players_max_selections_per_country_txt():

    return pn.pane.Markdown(explanations(f'players_max_selections_per_country_max'))



from ..base_block import BaseBlock

class PlayersMaxSelectionsPerCountry(BaseBlock):

    def __init__(self, full_df, theme):
        super(BaseBlock, self).__init__()
        self.main_plot = players_max_selections_per_country_main(full_df, theme)

    
    def items(self):
       
        items = [   pn.pane.Markdown(f'''## {_('selections_title')} '''),
                    br(),
                    pn.pane.Markdown(f''' {_('selections_subtitle_1')} ''', sizing_mode='stretch_width'),
                    br(),
        ]

        if self.preloading:
        
            items.append( pn.Spacer(height=508, loading=True) )
            return items

        else:

            items.append( pn.Row(pn.Spacer(width=50),
                           players_max_selections_per_country_txt(),
                            self.main_plot,
                        )
                    )
            return items 




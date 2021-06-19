import panel as pn
from i18n import _, countries_translations, field_positions_colors, explanations
from bokeh.models import HoverTool

from .common import fix_flags_hook, br, default_hovertool, uses_shitdows
import pandas as pd

import holoviews as hv


def players_age_nbr_selections_main(full_df, theme='light', dim="nbr_selections",):

    options_raw = list(full_df.groupby(
        ['country_name', 'country_flag', 'country_code']).groups.keys())
    options = {f"{i[0]} {i[1]}": i[2] for i in options_raw}

    select = pn.widgets.Select(name=' ',
                               options=options,
                               # we want to display Portugal by default, because CR7.
                               value='POR',
                               width=120,
                               css_classes=[ 'fix_shitdows'] if uses_shitdows() else []
                               )

    bound_fn = pn.bind(players_age_nbr_selections_plot,
                       full_df=full_df,
                       theme=theme,
                       dim=dim,
                       country_code=select,
                       )

    return pn.Column(
        select,
        bound_fn)



def players_age_nbr_selections_plot(full_df, theme='light', dim="nbr_selections", country_code=None):

    # doesn't require much caching on the data here

    df = full_df
    if country_code is not None:
        df = full_df[full_df["country_code"] == country_code]


    scatter = df.hvplot.scatter(x='age_float',
                                y=dim,
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
                                            "nbr_selections_wcup",
                                            "league_name"],
                                height=600,
                                width=800,
                                muted_alpha=0.1,
                                tools=[default_hovertool()],
                                ylim=(0, int(full_df[dim].max() * 1.1)),
                                xlim=(full_df['age'].min()-1,
                                      full_df["age"].max()+1)
                                      
                                ) \
        .opts(
        legend_position='bottom_right',
        legend_opts={"title": None},
        shared_axes=False,
        show_grid=True,
        toolbar="above",
        active_tools=[],
        hooks=[fix_flags_hook],
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

    return scatter


def players_age_nbr_selections_main_txt():

    return pn.pane.Markdown(explanations(f'players_max_selections_per_country_all'))



from .base_block import BaseBlock

class PlayersAgeNbrSelections(BaseBlock):

    def __init__(self, full_df, theme, dim="nbr_selections"):
        super(BaseBlock, self).__init__()
        self.main_plot = players_age_nbr_selections_main(full_df, theme, dim)

    
    def items(self):
       
        items = [ br(2),
                      pn.Row(pn.Spacer(width=50), 
                            pn.pane.Markdown(f''' {_('selections_subtitle_2')} ''', sizing_mode='stretch_width'),
                    )
        ]

        if self.preloading:
        
            items.append( pn.Spacer(height=508, loading=True) )
            return items

        else:

            items.append( pn.Row(pn.Spacer(width=50),

                                pn.Column(
                                    pn.Spacer(height=50),
                                    players_age_nbr_selections_main_txt(),
                                ),
                           
                            self.main_plot,
                        )
                    )
            return items 





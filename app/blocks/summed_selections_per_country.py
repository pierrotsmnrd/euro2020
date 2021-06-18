import panel as pn
from i18n import _, countries_translations, field_positions_colors, explanations
from bokeh.models import HoverTool

from .common import fix_flags_hook, br, default_hovertool, sort_options
import pandas as pd

import holoviews as hv

def summed_selections_per_country_main(full_df, theme):

    sum_sel_df = full_df.groupby(['country_name', 'country_flag']).sum()[['nbr_selections', 'nbr_selections_euro', 'nbr_selections_wcup', 'nbr_selections_friendly']]\
        .reset_index()\
        .sort_values('nbr_selections', ascending=False)

    sum_sel_df = sum_sel_df.rename(columns={
        'nbr_selections': 'Total',
        'nbr_selections_euro': 'Euro',
        'nbr_selections_wcup': 'WorldCup',
        'nbr_selections_friendly': 'Friendly',
    }
    )

    sum_sel_df['country_name'] = sum_sel_df['country_name'] + \
        sum_sel_df['country_flag']
    sum_sel_df = sum_sel_df.melt(id_vars=['country_name'], value_vars=[
                                 'Total', 'Euro', 'WorldCup', 'Friendly']).sort_values('value', ascending=True)
    sum_sel_df.set_index(['country_name', 'variable'])

    # default
    asc = True
    ordered_countries_names = sum_sel_df[sum_sel_df['variable'] == 'Total'].sort_values(
        'value', ascending=asc)['country_name'].values

    sort = 'Total'
    # we use this to reorder using redim.values
    if sort in sort_options():
        sort = sort_options()[sort]
        if sort != "country_name":
            ordered_countries_names = sum_sel_df[sum_sel_df['variable'] == sort].sort_values(
                'value', ascending=asc)['country_name'].values

    plots_width = {
        "Euro": 430,
        "WorldCup": 250,
        "Friendly": 250,
        "Total": 300
    }

    final_plot = None
    for c in ['Euro', 'WorldCup', 'Friendly', 'Total']:

        subdf = sum_sel_df[sum_sel_df['variable'] == c]

        subplot = subdf.hvplot.barh("country_name", "value",
                                    stacked=True,
                                    height=600,
                                    c='value',
                                    cmap='kgy',
                                    # cmap=hv.plotting.util.process_cmap('kgy')[::-1],
                                      width=plots_width[c],
                                      title=_(f"match_category_{c}")
                                    ).opts(toolbar=None,
                                            hooks=[fix_flags_hook],
                                           default_tools=[],
                                           ylim=(0, 1700) if c == 'Total' else (
                                               0, 570),

                                           )\
                        .redim.values(country_name=ordered_countries_names)\
                        .redim.label(value=_("dim_nbr_selections"),
                                    country_name=_("dim_country_code")
                                )

        if final_plot is None:
            final_plot = subplot
        else:
            final_plot += subplot.opts(yaxis=None,
                                       show_legend=False,
                                       shared_axes=False,
                                       )

    return final_plot



def items(full_df, theme):

    items = [   br(3),
            pn.Row(pn.Spacer(width=50), 
                
                pn.Column(
                    br(2),
                    pn.pane.Markdown(f''' {_('selections_subtitle_3')} ''', sizing_mode='stretch_width'),
                    br(),
                    summed_selections_per_country_main(full_df, theme),
                    br(),
                    pn.pane.Markdown(f''' {_('selections_conclusion')} ''', sizing_mode='stretch_width'),

                )
            ),
        
            ]

    return items
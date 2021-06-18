import panel as pn
from i18n import _, countries_translations, field_positions_colors, explanations
from bokeh.models import HoverTool

from .common import fix_flags_hook, br
import pandas as pd

import holoviews as hv

import os
import cache_manager 


def clubs_distribution_main(full_df, theme='light', full=False):



    plot_name = os.path.basename(__file__)[:-3]

    plot_data = cache_manager.get_data(plot_name)
    if plot_data is None:

        count_per_club = full_df.groupby(["international_name_club", "country_code_club"]).size(
        ).reset_index(name="count").sort_values('count', ascending=False)
        count_per_club = count_per_club[count_per_club['count'] > 5]

        count_per_club['international_name_club'] = count_per_club['international_name_club'] + "-" + \
            count_per_club['country_code_club'].transform(
                lambda x: _(x, countries_translations(), 'flag'))


        cache_manager.cache_data(plot_name, count_per_club)


    else:
        count_per_club = plot_data


    result = count_per_club.hvplot.bar(x='international_name_club',
                                       y='count',
                                       height=500,
                                       width=1000,
                                       cmap='kgy',
                                       color='count',
                                       title=_('clubs_distribution_plot_title')
                                       ).opts(
        xrotation=45,
        fontsize={
            'yticks': 10, 'xticks': 10},
        toolbar=None,
        hooks=[fix_flags_hook],
        default_tools=[],
        shared_axes=False,
        # ylim=(0,18),
    ).redim.label(
        international_name_club=_('dim_international_name_club'),
        count=_('dim_total'))

    # hardcoded because I need to spare time and mental health
    align_on = "Man. City-"+_('ENG', countries_translations(), 'flag')

    highlight = hv.VSpan(0, 5).opts(color='#636363',
                                    shared_axes=False,
                                    apply_ranges=True,
                                    toolbar=None,
                                    default_tools=[],)

    # highlight =  hv.VLine(4.5 ).opts(color='#636363', shared_axes=False,).opts(ylim=(0,18))
    highlight = highlight * \
        hv.Text(align_on,
                19, '11% of all\nthe players').opts(color='#FFFFFF',
                                                    text_align='left',
                                                    toolbar=None,
                                                    default_tools=[],)

    return (result*highlight).opts(ylim=(0, 22), shared_axes=False,)



def clubs_distribution_txt():
    return pn.pane.Markdown(explanations('clubs_distribution'))




def items(full_df, theme):

    items = [     br(),
            pn.pane.Markdown(f'''{_('clubs_distribution_title')} '''),
            pn.Row(pn.Spacer(width=50),
                clubs_distribution_txt(),
                clubs_distribution_main(full_df, theme)
            )
        
            ]

    return items
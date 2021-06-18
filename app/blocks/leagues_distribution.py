import panel as pn
from i18n import _, countries_translations, field_positions_colors, explanations
from bokeh.models import HoverTool

from .common import fix_flags_hook, br
import pandas as pd

import holoviews as hv


import os
import cache_manager 


def leagues_distribution_main(full_df, theme='light'):


    plot_name = os.path.basename(__file__)[:-3] + f"_{theme}"

    plot_data = cache_manager.get_data(plot_name)
    if plot_data is None : 

        count_per_country_club = full_df.groupby(["country_code_club"]).size(
        ).reset_index(name="count").sort_values('count', ascending=False)

        #count_per_country_club = count_per_country_club[  count_per_country_club['count'] >= 10 ]

        count_per_country_club['country_name_club'] = count_per_country_club['country_code_club'] \
            .transform(lambda x: "%s %s" % (_(x, countries_translations(), 'league'), _(x, countries_translations(), 'flag')))

        cache_manager.cache_data(plot_name, count_per_country_club)


    else:
        count_per_country_club = plot_data


    main = count_per_country_club.hvplot.bar(x='country_name_club',
                                             y='count',
                                             height=600,
                                             width=1000,
                                             cmap='kgy',
                                             color='count',
                                             title=_(
                                                 'leagues_distribution_plot_title'),
                                             ).opts(
        xrotation=45,
        fontsize={'yticks': 10, 'xticks': 10},
        toolbar=None,
        default_tools=[],
        shared_axes=False,
        hooks=[fix_flags_hook],
    ).redim.label(
        country_name_club=_('dim_league_name'),
        count=_('dim_total'))

    # hardcoded because I need to spare time and mental health
    align_on = "ENG"
    x_position = "%s %s" % (_(align_on, countries_translations(), 'league'), _(
        align_on, countries_translations(), 'flag'))
    highlight_left = hv.VSpan(0, 6,).opts(color='#636363', shared_axes=False, toolbar=None,
                                                      default_tools=[],) * \
        hv.Text(x_position,
                165, _('leagues_distribution_plot_67')).opts(color='#FFFFFF',
                                                             text_align='left', toolbar=None,
                                                             default_tools=[],)

    align_on = "BEL"
    x_position = "%s %s" % (_(align_on, countries_translations(), 'league'), _(
        align_on, countries_translations(), 'flag'))
    highlight_right = hv.Text(x_position,
                              170, _('leagues_distribution_plot_33')).opts(color='white',
                                                                           text_align='left', toolbar=None,
                                                                           default_tools=[],)

    return (main * highlight_left * highlight_right).opts(ylim=(0, 180),
                                                          toolbar=None,
                                                          default_tools=[],)




def leagues_distribution_txt():
    return pn.pane.Markdown(explanations('leagues_distribution') )
    

def items(full_df, theme):

    items = [  
        
            br(),
            pn.pane.Markdown(f'''{_('leagues_distribution_title')} '''),
            pn.Row(
                pn.Spacer(width=50), 
                leagues_distribution_txt(),
                leagues_distribution_main(full_df, theme),
                
            )
            ]

    return items
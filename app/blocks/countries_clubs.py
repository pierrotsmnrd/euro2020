import panel as pn
from i18n import _, countries_translations, field_positions_colors, explanations
from bokeh.models import HoverTool

from .common import fix_flags_hook, br
import pandas as pd

import holoviews as hv


def countries_clubs_main(full_df, theme='light', full=False):

    df_grouped_by = full_df.groupby(
        ["country_code", "international_name_club", "country_code_club"])

    count_per_club = df_grouped_by.size().reset_index(name="count")

    if not full:
        # filter to keep only starting at 2 players in the club
        count_per_club = count_per_club[count_per_club['count'] > 2]

    colormap = hv.plotting.util.process_cmap('kgy')

    if theme == 'dark':
        # For pairs that have zero values (eg France selected zero player playing in Belgian league)
        # we add a zero count ...
        #all_pairs = list(df_grouped_by.groups.keys())

        coutries_from = full_df['country_code'].unique()
        clubs_to = count_per_club[[
            'international_name_club', 'country_code_club']].values

        for c0 in coutries_from:
            for c1 in clubs_to:
                filter_c0 = count_per_club['country_code'] == c0
                filter_c1 = count_per_club['international_name_club'] == c1[0]

                if len(count_per_club[(filter_c0) & (filter_c1)]) == 0:
                    #print("adding : ")
                    #print(c0, c1 )
                    count_per_club = count_per_club.append({"country_code": c0,
                                                            "international_name_club": c1[0],
                                                            "country_code_club": c1[1],
                                                            "count": 0}, ignore_index=True)

        # ... and for value 0, we give a darkfgray color.
        # otherwise it remains white, despite trying to set the bgcolor.
        colormap[0] = "#2f2f2f"

    count_per_club['country_name'] = count_per_club['country_code'] \
        .transform(lambda x: "%s %s" % (_(x, countries_translations()), _(x, countries_translations(), 'flag')))
    count_per_club['country_name_club'] = count_per_club['country_code_club'] \
        .transform(lambda x: "%s %s" % (_(x, countries_translations(), 'league'), _(x, countries_translations(), 'flag')))

    count_per_club['international_name_club'] = count_per_club['international_name_club'] + " " + \
        count_per_club['country_code_club'] \
        .transform(lambda x: _(x, countries_translations(), 'flag'))

    yticks_sorted = sorted(list(count_per_club[['international_name_club', 'country_name_club']]
                                .groupby(['international_name_club', 'country_name_club']).groups.keys()), key=lambda x: x[1])
    yticks_sorted = [t[0] for t in yticks_sorted]

    heatmap = count_per_club.hvplot.heatmap(
        x='international_name_club',
        y='country_name',
        C='count',
        hover_cols=['count'],
        height=600,
        width=1350,
        colorbar=True,
        cmap=colormap,
        title=_('countries_clubs_plot_title') +
        _('countries_clubs_plot_title_extra') if not full else '',
    ) \
        .opts(xrotation=45,
              clim=(0, 10),
              bgcolor='white',
              toolbar=None,
              default_tools=[],
              fontsize={'yticks': 10, 'xticks': 10},
              shared_axes=False,
              hooks=[fix_flags_hook],
              ) \
        .redim.values(
        international_name_club=yticks_sorted,
        country_name=count_per_club['country_name'].sort_values()[::-1]) \
        .redim.label(country_name=_("dim_country_code"),
                     international_name_club=_('dim_international_name_club'),
                     count=_('dim_total'))

    return heatmap



def countries_clubs_txt():
    return pn.pane.Markdown(explanations('countries_clubs'))


def items(full_df, theme):

    items = [  
            br(3),
                pn.pane.Markdown(f'''### {_('countries_clubs_title')} '''),

                pn.Row(pn.Spacer(width=50), 
                        pn.pane.Markdown(f''' {_('countries_clubs_subtitle')} ''', sizing_mode='stretch_width'),
                        
                ),
                pn.Row(pn.Spacer(width=50),
                    pn.Column(countries_clubs_main(full_df, theme),
                    countries_clubs_txt())
                ),
                
            ]

    return items
import panel as pn
from i18n import _, countries_translations, field_positions_colors, explanations
from bokeh.models import HoverTool

from .common import fix_flags_hook, br
import pandas as pd

import holoviews as hv

def leagues_distribution_per_team_main(full_df, theme='light'):


    df_grouped_by = full_df.groupby(["country_code", "country_code_club"])

    count_per_country_club = df_grouped_by.size().reset_index(name="count")

    colormap = hv.plotting.util.process_cmap('kgy')

    if theme == 'dark':
        # For pairs that have zero values (eg France selected zero player playing in Belgian league)
        # we add a zero count ...
        all_pairs = list(df_grouped_by.groups.keys())

        coutries_from = list(set([c[0] for c in all_pairs]))
        coutries_to = list(set([c[1] for c in all_pairs]))

        for c0 in coutries_from:
            for c1 in coutries_to:
                filter_c0 = count_per_country_club['country_code'] == c0
                filter_c1 = count_per_country_club['country_code_club'] == c1

                if len(count_per_country_club[(filter_c0) & (filter_c1)]) == 0:
                    count_per_country_club = count_per_country_club.append(
                        {"country_code": c0, "country_code_club": c1, "count": 0}, ignore_index=True)

        # ... and for value 0, we give a darkfgray color.
        # otherwise it remains white, despite trying to set the bgcolor.
        colormap[0] = "#2f2f2f"

    count_per_country_club['country_name'] = count_per_country_club['country_code'] \
        .transform(lambda x: "%s %s" % (_(x, countries_translations()), _(x, countries_translations(), 'flag')))
    count_per_country_club['country_name_club'] = count_per_country_club['country_code_club'] \
        .transform(lambda x: "%s %s" % (_(x, countries_translations(),), _(x, countries_translations(), 'flag')))

    count_per_country_club['league_name'] = count_per_country_club['country_code_club'] \
        .transform(lambda x: "%s %s" % (_(x, countries_translations(), 'league'), _(x, countries_translations(), 'flag')))
    count_per_country_club['country_flag'] = count_per_country_club['country_code'] \
        .transform(lambda x: _(x, countries_translations(), 'flag'))

    # count_per_country_club =count_per_country_club \
    #                                 .sort_values(by="country_name_club", ascending=False) \
    #                                 .sort_values(by="country_name", ascending=False)

    main_heatmap = count_per_country_club.hvplot.heatmap(y='country_name',
                                                         x='league_name',
                                                         C='count',
                                                         hover_cols=['count'],
                                                         height=650,
                                                         width=1200,
                                                         colorbar=True,
                                                         # cmap='kgy',
                                                         cmap=colormap,
                                                         # cmap='kbc',
                                                         title=_(
                                                             "leagues_distribution_per_team_plot_title"),
                                                         ) \
        .opts(xrotation=45,
              bgcolor='white',
              fontsize={'yticks': 10, 'xticks': 10},
              shared_axes=False,
              toolbar=None,
              default_tools=[],
              ) \
        .redim.values(
        country_name=count_per_country_club['country_name'].sort_values()[
            ::-1],
        league_name=count_per_country_club.sort_values('country_name_club')[
            'league_name'],
    ) \
        .redim.label(country_name=_("dim_country_code"),
                     league_name=_(
            "dim_league_name"),
        count=_('dim_total'))

    # country_club_count = count_per_country_club.groupby(["country_name", "country_flag"])  \
    #                                         .size()   \
    #                                         .reset_index(name="count")  \
    #                                         .sort_values(by="country_name", ascending=False)

    # country_club_count['x'] = 1

    # tooltips_raw = [
    #     ('Pays', '@country_name'),
    #     ('Nombre de ligues différentes', '@count'),
    # ]

    # hover = HoverTool(tooltips=tooltips_raw)

    # ccc_hm = country_club_count.hvplot.heatmap(y='country_flag',
    #                                         x='x',
    #                                         C='count',
    #                                         hover_cols=['count', 'country_name'],
    #                                         height=500,
    #                                         width=150,
    #                                         colorbar=True,
    #                                         cmap='kgy',
    #                                 ) \
    #                                 .opts(  tools=[hover],
    #                                         xaxis=None,
    #                                         colorbar_position='right',
    #                                         yaxis='left',
    #                                         ylabel='Nombre total de ligues différents'
    #                                 )

    return main_heatmap




def leagues_distribution_per_team_txt():
    
    return pn.Row(pn.pane.Markdown(explanations('leagues_distribution_per_team') ,
                        width=200
            ) )

def items(full_df, theme):

    items = [   br(),
            
            pn.pane.Markdown(f'''### {_('leagues_distribution_per_team_title')} '''),
            pn.Row(pn.Spacer(width=50), 
                    pn.pane.Markdown(f'''{_('leagues_distribution_per_team_subtitle')} ''',
                    sizing_mode='stretch_width',
                    height=50),                    
            ),
            pn.Row(
                leagues_distribution_per_team_main(full_df, theme),
                leagues_distribution_per_team_txt()
            ),

        
            ]

    return items
from pdb import set_trace as bp
from datetime import datetime as dt
from threading import main_thread

import pandas as pd
import numpy as np

from pprint import pprint

import panel as pn
import hvplot.pandas  # noqa
import holoviews as hv
from bokeh.models import HoverTool
import param

from i18n import _, countries_translations, field_positions_colors, get_lang_id

pd.options.plotting.backend = 'holoviews'



def players_height_weight(full_df, theme='light'):

    tooltips_raw = [
        (_('dim_international_name'), '@international_name'),
        (_('dim_field_position_hr'), '@{field_position_hr}'),
        (_('dim_age'), f"@age { _('years_old') }"),
        (_('dim_country_code'), '@country_name @country_flag'),
        (_('dim_height'), '@height cm'),
        (_('dim_weight'), '@weight kg'),
        (_('dim_international_name_club'),
         '@international_name_club, @country_name_club @country_flag_club')
    ]

    hover = HoverTool(tooltips=tooltips_raw)

    scatter = full_df.hvplot.scatter(x='weight',
                                     y='height',
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
                                                 "international_name_club", ],
                                     height=600,
                                     width=800,
                                     muted_alpha=0.1,
                                     tools=[hover],

                                     ) \
        .opts(
        legend_position='bottom_right',
        legend_opts={"title": None},
        shared_axes=False,
        toolbar=None,
        default_tools=[],
        show_grid=True) \
        .redim.label(
        height=_('dim_height'),
        weight=_('dim_weight'),
        field_position_hr=_('dim_field_position_hr'),
        international_name=_('dim_international_name'),
        age=_('dim_age'),
        country_code=_('dim_country_code'),
        international_name_club=_('dim_international_name_club'),
    )

    #shown_count = len(full_df.loc[ ~(full_df.height.isna() | full_df.weight.isna()) ])

    #subtitle = _('subtitle_players_weight_and_size').replace("{%shown%}", str(shown_count)).replace("{%total%}",str(len(full_df)) )

    # result = pn.Column(pn.pane.Markdown(f'''## {_('title_players_weight_and_size')}
    # _{subtitle}_'''),
    #          scatter)

    return scatter

def players_height_weight_per_country(full_df,  theme):

    tooltips_raw = [
        (_('dim_country_code'), '@country_name'),
        (_('dim_height'), '@height cm'),
        (_('dim_weight'), '@weight kg'),
        ('', '@group_hr'),
    ]

    hover = HoverTool(tooltips=tooltips_raw)

    df_left = full_df.groupby('country_code').mean()[
        ['height', 'weight']].reset_index()

    df_right = full_df.groupby(['country_code', 'group', 'group_hr']).size(
    ).reset_index()[['country_code', 'group', 'group_hr']]

    df = pd.merge(df_left, df_right, how="outer",
                  on="country_code").sort_values('group_hr')

    df['country_name'] = df['country_code'].transform(lambda x: "%s %s" % (_(x, countries_translations()),
                                                                           _(x, countries_translations(), 'flag'))
                                                      )

    # The names of countries are of various lengths.
    # setting an offset to place all of them properly without overlapping is a challenge.
    # Furthermore, I haven't found a way to set a *variable* xoffset (even using hooks)
    # Simple and straightforward solution : set the offsets manually.

    # First, a base offset for all country names
    df['weight_offset'] = df['weight'] + 0.6
    df['height_offset'] = df['height']

    # Then, on-demand for some countries
    df.loc[df['country_code'] == 'TUR', "height_offset"] -= 0.1
    df.loc[df['country_code'] == 'FRA', "height_offset"] -= 0.1
    df.loc[df['country_code'] == 'POR', "height_offset"] -= 0.1

    df.loc[df['country_code'] == 'SUI', "weight_offset"] += 0.1
    df.loc[df['country_code'] == 'MKD', "weight_offset"] += 0.1

    df.loc[df['country_code'] == 'ITA', "weight_offset"] -= 0.9
    df.loc[df['country_code'] == 'ITA', "height_offset"] -= 0.1

    df.loc[df['country_code'] == 'BEL', "weight_offset"] -= 1.1
    df.loc[df['country_code'] == 'BEL', "height_offset"] += 0.0

    df.loc[df['country_code'] == 'NED', "weight_offset"] += 0.1
    df.loc[df['country_code'] == 'NED', "height_offset"] -= 0.15

    df.loc[df['country_code'] == 'CZE', "weight_offset"] += 0.3

    labels = hv.Labels(df, ['weight_offset', 'height_offset'], 'country_name',).opts(text_font_size='9pt',
                                                                                     # xoffset=0.52,
                                                                                     text_color='white'
                                                                                     )

    #colormap = hv.Cycle.default_cycles['default_colors'][::-1]

    scatter = df.hvplot.scatter(x='weight',
                                y='height',
                                # c='group_hr',
                                by='group_hr',
                                size=30,
                                # cmap=colormap,
                                hover_cols=["international_name",
                                            "field_position_hr",
                                            "age",
                                            "country_name",
                                            "country_flag",
                                            "country_name_club",
                                            "country_flag_club",
                                            "weight",
                                            "height",
                                            "international_name_club", ],
                                height=600,
                                width=800,
                                muted_alpha=0,
                                tools=[hover],
                                ) \
        .opts(
        legend_position='bottom_right',
        legend_opts={"title": None},
        #padding=((0.1, 0.2), 0.1)
        shared_axes=False,
        xlim=(72, 82),
        show_grid=True,
    ) \
        .redim.label(
        height=_('dim_height'),
        weight=_('dim_weight'),
        group_hr=_('dim_group')
    )

    #     shown_count = len(full_df.loc[ ~(full_df.height.isna() | full_df.weight.isna()) ])

    #     subtitle = _('subtitle_players_weight_and_size').replace("{%shown%}", str(shown_count)).replace("{%total%}",str(len(full_df)) )

    #     result = pn.Column(pn.pane.Markdown(f'''## {_('title_players_weight_and_size')}
    # _{subtitle}_'''),
    #               scatter*labels)

    result = (scatter*labels).opts(shared_axes=False)
    return result

def legend_for_players_dim():

    field_positions = list(field_positions_colors().keys())

    df = pd.DataFrame({
        'x': [0, 1, 2, 3],
        'y': [0]*4,
        'field_position': [_(x) for x in field_positions],
        'color': [field_positions_colors()[x] for x in field_positions]

    })

    points = hv.Points(df, ['x', 'y']).opts(color='color',
                                            size=6,
                                            )

    labels = hv.Labels(df, ['x', 'y'], 'field_position').opts(text_color='white',
                                                              text_align='left',
                                                              xoffset=0.05)

    return (points*labels).opts(shared_axes=False,
                                width=1300,
                                height=80,
                                xaxis=None,
                                yaxis=None,
                                toolbar=None,
                                xlim=(-0.5, 4),
                                ylim=(-1, 1),
                                )

def players_dim_per_country_per_position(full_df,  theme, dimension='age'):

    tooltips_raw = [
        (_('dim_international_name'), '@international_name'),
        (_('dim_field_position_hr'), '@{field_position_hr}'),
        (_('dim_age'), f"@age { _('years_old') }"),
        (_('dim_country_code'), '@country_name @country_flag'),
        (_('dim_height'), '@height cm'),
        (_('dim_weight'), '@weight kg'),
        (_('dim_international_name_club'),
         '@international_name_club, @country_name_club @country_flag_club')
    ]

    hover = HoverTool(tooltips=tooltips_raw)

    df = full_df.set_index(["country_code", "field_position"]).reset_index()

    df['color'] = df['field_position'].transform(
        lambda x: field_positions_colors()[x])
    df['country_name'] = df['country_code'] \
        .transform(lambda x: "%s %s" % (_(x, countries_translations()),
                                        _(x, countries_translations(), 'flag')))

    points = hv.Points(df, ['country_name', dimension],
                       ).opts(color='color',
                              # show_legend=False,
                              jitter=0.2,
                              alpha=0.5,
                              size=6,
                              tools=[hover],
                              height=600,
                              width=1300,
                              xrotation=45,
                              show_grid=True,
                              gridstyle={
                                  'grid_line_color': 'lightgray',
                                  # 'grid_line_width': 1.5,
                                  # 'xgrid_bounds': (0, 0),
                                  'minor_xgrid_line_color': 'lightgray',
                                  'xgrid_line_dash': [1, 4]},
                              shared_axes=False,
                              ).redim.label(age=_('dim_age'),
                                            weight=_(
                                  'dim_weight'),
        height=_(
                                  'dim_height'),
        country_name='Equipe')

    legend = legend_for_players_dim()

    return hv.Layout(legend + points).cols(1).opts(shared_axes=False,)


def teams_average_age(full_df,  theme):

    mean_ages_df = pd.DataFrame(full_df.groupby("country_code")
                                .mean()['age']
                                .sort_values(ascending=True)).reset_index()
    mean_ages_df['country_name'] = mean_ages_df['country_code'] \
        .transform(lambda x: "%s %s" % (_(x, countries_translations()),
                                        _(x, countries_translations(), 'flag')))

    mean_ages_df = mean_ages_df.set_index('country_name')

    mean_ages_df = mean_ages_df.sort_values(by='age')

    result = mean_ages_df.hvplot.barh(height=600) \
        .opts(labelled=[],
              title="Age moyen des joueurs par équipe",
              shared_axes=False,) \
        .redim.label(age='Age moyen', country_name='Equipe')

    return result

import panel as pn
from i18n import _, countries_translations, field_positions_colors, explanations
from bokeh.models import HoverTool

from .common import fix_flags_hook, br, uses_shitdows
import pandas as pd

import holoviews as hv

_sankey_full_singleton = None


def build_sankey_full(full_df):

    global _sankey_full_singleton
    if _sankey_full_singleton is None:

        
        # First, build the data where :
        # - source is the club's country (country_code_club)
        # - destination is the club's name (display_official_name)
        # - volume is the number of players

        # count_per_country_club['league_name'] = count_per_country_club['country_code_club'] \
        #                             .transform(lambda x:"%s %s"%(_(x, countries_translations(), 'league'),_(x, countries_translations(), 'flag'))  )

        sankey_base = full_df.groupby(["country_code", "country_name", "country_flag",                 # National teams' data
                                       "country_code_club", "league_name",                            # Leagues' data
                                       "display_official_name",                                       # clubs' data
                                       "international_name"                                           # players'
                                       ]).size().reset_index(name="count")

        sankey_base["country_name_flag"] = sankey_base["country_name"] + \
            " " + sankey_base['country_flag']
        sankey_base['country_country_club_junction'] = sankey_base['country_code'] + \
            "_" + sankey_base['country_code_club']

        # left part, national teams -> clubs' countries
        left_part_groupby = sankey_base.groupby(["country_code",
                                                "country_name_flag",
                                                 "country_country_club_junction",
                                                 "league_name",
                                                 ])
        left_part = left_part_groupby["count"].sum().reset_index(name="volume")
        left_part = left_part.rename(columns={
            "country_code": "source",
            "country_name_flag": "source_lib",
            "country_country_club_junction": "destination",
            "league_name": "destination_lib"
        })

        names_serie = left_part_groupby['international_name'].apply(
            lambda x: ', '.join(x))
        names_serie = names_serie.reset_index(name='players').rename(columns={
            "country_code": "source",
            "country_name_flag": "source_lib",
            "country_country_club_junction": "destination",
            "league_name": "destination_lib"
        })

        left_part['source_type'] = 'country'

        left_part = pd.merge(left_part,
                             names_serie,
                             how='outer',
                             on=['source', 'source_lib', 'destination', 'destination_lib'])

        # right part, clubs' countries -> clubs
        right_part_groupby = sankey_base.groupby(
            ["league_name", "country_country_club_junction", "display_official_name"])
        right_part = right_part_groupby["count"].sum(
        ).reset_index(name="volume")

        right_part = right_part.rename(columns={
            "country_country_club_junction": "source",
            "league_name": "source_lib",
            "display_official_name": "destination"
        })

        names_serie = right_part_groupby['international_name'].apply(
            lambda x: ', '.join(x))
        names_serie = names_serie.reset_index(name='players').rename(columns={
            "country_country_club_junction": "source",
            "league_name": "source_lib",
            "display_official_name": "destination"
        })
        right_part['source_type'] = 'league'
        right_part = pd.merge(right_part,
                              names_serie,
                              how='outer',
                              on=['source', 'source_lib', 'destination'])

        right_part["destination_lib"] = right_part["destination"]

        # .drop('destination_code', axis=1)
        _sankey_full_singleton = pd.concat([left_part, right_part])

    return _sankey_full_singleton


# https://chase-seibert.github.io/blog/2011/07/29/python-calculate-lighterdarker-rgb-colors.html
def color_variant(hex_color, brightness_offset=1):
    """ takes a color like #87c95f and produces a lighter or darker variant """
    if len(hex_color) != 7:
        raise Exception(
            "Passed %s into color_variant(), needs to be in #87c95f format." % hex_color)
    rgb_hex = [hex_color[x:x+2] for x in [1, 3, 5]]
    new_rgb_int = [int(hex_value, 16) +
                   brightness_offset for hex_value in rgb_hex]
    # make sure new values are between 0 and 255
    new_rgb_int = [min([255, max([0, i])]) for i in new_rgb_int]
    # hex() produces "0x88", we want just "88"
    return "#" + "".join([hex(i)[2:] for i in new_rgb_int])


def sankey_hook(plot, element):

    for handle in plot.handles:
        # print(handle)
        # print( dir(plot.handles[handle]) )
        # print("\n")
        try:
            plot.handles[handle].text_color = 'white'
            # print(handle)
        except:
            pass


def sankey_for_country_code(country_code, sankey_full,  theme):

    sankey_df = pd.DataFrame(sankey_full[(sankey_full['source'] == country_code) | (
        sankey_full['source'].str.startswith(f'{country_code}_'))])

    

    nbr_leagues = sankey_df.loc[ sankey_df['source_type'] == 'league', 'source' ].nunique()
    nbr_clubs = sankey_df.loc[ sankey_df['source_type'] == 'league', 'destination' ].nunique()

    # Build a list of colors to give as colormap for the Sankey, to get around a bug
    # that prevents using a column as color dimension
    if len(sankey_df['source'].unique()) > len(hv.Cycle.default_cycles['default_colors']):
        base_cmap = hv.Cycle.default_cycles['default_colors'] * 2
    else:
        base_cmap = hv.Cycle.default_cycles['default_colors']

    colormap = list(base_cmap[: len(sankey_df["source"].unique())])
    color_dict = dict(zip(sankey_df['source'].unique()[1:], colormap[1:]))

    for node in sankey_df['source'].unique()[1:]:
        nbr_variations = len(sankey_df[sankey_df['source'] == node])

        # The more variations in color,
        # the smaller the offset in each variation
        variation_offset = int(30 / (nbr_variations//5 + 1))
        for i in range(nbr_variations):
            #print(nbr_variations, variation_offset, i*variation_offset)
            colormap.append(color_variant(
                color_dict[node], i*variation_offset))

    if theme == 'dark':
        bgcolor = '#424242'
        edge_color = '#707070'
        hooks = [sankey_hook, fix_flags_hook]
        text_color = 'white'
    else:
        bgcolor = '#424242'  # TO CHANGE !
        edge_color = '#707070'  # TO CHANGE !
        hooks = [fix_flags_hook]
        text_color = 'black'

    sankey = hv.Sankey(sankey_df,
                       ["source_lib", "destination_lib"],
                       vdims=[hv.Dimension("volume"), hv.Dimension("players")],
                       ).opts(width=1200,
                              height=800,
                              bgcolor=bgcolor,
                              edge_color=edge_color,
                              node_line_color=edge_color,
                              edge_line_color=edge_color,
                              cmap=colormap,
                              label_position='right',
                              node_sort=False,
                              toolbar=None,
                              default_tools=[],
                              fontsize={'yticks': 10, 'xticks': 10},
                              hooks=hooks
                              ).redim.label(source_lib=_('from'),
                                            destination_lib=_('to'),
                                            volume=_('dim_number_players'),
                                            players=_('dim_players'))

    result =  sankey \
        * hv.Text(0+35, 530, _('dim_country_code')).opts(color=text_color, toolbar=None, default_tools=[],) \
        * hv.Text(500, 530, f'{nbr_leagues} ' + _('dim_league_name_plural')   ).opts(color=text_color, toolbar=None, default_tools=[],) \
        * hv.Text(1000, 530, f'{nbr_clubs} ' + _('dim_international_name_club_plural')  ).opts(color=text_color, toolbar=None, default_tools=[],)


    return result


def clubs_distribution_per_team_main(full_df, theme='light'):

    options_raw = list(full_df.groupby(
        ['country_name', 'country_flag', 'country_code']).groups.keys())
    options = {f"{i[0]} {i[1]}": i[2] for i in options_raw}


    select = pn.widgets.Select(name=' ',
                               options=options,
                               value='FRA',
                               width=120,
                               css_classes=[ 'fix_shitdows'] if uses_shitdows() else []
                               )

    bound_fn = pn.bind(sankey_for_country_code,
                       country_code=select,
                       sankey_full=build_sankey_full(full_df),
                       theme=theme)

    return pn.Column(   select,
                        bound_fn )



def items(full_df, theme):

    items = [  
         br(3),
            pn.Row(pn.Spacer(width=50), 
                    pn.pane.Markdown(f''' {_('sankey_title')} ''')
            ),
            pn.Row(pn.Spacer(width=50),
                clubs_distribution_per_team_main(full_df,  theme)
            )

            ]

    return items
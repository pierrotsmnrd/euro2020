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

from i18n import _, countries_translations, field_positions_colors

pd.options.plotting.backend = 'holoviews'

from pdb import set_trace as bp

#from panel.template import DefaultTheme
#from panel.template import DarkTheme


# We want the count of each field_position for each country
# We keep column international_name because we're sure there are no NA values for this column

def positions_distribution(full_df, lang_id, theme='light'):
    counts = full_df.groupby(['country_code', 'field_position']) \
                .size().reset_index(name = "count").sort_values(by="country_code", ascending=True)

    maxis = counts.groupby('field_position').max().rename(columns={'count':'maxi'})


    tooltips = f"""
    <div style="width:200px">

        <div class="bk" style="display: table; border-spacing: 2px;">
            <div class="bk" style="display: table-row;">
                <div class="bk bk-tooltip-row-label" style="display: table-cell;">{_('dim_country_code')} : </div>
                <div class="bk bk-tooltip-row-value" style="display: table-cell;">
                    <span class="bk" data-value="">@country_name</span>
                </div>
            </div>
        </div>

        <div class="bk" style="display: table; border-spacing: 2px;">
            <div class="bk" style="display: table-row;">
                <div class="bk bk-tooltip-row-label" style="display: table-cell;">{_('label_number')} : </div>
                <div class="bk bk-tooltip-row-value" style="display: table-cell;">
                    <span class="bk" data-value="">@count</span>
                </div>
            </div>
        </div>

          <div class="bk" style="display: table; border-spacing: 2px;">
            <div class="bk" style="display: table-row;">
                <div class="bk bk-tooltip-row-label" style="display: table-cell;">{_('label_players')}</div>
                <div class="bk bk-tooltip-row-value" style="display: table-cell;">
                    <span class="bk" data-value="">@international_name</span>
                </div>
            </div>
        </div>

    </div>
    """


    hover = HoverTool(tooltips=tooltips)

    plots_per_position = {}
    final_plot = None

    
    positions = full_df.field_position.unique()
    for p in positions:

        max_for_p = maxis.loc[p]['maxi']

        count_serie = full_df[ full_df.field_position == p ].groupby(['country_code', 'field_position']) \
                          .size().reset_index(name = "count") \
                          .set_index(['country_code', 'field_position'])

        names_serie = full_df[ full_df.field_position == p ].groupby(['country_code', 'field_position'])['international_name'].apply(lambda x: ', '.join(x))

        df_for_p = pd.concat([count_serie, names_serie], axis=1).reset_index()

        df_for_p['country_name'] = df_for_p['country_code'].transform(lambda x:"%s %s"%(_(x, countries_translations(), lang_id),_(x, countries_translations(), 'flag'))  )

        df_for_p = df_for_p.set_index(['country_name', 'field_position']).sort_values(by="country_name", ascending=False)

        width = max(150, int(max_for_p*20) ) + (100 if p == positions[0] else 0)
        
        plot = df_for_p.hvplot \
            .barh(stacked=True,
                  cmap=field_positions_colors(), 
                  height=450, 
                  width= width,
                  hover_cols=[  'country_name', 
                                'field_position_hr',
                                'count',
                                'international_name', ],
                  tools=[hover]
                 ) \
            .opts(title=_(p+"_plural"), 
                  show_legend=False,
                  xticks=[ i for i in range(max_for_p)], 
                  labelled=[],
                  fontsize={'yticks': 10},
                 )

        plots_per_position[p] = plot

        if final_plot is None:
            final_plot = plot
        else:
            final_plot += plot.opts(yaxis=None, )

    

    final_plot = final_plot.opts(shared_axes=False, toolbar=None, width=1200,)

    return final_plot
    
    
def countries_local_leagues(full_df, lang_id, theme='light'):
    total_counts = full_df.groupby(["country_code"]).size().to_dict()

    # Which national teams rely the most on their local leagues?

    #count_per_country_club = full_df.groupby(["country_code", "country_code_club"]).count()['jersey_number'].reset_index().rename(columns={"jersey_number":"count"})
    count_per_country_club = full_df.groupby(["country_code", "country_code_club"]).size().reset_index(name="count")

    count_per_country_club = count_per_country_club.loc[  count_per_country_club['country_code'] == count_per_country_club['country_code_club'] , ["country_code", "count"] ].sort_values(by="count", ascending=True)

    count_per_country_club['percentage'] = count_per_country_club.apply( lambda x: round(x['count'] / total_counts[x['country_code']] *100,1) , axis=1 )


    count_per_country_club['country_name'] = count_per_country_club['country_code'] \
                                    .transform(lambda x:"%s %s"%(_(x, countries_translations(), lang_id),_(x, countries_translations(), 'flag'))  )

    count_per_country_club = count_per_country_club.set_index('country_name')


    chart = count_per_country_club.hvplot.barh("country_name", "count", height=600, color='count', cmap='kgy') \
                        .opts(labelled=[], 
                            # title="Quelles équipes ont selectionné des joueurs de leurs propres ligues ?",
                            #title="Nombre de joueurs sélectionnés évoluant dans le championnat de leur propre pays ",
                            #title="Par pays, nombre de joueur sélectionnés qui évoluent dans le championnat national",
                            title='Nombre de joueurs sélectionnés évoluant dans la ligue de leur pays',

                            fontsize={'yticks': 10},
                            shared_axes=False,
                            ) \
                        .redim.label(count='Nombres de joueurs sélectionnés', country_name='Equipe')

    return chart



def leagues_distribution(full_df, lang_id, theme='light'):
        

    df_grouped_by = full_df.groupby(["country_code", "country_code_club"])

    count_per_country_club = df_grouped_by.size().reset_index(name = "count")

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
                
                if len(count_per_country_club[ (filter_c0) & (filter_c1) ]) == 0:
                    count_per_country_club = count_per_country_club.append({"country_code":c0, "country_code_club":c1, "count":0}, ignore_index=True)
                    
        
        # ... and for value 0, we give a darkfgray color.
        # otherwise it remains white, despite trying to set the bgcolor.
        colormap[0] = "#2f2f2f"

    

    count_per_country_club['country_name'] = count_per_country_club['country_code'] \
                                    .transform(lambda x:"%s %s"%(_(x, countries_translations(), lang_id),_(x, countries_translations(), 'flag'))  )
    count_per_country_club['country_name_club'] = count_per_country_club['country_code_club'] \
                                    .transform(lambda x:"%s %s"%(_(x, countries_translations(), lang_id),_(x, countries_translations(), 'flag'))  )
    count_per_country_club['country_flag'] = count_per_country_club['country_code'] \
                                    .transform(lambda x: _(x, countries_translations(), 'flag'))  



    # count_per_country_club =count_per_country_club \
    #                                 .sort_values(by="country_name_club", ascending=False) \
    #                                 .sort_values(by="country_name", ascending=False)


    main_heatmap = count_per_country_club.hvplot.heatmap(y='country_name', 
                                        x='country_name_club', 
                                        C='count', 
                                        hover_cols=['count'],
                                        height=600,
                                        width=1100, 
                                        colorbar=True,
                                        #cmap='kgy', 
                                        cmap=colormap,
                                        #cmap='kbc',
                                        title='Répartition des ligues des joueurs'
                                        ) \
                                    .opts(xrotation=45, 
                                        bgcolor='white',
                                        toolbar=None,
                                        fontsize={'yticks': 10},
                                        shared_axes=False,
                                        ) \
                                    .redim.values(
                                        country_name=count_per_country_club['country_name'].sort_values()[::-1],
                                        country_name_club=count_per_country_club['country_name_club'].sort_values(),
                                    ) \
                                    .redim.label(country_name="Equipes", 
                                                country_name_club="Ligue des joueurs selectionnés",
                                                count='Total')

    
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



def countries_clubs(full_df, lang_id, theme='light', full=False):

    #bp()

    df_grouped_by = full_df.groupby(["country_code", "international_name_club", "country_code_club"])

    count_per_club = df_grouped_by.size().reset_index(name = "count")

    if not full: 
        count_per_club = count_per_club[ count_per_club['count'] > 2 ] # filter to keep only starting at 2 players in the club
    
    colormap = hv.plotting.util.process_cmap('kgy')

    if theme == 'dark':
        # For pairs that have zero values (eg France selected zero player playing in Belgian league)
        # we add a zero count ...
        #all_pairs = list(df_grouped_by.groups.keys())


        coutries_from =  full_df['country_code'].unique() 
        clubs_to = count_per_club[ ['international_name_club', 'country_code_club'] ].values

        for c0 in coutries_from:
            for c1 in clubs_to:
                filter_c0 = count_per_club['country_code'] == c0
                filter_c1 = count_per_club['international_name_club'] == c1[0]
                
                if len(count_per_club[ (filter_c0) & (filter_c1) ]) == 0:
                    #print("adding : ")
                    #print(c0, c1 )
                    count_per_club = count_per_club.append({"country_code":c0,
                                                             "international_name_club":c1[0], 
                                                            "country_code_club":c1[1],
                                                            "count":0}, ignore_index=True)
                    
        
        # ... and for value 0, we give a darkfgray color.
        # otherwise it remains white, despite trying to set the bgcolor.
        colormap[0] = "#2f2f2f"

    
    count_per_club['country_name'] = count_per_club['country_code'] \
                                    .transform(lambda x:"%s %s"%(_(x, countries_translations(), lang_id),_(x, countries_translations(), 'flag'))  )
    count_per_club['country_name_club'] = count_per_club['country_code_club'] \
                                     .transform(lambda x:"%s %s"%(_(x, countries_translations(), lang_id),_(x, countries_translations(), 'flag'))  )

    count_per_club['international_name_club'] = count_per_club['international_name_club'] + " " + \
                                                 count_per_club['country_code_club'] \
                                                    .transform(lambda x: _(x, countries_translations(), 'flag'))

    
    
    yticks_sorted = sorted(list(count_per_club[ ['international_name_club', 'country_name_club']]\
        .groupby(['international_name_club', 'country_name_club']).groups.keys()), key=lambda x:x[1])
    yticks_sorted = [ t[0] for t in yticks_sorted]


    heatmap = count_per_club.hvplot.heatmap(
                                        x='international_name_club', 
                                        y='country_name', 
                                        C='count', 
                                        hover_cols=['count'],
                                        height=600,
                                        width=1350, 
                                        colorbar=True,
                                        #cmap='kgy', # 'kbc'
                                        cmap=colormap,
                                        title='Répartition des clubs des joueurs' +  '(à partir de 3 joueurs d\'un même club par équipe)' if not full else '',
                                        ) \
                                    .opts(xrotation=45, 
                                          clim=(0,10),
                                            bgcolor='white',
                                        toolbar = None, 
                                        fontsize={'yticks': 10}
                                    ) \
                                    .redim.values(
                                            international_name_club=yticks_sorted, 
                                            country_name=count_per_club['country_name'].sort_values()[::-1] ) \
                                    .redim.label(country_name="Equipes", 
                                                international_name_club="Clubs des joueurs selectionnés", 
                                                count='Total') 


    return heatmap

    
_sankey_full_singleton = None

def build_sankey_full(full_df):

    global _sankey_full_singleton
    if _sankey_full_singleton is None : 

        # First, build the data where :
        # - source is the club's country (country_code_club) 
        # - destination is the club's name (display_official_name)
        # - volume is the number of players

        sankey_base = full_df.groupby(["country_code", "country_code_club", "display_official_name","international_name"]).size().reset_index(name = "count")

        sankey_base['country_country_club_junction'] = sankey_base['country_code'] + "_" + sankey_base['country_code_club']

        # left part, national teams -> clubs' countries
        left_part_groupby = sankey_base.groupby(["country_code", "country_country_club_junction"])
        left_part = left_part_groupby["count"].sum().reset_index(name="volume")
        left_part = left_part.rename(columns={
            "country_code":"source",
            "country_country_club_junction":"destination"
        })

        names_serie = left_part_groupby['international_name'].apply(lambda x: ', '.join(x))
        names_serie = names_serie.reset_index(name='players').rename(columns={
            "country_code":"source",
            "country_country_club_junction":"destination"
        })

        left_part = pd.merge(left_part, 
                names_serie,
                how='outer', 
                on=['source', 'destination'])



        # right part, clubs' countries -> clubs
        right_part_groupby = sankey_base.groupby([ "country_country_club_junction", "display_official_name"])
        right_part = right_part_groupby["count"].sum().reset_index(name="volume")

        right_part = right_part.rename(columns={
            "country_country_club_junction":"source",
            "display_official_name":"destination"
        })

        names_serie = right_part_groupby['international_name'].apply(lambda x: ', '.join(x))
        names_serie = names_serie.reset_index(name='players').rename(columns={
            "country_country_club_junction":"source",
            "display_official_name":"destination"
        })

        right_part = pd.merge(right_part, 
                names_serie,
                how='outer', 
                on=['source', 'destination'])


        _sankey_full_singleton = pd.concat([left_part, right_part])


    return _sankey_full_singleton


# https://chase-seibert.github.io/blog/2011/07/29/python-calculate-lighterdarker-rgb-colors.html
def color_variant(hex_color, brightness_offset=1):
    """ takes a color like #87c95f and produces a lighter or darker variant """
    if len(hex_color) != 7:
        raise Exception("Passed %s into color_variant(), needs to be in #87c95f format." % hex_color)
    rgb_hex = [hex_color[x:x+2] for x in [1, 3, 5]]
    new_rgb_int = [int(hex_value, 16) + brightness_offset for hex_value in rgb_hex]
    new_rgb_int = [min([255, max([0, i])]) for i in new_rgb_int] # make sure new values are between 0 and 255
    # hex() produces "0x88", we want just "88"
    return "#" + "".join([hex(i)[2:] for i in new_rgb_int])


def sankey_hook(plot, element):
   
    for handle in plot.handles:
        # print(handle)
        # print( dir(plot.handles[handle]) )
        # print("\n")
        try:
            plot.handles[handle].text_color = 'white'
            #print(handle)
        except:
            pass
    

def sankey_for_country_code(country_code, sankey_full, lang_id, theme):

    sankey_fr = pd.DataFrame(sankey_full[ (sankey_full['source']==country_code) | (sankey_full['source'].str.startswith(f'{country_code}_')) ])

    # Build a list of colors to give as colormap for the Sankey, to get around a bug 
    # that prevents using a column as color dimension
    if len(sankey_fr['source'].unique()) > len(hv.Cycle.default_cycles['default_colors']):
        base_cmap = hv.Cycle.default_cycles['default_colors'] * 2
    else:
        base_cmap = hv.Cycle.default_cycles['default_colors']

    colormap =  list(base_cmap[ : len(sankey_fr["source"].unique()) ])
    color_dict = dict(zip(sankey_fr['source'].unique()[1:], colormap[1:]))


    for node in sankey_fr['source'].unique()[1:]:
        nbr_variations = len(sankey_fr[ sankey_fr['source'] == node ])

        # The more variations in color,
        # the smaller the offset in each variation
        variation_offset = int(30 / (nbr_variations//5 +1)) 
        for i in range(nbr_variations):
            #print(nbr_variations, variation_offset, i*variation_offset)
            colormap.append( color_variant( color_dict[node], i*variation_offset ) )


    # if country_code is FRA : 
    # - replace FRA with "France 🇫🇷"
    # - replace FRA_* with the corresponding country + flag
    # _ for FRA_FRA, replaces it with "France  🇫🇷" WITH TWO SPACES to avoid cycling graph (Sankey doesn't support them)

    sankey_fr = sankey_fr.replace(country_code,
         "%s %s"%(_(country_code, countries_translations(), lang_id),
                  _(country_code, countries_translations(), 'flag'))  )

        

    for node in sankey_fr['source'].unique()[1:]:

        country = node.split("_")[1]    
        if node == '%s_%s'%(country_code, country_code):
            # two spaces, to make it 
            replacement = "%s  %s"%(_(country, countries_translations(), lang_id), _(country, countries_translations(), 'flag'))
        else:
            replacement = "%s %s"%(_(country, countries_translations(), lang_id), _(country, countries_translations(), 'flag'))

        sankey_fr = sankey_fr.replace(node, replacement  )

    title = f"{ _(country_code, countries_translations(),lang_id)} {_(country_code, countries_translations(),'flag')} - Clubs d'origine des joueurs"
    
    if theme == 'dark':
        bgcolor = '#424242'
        edge_color = '#707070'
        hooks = [sankey_hook]
        text_color = 'white'
    else:
        bgcolor = '#424242' # TO CHANGE !
        edge_color = '#707070' # TO CHANGE ! 
        hooks = []
        text_color = 'black'


    sankey = hv.Sankey(sankey_fr,
                    vdims=[hv.Dimension("volume"), hv.Dimension("players")], 
                ).opts(width=1200, 
                        height=800,
                        bgcolor=bgcolor,
                        edge_color=edge_color,
                        node_line_color=edge_color,
                        edge_line_color=edge_color,
                        cmap= colormap, 
                        label_position='right',
                        node_sort=False,
                        toolbar=None,
                        fontsize={'yticks': 10},
                        hooks = hooks
                    ).redim(source='De', 
                            destination="Vers", 
                            volume="Nombre de joueurs", 
                            players='Joueurs')

    
    return sankey \
                * hv.Text(   0+35, 530, _('dim_country_code')            ).opts(color=text_color) \
                * hv.Text( 500+80, 530, _('dim_country_code_club')       ).opts(color=text_color) \
                * hv.Text(1000+15, 530, _('dim_international_name_club') ).opts(color=text_color) 


def sankey_ui(full_df, lang_id, theme='light'):

    options_raw = list(full_df.groupby(['country_name', 'country_flag', 'country_code']).groups.keys())
    options = { f"{i[0]} {i[1]}":i[2] for i in options_raw }
    
    select = pn.widgets.Select(name='Pick a team', 
                    options=options,
                    value='FRA',
                    width=120
                    )

    bound_fn = pn.bind(sankey_for_country_code,
                    country_code=select, 
                    sankey_full=build_sankey_full(full_df),
                    lang_id=lang_id, 
                    theme=theme)

    return pn.Column(
        pn.pane.Markdown("## Clubs d\'origine des joueurs"),
        select, 
        bound_fn)

    


def players_height_weight(full_df, lang_id, theme='light'):

    tooltips_raw = [
        (_('dim_international_name'), '@international_name'),
        (_('dim_field_position_hr'), '@{field_position_hr}'),
        (_('dim_age'), f"@age { _('years_old') }"),
        (_('dim_country_code'), '@country_name @country_flag'),
        (_('dim_height'), '@height cm'),
        (_('dim_weight'), '@weight kg'),
        (_('dim_international_name_club'), '@international_name_club, @country_name_club @country_flag_club')
    ]


    hover = HoverTool(tooltips=tooltips_raw)

    scatter = full_df.hvplot.scatter( x='weight', 
                                      y='height', 
                                      c='field_position_color',                                   
                                      by='field_position_hr',

                                      hover_cols=[ "international_name",
                                                    "field_position_hr",
                                                    "age",
                                                    "country_name",
                                                    "country_flag",
                                                    "country_name_club",
                                                    "country_flag_club",
                                                    "weight",
                                                    "height",
                                                    "international_name_club",],
                                      height=600, 
                                      width=800, 
                                      muted_alpha=0.1,
                                     tools=[hover],
                                     
                                    ) \
                            .opts(
                                  legend_position='bottom_right', 
                                  legend_opts={"title":None},
                                  shared_axes=False,
                                  show_grid=True) \
                            .redim.label(
                                   height=_('dim_height'), 
                                   weight=_('dim_weight'), 
                                   field_position_hr= _('dim_field_position_hr'),
                                   international_name= _('dim_international_name'),
                                   age = _('dim_age'),
                                   country_code = _('dim_country_code'),
                                   international_name_club = _('dim_international_name_club'),        
                                  ) 

    #shown_count = len(full_df.loc[ ~(full_df.height.isna() | full_df.weight.isna()) ])

    #subtitle = _('subtitle_players_weight_and_size').replace("{%shown%}", str(shown_count)).replace("{%total%}",str(len(full_df)) )
    
    #result = pn.Column(pn.pane.Markdown(f'''## {_('title_players_weight_and_size')}
    #_{subtitle}_'''), 
    #          scatter)
    
    return scatter



def players_height_weight_per_country(full_df,lang_id, theme):

    tooltips_raw = [
        (_('dim_country_code'), '@country_name'),
        (_('dim_height'), '@height cm'),
        (_('dim_weight'), '@weight kg'),
        ('', '@group_hr'),
    ]

    hover = HoverTool(tooltips=tooltips_raw)
    
    df_left = full_df.groupby('country_code').mean()[['height', 'weight']].reset_index()

    df_right = full_df.groupby(['country_code', 'group', 'group_hr']).size().reset_index()[['country_code', 'group', 'group_hr']]

    df = pd.merge(df_left, df_right, how="outer", on="country_code").sort_values('group_hr')
    
    df['country_name'] = df['country_code'].transform(lambda x:"%s %s"%( _(x, countries_translations(),lang_id),
                                                                         _(x, countries_translations(), 'flag')  )
                                                    )

    # The names of countries are of various lengths.
    # setting an offset to place all of them properly without overlapping is a challenge.
    # Furthermore, I haven't found a way to set a *variable* xoffset (even using hooks)
    # Simple and straightforward solution : set the offsets manually.

    # First, a base offset for all country names
    df['weight_offset'] = df['weight'] +  0.6
    df['height_offset'] = df['height']

    # Then, on-demand for some countries
    df.loc[ df['country_code'] =='TUR', "height_offset" ] -= 0.1
    df.loc[ df['country_code'] =='FRA', "height_offset" ] -= 0.1
    df.loc[ df['country_code'] =='POR', "height_offset" ] -= 0.1
    
    df.loc[ df['country_code'] =='SUI', "weight_offset" ] +=  0.1
    df.loc[ df['country_code'] =='MKD', "weight_offset" ] +=  0.1

    df.loc[ df['country_code'] =='ITA', "weight_offset" ] -=  0.9
    df.loc[ df['country_code'] =='ITA', "height_offset" ] -=  0.1    

    
    df.loc[ df['country_code'] =='BEL', "weight_offset" ] -=  1.1
    df.loc[ df['country_code'] =='BEL', "height_offset" ] +=  0.0    

    df.loc[ df['country_code'] =='NED', "weight_offset" ] += 0.1 
    df.loc[ df['country_code'] =='NED', "height_offset" ] -=  0.15
    
    df.loc[ df['country_code'] =='CZE', "weight_offset" ] += 0.3

    
    
    labels = hv.Labels(df, ['weight_offset', 'height_offset'], 'country_name',).opts(text_font_size='9pt',
                                                                      #xoffset=0.52,
                                                                      text_color='white'
                                                                                                 ) 
    
    #colormap = hv.Cycle.default_cycles['default_colors'][::-1]
    
    scatter = df.hvplot.scatter( x='weight', 
                                 y='height', 
                                 #c='group_hr',
                                 by='group_hr',    
                                size=30,
                                #cmap=colormap,
                                    hover_cols=[ "international_name",
                                                    "field_position_hr",
                                                    "age",
                                                    "country_name",
                                                    "country_flag",
                                                    "country_name_club",
                                                    "country_flag_club",
                                                    "weight",
                                                    "height",
                                                    "international_name_club",],
                                      height=600, 
                                      width=800, 
                                      muted_alpha=0,
                                     tools=[hover],
                                    ) \
                            .opts(
                                  legend_position='bottom_right', 
                                  legend_opts={"title":None},
                                  #padding=((0.1, 0.2), 0.1)
                                  xlim=(72,82),
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
    
    result = (scatter*labels).opts( shared_axes=False )
    return result


def legend_for_players_dim(lang_id):

    field_positions = list(field_positions_colors().keys())

    df = pd.DataFrame({
        'x':[0,1,2,3],
        'y':[0]*4,
        'field_position':[ _(x, lg_id=lang_id) for x in field_positions]  ,
        'color': [  field_positions_colors()[x] for x in field_positions ]
        
    })

    points = hv.Points(  df, ['x', 'y'] ).opts(color='color',
                                    size=6,
                                    )

    labels = hv.Labels(df, ['x', 'y'], 'field_position' ).opts(text_color='white', 
                                                            text_align='left',
                                                            xoffset=0.05)

    return (points*labels).opts(shared_axes=False, 
                                width=1300, 
                                height=80, 
                                xaxis=None,
                                yaxis=None, 
                                toolbar=None,
                                xlim=(-0.5,4),
                                ylim=(-1,1),
                                )

def players_dim_per_country_per_position(full_df, lang_id, theme, dimension='age'):

    tooltips_raw = [
        (_('dim_international_name'), '@international_name'),
        (_('dim_field_position_hr'), '@{field_position_hr}'),
        (_('dim_age'), f"@age { _('years_old') }"),
        (_('dim_country_code'), '@country_name @country_flag'),
        (_('dim_height'), '@height cm'),
        (_('dim_weight'), '@weight kg'),
        (_('dim_international_name_club'), '@international_name_club, @country_name_club @country_flag_club')
    ]

    hover = HoverTool(tooltips=tooltips_raw)

    df = full_df.set_index(["country_code", "field_position"]).reset_index()

    df['color'] = df['field_position'].transform(lambda x: field_positions_colors()[x] )
    df['country_name'] = df['country_code'] \
                                    .transform(lambda x:"%s %s"%(  _(x, countries_translations(), lang_id),
                                        _(x, countries_translations(), 'flag'))  ) 

    points =  hv.Points( df, ['country_name', dimension], 
                            ).opts( color='color', 
                                    #show_legend=False,
                                    jitter=0.2, 
                                    alpha=0.5, 
                                    size=6, 
                                    tools=[hover],
                                    height=600,
                                    width=1300, 
                                    xrotation=45, 
                                    show_grid=True,
                                    gridstyle = {
                                    'grid_line_color': 'lightgray', 
                                    #'grid_line_width': 1.5, 
                                    #'xgrid_bounds': (0, 0),
                                    'minor_xgrid_line_color': 'lightgray', 
                                    'xgrid_line_dash': [1, 4]},
                                    shared_axes=False,
                            ).redim.label(age=_('dim_age', lg_id=lang_id),
                                            weight=_('dim_weight', lg_id=lang_id),
                                            height=_('dim_height', lg_id=lang_id),
                                        country_name='Equipe') 

    legend = legend_for_players_dim(lang_id)

    return hv.Layout(legend + points).cols(1).opts(shared_axes=False,)
    

def teams_average_age(full_df, lang_id, theme):


    mean_ages_df = pd.DataFrame(full_df.groupby("country_code") \
                .mean()['age']\
                .sort_values(ascending=True)).reset_index()
    mean_ages_df['country_name'] = mean_ages_df['country_code'] \
                                    .transform(lambda x:"%s %s"%(  _(x, countries_translations(), lang_id),
                                        _(x, countries_translations(), 'flag'))  )

    mean_ages_df = mean_ages_df.set_index('country_name')


    mean_ages_df = mean_ages_df.sort_values(by='age')

    result = mean_ages_df.hvplot.barh(height=600) \
                        .opts(labelled=[], 
                            title="Age moyen des joueurs par équipe",
                            shared_axes=False,) \
                        .redim.label(age='Age moyen', country_name='Equipe') 
                        

    return result
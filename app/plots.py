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
                  fontsize={'yticks': 10}
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

                            fontsize={'yticks': 10}
                            
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



    count_per_country_club =count_per_country_club \
                                    .sort_values(by="country_name_club", ascending=False) \
                                    .sort_values(by="country_name", ascending=False)


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
                                        toolbar=None
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

    
    

    #count_per_club =count_per_club \
    #                                .sort_values(by="country_name_club", ascending=False) \
    #                                .sort_values(by="country_name", ascending=False)

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
                                    ) \
                                    .redim.values(x=count_per_club['international_name_club'].sort_values(), 
                                                    y=count_per_club['country_name'].sort_values() ) \
                                    .redim.label(country_name="Equipes", 
                                                international_name_club="Clubs des joueurs selectionnés", 
                                                count='Total') \

    return heatmap
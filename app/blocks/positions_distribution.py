from inspect import ClassFoundException
import panel as pn
from i18n import _, countries_translations, field_positions_colors, explanations
from bokeh.models import HoverTool

from .common import fix_flags_hook, sort_options, uses_shitdows
import pandas as pd
import holoviews as hv
from .base_block import BaseBlock

import os
import cache_manager 


from pdb import set_trace as bp

def positions_distribution_main(full_df, theme='light', sort="country_name", asc=True):

    sort_selector = pn.widgets.Select(
        name='',
        options=list(sort_options().keys()),
        value=list(sort_options().keys())[0],
        width=250)

    asc_cbox = pn.widgets.Checkbox(name=_('ascending'), value=True, width=80)

    bound_fn = pn.bind(positions_distribution_plot,
                       full_df=full_df,
                       theme=theme,
                       sort=sort_selector,
                       asc=asc_cbox
                       )

    result = pn.Column(
        pn.Row(pn.pane.Markdown(f'''### {_('positions_distribution_plot_title')}''', sizing_mode='stretch_width'),

               pn.pane.Markdown(_('sort_by')),
               sort_selector,
               asc_cbox),
        bound_fn
    )

    return result



def positions_distribution_plot(full_df, theme='light', sort="country_name", asc=True):

    plot_name = os.path.basename(__file__)[:-3] + f"_{theme}_{sort}_{asc}"

    plot_data = cache_manager.get_data(plot_name)
    if plot_data is None : 

        counts = full_df.groupby(['country_code', 'field_position']) \
            .size().reset_index(name="count").sort_values(by="country_code", ascending=True)

        counts['country_name'] = counts['country_code'].transform(lambda x: _(x, countries_translations()) )
        counts['country_flag'] = counts['country_code'].transform(lambda x: _(x, countries_translations(), 'flag'))
        counts['country_name_flag'] = counts['country_name'] + " " + counts['country_flag']


        maxis = counts.groupby('field_position').max().rename(
            columns={'count': 'maxi'})


        # default
        ordered_countries_names = counts.sort_values(
            'country_name', ascending=not asc)['country_name'].values

        
        # we use this to reorder using redim.values
        if sort in sort_options():
            sort = sort_options()[sort]
            if sort != "country_name":
                ordered_countries_names = counts[counts['field_position'] == sort].sort_values(
                    'count', ascending=not asc)['country_name_flag'].values

        positions = full_df.field_position.unique()

        cache_manager.cache_data(plot_name, (counts, maxis, ordered_countries_names, positions ))

    else:
        (counts, maxis, ordered_countries_names, positions) = plot_data
    
    fx_shitdows = 'fix_shitdows' if uses_shitdows() else ''

    tooltips = f"""
    <div style="width:200px">

        <div class="bk" style="display: table; border-spacing: 2px;">
            <div class="bk" style="display: table-row;">
                <div class="bk bk-tooltip-row-label" style="display: table-cell;">{_('dim_country_code')} : </div>
                <div class="bk bk-tooltip-row-value" style="display: table-cell;">
                    <span class="bk" data-value="">@country_name</span>
                    <span class="bk {fx_shitdows}" data-value="">@country_flag</span>
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

    final_plot = None

    for p in positions:

        max_for_p = maxis.loc[p]['maxi']

        count_serie = counts[ counts.field_position == p ]
       
        # TODO rework this
        names_serie = full_df[full_df.field_position == p].groupby(
            ['country_code', 'field_position'])['international_name'].apply(lambda x: ', '.join(x))
       
        df_for_p = pd.merge(count_serie,names_serie,how='left', on='country_code').set_index(['country_name_flag', 'field_position'])
       
        width = max(150, int(max_for_p*20)) + (100 if p == positions[0] else 0)

        plot = df_for_p.hvplot \
            .barh(stacked=True,
                  cmap=field_positions_colors(),
                  height=450,
                  width=width,
                  hover_cols=['country_name',
                              'country_flag', 
                              'field_position_hr',
                              'count',
                              'international_name', ],
                  tools=[hover]
                  ) \
            .opts(title=_(p+"_plural"),
                  show_legend=False,
                  xticks=[i for i in range(max_for_p)],
                  labelled=[],
                  fontsize={'yticks': 10, 'xticks': 10},
                  toolbar=None,
                  default_tools=[],
                  hooks=[fix_flags_hook]
                  ).redim.values(country_name_flag=ordered_countries_names)

        if final_plot is None:
            final_plot = plot
        else:
            final_plot += plot.opts(yaxis=None, )

    final_plot = final_plot.opts(shared_axes=False, toolbar=None, width=1200,)



    return final_plot


def positions_distribution_txt():
    return pn.Column(pn.Spacer(height=30),  
                        pn.pane.Markdown(explanations('positions_distribution')))


from .base_block import BaseBlock

class PositionsDistribution(BaseBlock):

    def __init__(self, full_df, theme):
        super(BaseBlock, self).__init__()
        self.main_plot = positions_distribution_main(full_df, theme)

    
    def items(self):
       
        items = [   pn.pane.Markdown(f'''## {_('positions_distribution_title')} '''),
                    pn.pane.Markdown(_('intro_positions_distribution'), ),
        ]

        if self.preloading:
        
            items.append( pn.Spacer(height=508, loading=True) )
            return items

        else:

            items.append( pn.Row(pn.Spacer(width=50),
                            self.main_plot,
                            positions_distribution_txt()
                        )
                    )
            return items 

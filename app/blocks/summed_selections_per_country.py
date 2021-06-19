from re import A
import panel as pn
from i18n import _, countries_translations, field_positions_colors, explanations
from bokeh.models import HoverTool

from .common import fix_flags_hook, br, default_hovertool, sort_options
import pandas as pd

import holoviews as hv

import os
import cache_manager 
from pdb import set_trace as bp

def summed_selections_per_country_main(full_df, theme, sort_key="total", asc=True):


    options = sort_options(field_positions=False, championships=True)
    

    sort_selector = pn.widgets.Select(
        name='',
        options=list(options.keys()),
        value=list(options.keys())[-1], # 'Total'
        width=250)

    asc_cbox = pn.widgets.Checkbox(name=_('ascending'), value=True, width=80)

    bound_fn = pn.bind(summed_selections_per_country_plot,
                       full_df=full_df,
                       theme=theme,
                       sort_key=sort_selector,
                       asc=asc_cbox
                       )

    result = pn.Column(
        pn.Row( pn.layout.spacer.HSpacer(),
               pn.pane.Markdown(_('sort_by')),
                sort_selector,
                asc_cbox),
        bound_fn
    )

    return result


def summed_selections_per_country_plot(full_df, theme, sort_key="Total", asc=True):

    options = sort_options(field_positions=False, championships=True)


    plot_name = os.path.basename(__file__)[:-3] + f"_{theme}_{sort_key}_{asc}"

    plot_data = cache_manager.get_data(plot_name)
    if plot_data is None : 

            
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

        if sort_key not in options:
            sort_key = options[-1]  # 'Total'
        else:
            sort_key = options[sort_key]
        
        
        # we use this to reorder using redim.values
        if sort_key == "country_name":
            ordered_countries_names = sum_sel_df['country_name'].sort_values(ascending=not asc).unique()

        else:
            ordered_countries_names = sum_sel_df[sum_sel_df['variable'] == sort_key].sort_values(
                'value', ascending=not asc)['country_name'].values

        cache_manager.cache_data(plot_name, (sum_sel_df, ordered_countries_names))


    else:

        sum_sel_df, ordered_countries_names =  plot_data


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
                                            xrotation=45, 

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





from .base_block import BaseBlock

class SummedSelectionsPerCountry(BaseBlock):

    def __init__(self, full_df, theme, dim="nbr_selections"):
        super(BaseBlock, self).__init__()
        self.main_plot = summed_selections_per_country_main(full_df, theme)

    
    def items(self):

        items = [   pn.Row(pn.Spacer(width=50), 
                            
                            pn.Column(
                                br(2),
                                pn.pane.Markdown(f''' {_('selections_subtitle_3')} ''', sizing_mode='stretch_width'),
                                br(),
                                pn.Spacer(height=508, loading=True) if self.preloading else self.main_plot  , 
                                br(),
                                pn.pane.Markdown(f''' {_('selections_conclusion')} ''', sizing_mode='stretch_width'),

                            )
                        ),
        
            ]

            
        return items
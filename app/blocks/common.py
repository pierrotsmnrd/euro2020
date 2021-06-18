import panel as pn
from bokeh.models import HoverTool
from i18n import _

from pdb import set_trace as bp

import holoviews as hv

def uses_shitdows():
    return ("Windows" in pn.state.headers['User-Agent']) or ('windows' in pn.state.headers['User-Agent'])


def fix_flags_hook(plot, element):

    # bp()
    
    # for k in plot.handles:
    #     try:
    #         plot.handles[k].text_font = "babelstone" 
    #         print(k)
    #     except:
    #         pass

    # for k in plot.handles:
    #     print(k)
    #     print( [ p for p in dir(plot.handles[k]) if 'font' in p ] )
    #     print( )

    

    if uses_shitdows():    
        plot.handles['yaxis'].major_label_text_font = "babelstone" 
        plot.handles['xaxis'].major_label_text_font = "babelstone" 
    
        
        if "glyph" in plot.handles: #: and not isinstance(element, hv.element.chart.Bars):
            try:
                plot.handles['glyph'].text_font = "babelstone"
                print("worked : ", element)
            except:
                pass 
           
            
            

        if 'text_1_glyph' in plot.handles: 
            print("handled text_1_glyph ")
            plot.handles['text_1_glyph'].text_font = "babelstone"
            plot.handles['text_1_glyph'].text_font = '42pt'
        

        # doesn't seem necessary
        # plot.handles['yaxis'].axis_label_text_font = "babelstone" 
        # plot.handles['xaxis'].axis_label_text_font = "babelstone" 
         
        


def br(n=1):
    return pn.pane.HTML("<br />"*n) 


def sort_options(field_positions=True, country_name=True, championships=False):

    result = {}

    if field_positions:

        field_positions = { _("FORWARD_plural"): "FORWARD",
                            _("MIDFIELDER_plural"): "MIDFIELDER",
                            _("DEFENDER_plural"): "DEFENDER",
                            _("GOALKEEPER_plural"): "GOALKEEPER",
                        }
        result = {**result, **field_positions}

    if country_name:
        result[_('dim_country_code')] =  "country_name"

    if championships:
        
                        # values must match with the name
                        # of the columns in 
                        # summed_selections_per_country_plot:sum_sel_df
                        
        championships = {
                            _('match_category_Euro') : 'Euro',
                            _('match_category_WorldCup') : 'WorldCup',
                            _('match_category_Friendly') : 'Friendly',
                            _('match_category_Total') : 'Total',
        }
        
        result = {**result, **championships}
            
    return result


def default_hovertool():

    tooltips_raw = [
        (_('dim_international_name'), '@international_name'),
        (_('dim_field_position_hr'), '@{field_position_hr}'),
        (_('dim_age'), f"@age { _('years_old') }"),
        (_('dim_country_code'), '@country_name @country_flag'),
        (_('dim_height'), '@height cm'),
        (_('dim_weight'), '@weight kg'),
        (_('dim_international_name_club'), '@international_name_club, @league_name'),
        (_('dim_nbr_selections'), '@nbr_selections'),
        (_('dim_nbr_selections_euro'), '@nbr_selections_euro'),
        (_('dim_nbr_selections_wcup'), '@nbr_selections_wcup')
    ]

    hover = HoverTool(tooltips=tooltips_raw)
    return hover


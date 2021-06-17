import panel as pn
from bokeh.models import HoverTool
from i18n import _

def uses_noto():
    return ("Windows" in pn.state.headers['User-Agent']) or ('windows' in pn.state.headers['User-Agent'])


def fix_flags_hook(plot, element):
    
    if uses_noto():    
        plot.handles['yaxis'].major_label_text_font = "noto"
    


def br(n=1):
    return pn.pane.HTML("<br />"*n) 


def sort_options():

    return {_('dim_country_code'): "country_name",
            _("FORWARD_plural"): "FORWARD",
            _("MIDFIELDER_plural"): "MIDFIELDER",
            _("DEFENDER_plural"): "DEFENDER",
            _("GOALKEEPER_plural"): "GOALKEEPER",
            }


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


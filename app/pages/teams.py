import panel as pn
import param

import i18n
from i18n import _

from .base_page import BasePage

import blocks
from blocks.common import br, uses_shitdows


from pdb import set_trace as bp

class TeamsPage(BasePage):

    def __init__(self, full_df, lang_id, country_code, theme='dark', ** params):

        super(TeamsPage, self).__init__(lang_id, theme, **params)

        self.full_df = full_df
        self.country_code = country_code
        self.theme=theme

    @param.depends("lang_id", "theme")
    def teams_list(self):

        filepath = '../i18n/wip_%s.md'%(self.lang_id)
        f = open(filepath, 'r')
        content = f.read()

        return  pn.pane.Markdown(content + " teams_list ", sizing_mode='stretch_width')
        

    @param.depends("lang_id", "theme", "received_gotit")
    def team_details(self):

        if not self.received_gotit:
            return pn.Column(pn.pane.HTML('<br />'), sizing_mode='stretch_width')



        items = []

        # Header = Country name + flag
        country_name = _(self.country_code, i18n.countries_translations() ) 
        country_flag = _(self.country_code, i18n.countries_translations(), "flag" ) 

        #flag_style = ''' font-family:'babelstone'; ''' if uses_shitdows() else ''
        flag_style = "font-family:'babelstone';" if uses_shitdows() else ''

        flag_style += "font-size: 30pt;"
        flag = f'''<span style="{flag_style}">{country_flag}</span>'''
        
        #title = pn.pane.Markdown(f"# {country_name} {flag}", sizing_mode='stretch_width')
        title = pn.pane.HTML(f"<h1> {country_name} {flag}</h1>", sizing_mode='stretch_width')
        title = pn.pane.HTML(f"{flag}&nbsp;<h1 style='display:inline;'>{country_name}</h1>", sizing_mode='stretch_width')
        items.append(title)
        items.append(br(2))


        # Body, first tab : Squad
        players = self.full_df[ self.full_df['country_code']  == self.country_code ].to_dict("records")
        squad = blocks.list_players.ListPlayers(players).render

        
        # Body, second tab : Sankey
        sankey_clubs = blocks.clubs_distribution_per_team.ClubsDistributionForTeam(self.full_df, self.country_code, self.theme)

        # Body, Third tab : age VS nbr selections
        age_selections = blocks.players_age_nbr_selections.PlayersAgeNbrSelectionsForTeam(self.full_df, self.country_code, self.theme)


        custom_tab_style = pn.pane.HTML('''
        <style>
        .bk-tab {
            width: 100px;
            text-align: center;
        }
        </style>
        ''')

        tabs = pn.Tabs(
            ( _('tab_squad') , squad ),
            (  _('dim_international_name_club_plural'), sankey_clubs.render),
            (  _('tab_selections'), age_selections.render),
            css_classes=["custom_tab"]
        )
        
        items += [custom_tab_style, tabs] 

        result = pn.Column(objects=items, sizing_mode='stretch_width')
        return result


        
    
    def build_main(self, theme):
          
        if self.country_code is None:
            theme.main.append(self.teams_list)
        else:
            theme.main.append(self.team_details)
        
        
        theme.main.append(pn.Spacer(height=30))

        
        return theme



        
        
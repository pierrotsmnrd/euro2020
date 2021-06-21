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

    @param.depends("lang_id", "theme", "received_gotit")
    def teams_list(self):

        '''
        filepath = '../i18n/wip_%s.md'%(self.lang_id)
        f = open(filepath, 'r')
        content = f.read()
        '''
        

        css = '''<style>
        table.groups_list {
            width:100%;
        }

        table.groups_list th {
            border-bottom: 1px solid #ddd;
        }

        table.groups_list tr.noborder th {
            border-bottom: 0px !important;
        }

        table.groups_list td {
            text-align: center;
            height:44px
        }

        table.groups_list td a {
            color:white;
            font-size:16px;
            text-decoration:none;
        }

        table.groups_list td a:hover {
            text-decoration:underline;
            font-weight:bold;
        }
        </style>
        '''
        css = pn.pane.HTML(css)

        groups_raw = self.full_df.sort_values(['group', 'country_name']).groupby(['group', 'country_code', 'country_flag']).groups.keys()


        
        groups = {}
        for g in groups_raw:
            if g[0] not in groups:
                groups[g[0]] = []
            groups[g[0]].append(  g[1:] )

        

        items = [css]
        for gletter in 'ABCDEF':
            title =  pn.pane.Markdown(f'''# {gletter} ''')  
            
            links = '''<table class='groups_list'><tr>'''
            links += ''.join( [  f'''<td width="25%"><a href='/teams?team_id={p[0]}&lg={i18n.get_lang_id()}'> { _(p[0], i18n.countries_translations()) } { p[1] }</a></td>'''  for p in groups[gletter]  ] )
            links += '''</tr></table>'''
            links =  pn.pane.HTML(links,  sizing_mode='stretch_width') 

            items.append( pn.Row(title, links, sizing_mode='stretch_width') )
            

        
        
        return  pn.Column(objects=items, sizing_mode='stretch_width')
        

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



        
        
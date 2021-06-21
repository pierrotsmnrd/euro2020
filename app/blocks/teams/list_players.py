import panel as pn
from ..common import uses_shitdows, table_markdown

from ..base_block import BaseBlock

from i18n import _
import i18n

from pdb import set_trace as bp
import pandas as pd

class ListPlayers(BaseBlock):

    def __init__(self, players ):
        super(BaseBlock, self).__init__()
        self.players = players



    
    def players_table_header(self):
        
        if i18n.get_lang_id() == 'fr':
            date = '6 Juin 2021' 
        else:
            date = 'June 6th 2021' 
        
        return f'''<thead>
         <tr class='noborder'>
            <th colspan='6'></th>
            <th colspan='4'>{_('dim_nbr_selections')} <span style='font-size:8pt;'>({date})</span></th>
          </tr>
          <tr>
            <th width="10%" colspan='2'></th>
            <th width="5%">{_('dim_age')}</th>
            <th width="5%">{_('dim_height')}</th>
            <th width="5%">{_('dim_weight')}</th>
            <th width="15%">{_('dim_international_name_club')}</th>

            <th width="5%">{_('match_category_Euro')}</th>
            <th width="5%">{_('match_category_WorldCup')}</th>
            <th width="10%">{_('match_category_Friendly')}</th>
            <th width="5%">{_('match_category_Total')}</th>
          </tr>
        </thead>'''






    def player_html_row(self, player):
        print(player)

        league_name = _(player['country_code_club'], i18n.countries_translations(), 'league')
        league_flag = _(player['country_code_club'], i18n.countries_translations(), 'flag')
        
        club_style = "font-family:'babelstone';" if uses_shitdows() else ''
        club = f'''{player['display_official_name']}<br />{league_name}&nbsp;<span style="{club_style}">{league_flag}</span>'''
        
        return f'''
            <tr>
                <td style='width:52px;'>       
                    <img src="{player['image_url']}" width="52" height="52" style='border-radius: 50%;'>
                </td>
                <td>{player['international_name']}</td>
                <td>{player['age']}</td>
                <td>{ int(player['height']) if not pd.isna(player['height']) else "-" }</td>
                <td>{ int(player['weight']) if not pd.isna(player['weight']) else "-" }</td>
                <td>{club}</td>
        
                <td>{  int(player['nbr_selections']) 
                                if not pd.isna(player['nbr_selections']) 
                                else 0  }</td>
                <td>{  int(player['nbr_selections_euro']) 
                                if not pd.isna(player['nbr_selections_euro']) 
                                else 0  }</td>
                <td>{  int(player['nbr_selections_wcup']) 
                                if not pd.isna(player['nbr_selections_wcup']) 
                                else 0  }</td>
                <td>{  int(player['nbr_selections_friendly']) 
                                if not pd.isna(player['nbr_selections_friendly']) 
                                else 0  }</td>    
            </tr>'''
 	
 	
 	
 	
    
    def items(self):
        
        table_html = ''
        for fp in ["FORWARD", "MIDFIELDER", "DEFENDER", "GOALKEEPER"]: 

                players = [ p for p in self.players if p['field_position'] == fp]

                rows = '\n'.join([ self.player_html_row(p) for p in players ])
                
                table_html += f'''
                <h2 style="margin-bottom:0px;">{ _(fp + "_plural")  } ({len(players)})</h2>
                <table class='players_list' >
                    {self.players_table_header(  )}
                    <tbody>
                    {rows}
                    </tbody>
                </table>
                <br /><br /><br />
                '''

        css = '''<style>
        table.players_list {
            width:100%;
        }

        table.players_list th {
            border-bottom: 1px solid #ddd;
        }

        table.players_list tr.noborder th {
            border-bottom: 0px !important;
        }

        table.players_list td {
            text-align: center;
        }
        </style>
        '''



        return pn.Column(pn.pane.HTML(table_html + css, sizing_mode='stretch_width'), 
                    sizing_mode='stretch_width') 



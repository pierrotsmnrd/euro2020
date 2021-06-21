import panel as pn
import param

import i18n
from i18n import _

from .base_page import BasePage

import blocks
from blocks.common import br

class OverviewPage(BasePage):

    def __init__(self, full_df, lang_id, theme='dark', ** params):

        super(OverviewPage, self).__init__(lang_id, theme, **params)

        self.full_df = full_df


    @param.depends("lang_id")
    def test_markdown(self):
        return pn.pane.Markdown(f" ** this is a test in _markdown_ ** : {self.lang_id} {self.selected_flag}  {self.theme}")


    @param.depends("lang_id", "theme", "received_gotit")
    def teams_chapter(self):
        
        gspec = pn.GridSpec(  sizing_mode='stretch_width', 
                              height=210, 
                              
                                )

        gspec[0  , 0:3] = pn.Row(pn.pane.PNG('https://upload.wikimedia.org/wikipedia/fr/3/32/UEFA_Euro_2020_logo.png', width=150))
        gspec[0   , 3:12] = pn.Column( pn.pane.Markdown(f'''## {_('title_overview')} '''), 
                                       pn.pane.Markdown(f'''{_('intro_overview')} '''))

        return gspec
    



    @param.depends("lang_id", "theme", "received_gotit")
    def players_chapter_1(self):

        if not self.received_gotit:
            #print("Chapter -> NOT got it ... ")
            return pn.pane.HTML("")
        

        items = []
        position_distribution = blocks.positions_distribution.PositionsDistribution(self.full_df, self.theme)
        items.append(position_distribution.render)

        result = pn.Column(objects=items, sizing_mode='stretch_width')
        return result


    @param.depends("lang_id", "theme", "received_gotit")
    def players_chapter(self):

        if not self.received_gotit:
            #print("Chapter -> NOT got it ... ")
            return pn.pane.HTML("")
        
        #print("Chapter -> GOT IT ! ")



        items = []

        countries_local_leagues = blocks.countries_local_leagues.CountriesLocalLeagues(self.full_df, self.theme)
        items+= [  br(2), countries_local_leagues.render ]

        leagues_distribution_per_team = blocks.leagues_distribution_per_team.LeaguesDistributionPerTeam(self.full_df, self.theme)
        items+= [ br(), leagues_distribution_per_team.render]

        leagues_distribution = blocks.leagues_distribution.LeaguesDistribution(self.full_df, self.theme)
        items += [ leagues_distribution.render ]

        countries_clubs = blocks.countries_clubs.ConutriesClubs(self.full_df, self.theme)
        items+= [ br(), countries_clubs.render ]

        clubs_distribution = blocks.clubs_distribution.ClubsDistribution(self.full_df, self.theme)
        items += [ clubs_distribution.render ]

        # Sankey, flags to fix on Windows
        clubs_distribution_per_team = blocks.clubs_distribution_per_team.ClubsDistributionPerTeam(self.full_df, self.theme) 
        items += [ clubs_distribution_per_team.render ]

        # flags to fix on Windows
        players_max_selections_per_country = blocks.players_max_selections_per_country.PlayersMaxSelectionsPerCountry(self.full_df, self.theme) 
        items += [ br(2), players_max_selections_per_country.render ]

        players_age_nbr_selections = blocks.players_age_nbr_selections.PlayersAgeNbrSelections(self.full_df, self.theme)
        items += [ players_age_nbr_selections.render ]

        summed_selections_per_country = blocks.summed_selections_per_country.SummedSelectionsPerCountry(self.full_df, self.theme)
        items += [ summed_selections_per_country.render ]


        

        items += [
        
            br(3),
            pn.layout.Divider(),
            pn.Row(pn.Spacer(width=50), 
                
                pn.Column(
                    pn.pane.Markdown(i18n.explanations(f'overview_footer'), sizing_mode='stretch_width'),
                    br(), 
                    
                    sizing_mode='stretch_width'
                )
                
                , sizing_mode='stretch_width'
            )               
        ]

        result = pn.Column(objects=items, sizing_mode='stretch_width')
        return result
    


    
    def build_main(self, theme):
          

        theme.main.append(self.teams_chapter) 
        
        # We load the first chapter independantly, because 
        # all the chapters are actually in one big pn.Column.
        # When loading the page, the column takes time to show up, because of all its content.
        # So by displaying the first chapter alone, in its own pn.Column, 
        # it's shown faster and gives a better user experience
        theme.main.append(self.players_chapter_1)
        theme.main.append(self.players_chapter)
        

        theme.main.append(pn.Spacer(height=30))

        
        return theme
        
from datetime import datetime as dt
from threading import main_thread

import pandas as pd

from pprint import pprint
import panel as pn

import i18n 


def positions_distribution_txt():
    
    return pn.Column(pn.Spacer(height=30),  
                        pn.pane.Markdown(i18n.explanations('positions_distribution')))


    
def countries_local_leagues_txt():
    
    return pn.pane.Markdown(i18n.explanations('countries_local_leagues'),
                                width=450) 



def leagues_distribution_per_team_txt():
    
    return pn.Row(pn.pane.Markdown(i18n.explanations('leagues_distribution_per_team') ,
                        width=200
            ) )

def leagues_distribution_txt():

    return pn.pane.Markdown(i18n.explanations('leagues_distribution') )
    

def countries_clubs_txt():
    return pn.pane.Markdown(i18n.explanations('countries_clubs'))

def clubs_distribution_txt():
    return pn.pane.Markdown(i18n.explanations('clubs_distribution'))

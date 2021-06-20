import panel as pn
import param

import i18n
from i18n import _

from .base_page import BasePage

import blocks
from blocks.common import br

class TeamsPage(BasePage):

    def __init__(self, full_df, lang_id, theme='dark', ** params):

        super(TeamsPage, self).__init__(lang_id, theme, **params)

        self.full_df = full_df


    @param.depends("lang_id", "theme")
    def main_chapter(self):

        filepath = '../i18n/wip_%s.md'%(self.lang_id)
        f = open(filepath, 'r')
        content = f.read()

        return  pn.pane.Markdown(content, sizing_mode='stretch_width')
        
    
    def build_main(self, theme):
          

        theme.main.append(self.main_chapter) 
        
        
        theme.main.append(pn.Spacer(height=30))

        
        return theme
        
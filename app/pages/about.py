import panel as pn
import param

import i18n
from i18n import _

from .base_page import BasePage

import blocks
from blocks.common import br

class AboutPage(BasePage):

    def __init__(self, lang_id, theme='dark', ** params):

        super(AboutPage, self).__init__(lang_id, theme, **params)


    @param.depends("lang_id", "theme")
    def main_chapter(self):

        filepath = '../i18n/about_%s.md'%(self.lang_id)
        f = open(filepath, 'r')
        content = f.read()

        return  pn.pane.Markdown(content, sizing_mode='stretch_width')
        

    def build_main(self, theme):        
        theme.main.append(self.main_chapter) 

    
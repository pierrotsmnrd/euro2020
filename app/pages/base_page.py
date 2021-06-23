import pandas as pd
from pprint import pprint

import panel as pn
import param

import i18n
from i18n import _
from pages.menu import menu
from blocks.common import uses_shitdows

from panel.template import DarkTheme

from pdb import set_trace as bp
# from blocks.common import br

class BasePage(param.Parameterized):

    received_gotit = param.Boolean(default=False)

    languages_dict = { 'fr':'🇫🇷', 'en':'🇬🇧/🇺🇸'}
    selected_flag = param.ObjectSelector(objects=list(languages_dict.values()), 
                                         default=languages_dict['en'])

    lang_id = param.ObjectSelector(objects=list(languages_dict.keys()), 
                                         default='en')

    theme = param.ObjectSelector(default="dark", objects=['light', 'dark'])

    def __init__(self, lang_id, theme='dark', ** params):

        super(BasePage, self).__init__(**params)

        self.lang_id = lang_id

        self.flag_selector = pn.widgets.Select.from_param(
            self.param.selected_flag,
            name="", #_('Language'),
            value=self.languages_dict[lang_id],
            width=80,
            css_classes=[ 'fix_shitdows'] if uses_shitdows() else []
            )

        self.flag_selector_watcher = self.flag_selector.param.watch(self.update_lang_id, ['value'], 
                                        onlychanged=False,

        )

        # self.flag_selector.jscallback(value='''
        #     window.location = location.href.split("?")[0] + "?lg=" + languages_dict[select.value] 
        # ''', args={"select": self.flag_selector,
        #            "languages_dict": {v: k for (k, v) in languages_dict.items()}
        #            }
        # )



        self.theme_selector = pn.widgets.Select.from_param(
            self.param.theme,
            name='Display mode',
            value=theme, 
            width=80
        )

    def update_lang_id(self, event):
        #print(self.selected_flag, flush=True)
        new_lang_id = dict((v,k) for k,v in self.languages_dict.items())[self.selected_flag]
        
        print("%s -> %s"%(self.lang_id, new_lang_id) , flush=True)

        i18n.set_lang_id(new_lang_id)
        self.lang_id = new_lang_id
        

    @param.depends("lang_id")
    def menu(self):
        print("render menu", self.lang_id)
        return menu('overview', self.lang_id)


    @param.depends("lang_id", "received_gotit")
    def header(self):

        if not self.received_gotit:
            return  pn.Row(pn.layout.spacer.HSpacer(),
                            pn.Row( pn.pane.Markdown(_("last_update") ),
                                 pn.Column(pn.layout.spacer.VSpacer(height=1), 
                         ) , 
                                    width=400)
                        )

        
        return  pn.Row(pn.layout.spacer.HSpacer(),
                        pn.Row( pn.pane.Markdown(_("last_update") ),
                                pn.Column(pn.layout.spacer.VSpacer(height=1), 
                                        self.flag_selector) , 

                                width=400)
                    )

    def gotit_checkbox(self):

        if not self.received_gotit:

            checkbox =  pn.widgets.Checkbox.from_param(self.param.received_gotit, 
                                name="gotit",
                                css_classes=['gotit-hide']
                            )


            trigger_on_fonts_loaded = pn.pane.HTML(''' <script> 
                                            
                                var fired = false;

                                var fontLoader = new FontLoader(["babelstone"], {
                                    "fontLoaded": function(font) {
                                            // One of the fonts was loaded
                                            console.log("font loaded: " + font.family);
                                    },
                                    "complete": function(error) {
                                        if (error !== null) {
                                            // Reached the timeout but not all fonts were loaded
                                            console.log(error.message);
                                            console.log(error.notLoadedFonts);
                                        } else {
                                            // All fonts were loaded
                                            console.log("all fonts were loaded");

                                            if ( !fired) {

                                                Array.from(document.getElementsByTagName('input')).forEach(function(item) {
                                                    if (item.nextSibling.innerHTML == 'gotit' ){
                                                        item.click()
                                                        item.remove();
                                                        fired = true;
                                                    }
                                                });


                                            }
                                            

                                        }
                                    }
                                }, 10000);
                                fontLoader.loadFonts();
                                            
                                            
                                            </script>''' )

            return pn.Row(checkbox, trigger_on_fonts_loaded, )
            
        return pn.Row()


    def build_main(self, theme):
        print(" should be masked by the child class")
        return 
    
    def view(self):
          
        
        if self.theme =='light':
            theme = pn.template.MaterialTemplate(title=_("main_title")  )
        else:
            theme = pn.template.MaterialTemplate(title=_("main_title") , 
                                                theme=DarkTheme,
                                                #main_max_width="1200px"
                                                )

        theme.header.append(self.header)
        theme.sidebar.append(self.menu)
        theme.sidebar.append(self.gotit_checkbox)

        self.build_main(theme)

        theme.header.append(pn.pane.HTML('''<script>
        function toggleMenu(){
            console.log("test");
            sidebar = document.getElementById("sidebar");
            if (sidebar.classList.contains('mdc-drawer--open') ) {
                sidebar.classList.remove("mdc-drawer--open");
            } else {
                sidebar.classList.add("mdc-drawer--open");
            }
        }

        var menubutton = document.getElementsByClassName('mdc-top-app-bar__navigation-icon')[0];
        var newbutton = menubutton.cloneNode();
        newbutton.innerHTML = "menu";
        newbutton.onclick = toggleMenu;

        menubutton.parentElement.replaceChild(newbutton, menubutton);

        toggleMenu()
        
        </script>
        
        '''))
        
        
        return theme
        
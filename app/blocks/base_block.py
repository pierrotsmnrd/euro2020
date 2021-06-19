import param
import panel as pn

from random import randint

class BaseBlock(param.Parameterized):

    preloading = param.Boolean(default=True)
    items = []

    def trigger_postload(self):
        self.preloading=False
        
    @param.depends('preloading')
    def render(self):
        pn.state.curdoc.add_timeout_callback(self.trigger_postload, 100 ) # 1000 *randint(5,15))
        return pn.Column(objects=self.items(), sizing_mode='stretch_width')

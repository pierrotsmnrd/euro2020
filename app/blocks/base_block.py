import param
import panel as pn

class BaseBlock(param.Parameterized):

    preloading = param.Boolean(default=True)
    items = []

    def trigger_postload(self):
        self.preloading=False
        
    @param.depends('preloading')
    def render(self, order=1):
        pn.state.curdoc.add_timeout_callback(self.trigger_postload, 100*order)
        return pn.Column(objects=self.items(), sizing_mode='stretch_width')

import panel as pn
import holoviews as hv

from pdb import set_trace as bp

def store(store_name, obj_name, obj):

    if store_name not in pn.state.cache:
        pn.state.cache[store_name] = {}

    pn.state.cache[store_name][obj_name] = obj
    print(f"stored {obj_name} in store {store_name}")

def restore(store_name, obj_name):

    if store_name not in pn.state.cache:
        return None

    if obj_name not in pn.state.cache[store_name]:
        return None

    obj = pn.state.cache[store_name][obj_name]
    print(f"restored {obj_name} from store {store_name}")
    return obj
    
    

def cache_plot(name, plot):
    store('plots', name, plot)
    pass

def get_plot(name):
    restore('plots', name)
    pass



def cache_data(name, data):
    store('data', name, data)
    
def get_data(name):
    return restore('data', name)
    


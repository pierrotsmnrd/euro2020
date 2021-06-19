import panel as pn
import holoviews as hv

import pickle

from pdb import set_trace as bp
import os

def store(store_name, obj_name, obj):

    if store_name not in pn.state.cache:
        pn.state.cache[store_name] = {}

    pn.state.cache[store_name][obj_name] = obj
    
    if store_name == 'plots':
        print(f"stored {obj_name} in store {store_name}")


def restore(store_name, obj_name):

    if 'nocache' in pn.state.session_args:
        return None

    dump_file = f"../app_data/cache/{store_name}/{obj_name}.pickle"
    has_dump = os.path.isfile(dump_file)

    is_cached = store_name in pn.state.cache and obj_name in pn.state.cache[store_name]


    if has_dump and not is_cached:
        # loads the dump and stores it in the cache
        with open(dump_file, 'rb') as f:
            obj =  pickle.load(f)
            store(store_name, obj_name, obj)
            
            if store_name == 'plots':
                print(f"restored {obj_name} from dump in {store_name}")

            return obj

    elif is_cached:
        obj = pn.state.cache[store_name][obj_name]
        
        if store_name == 'plots':
            print(f"restored {obj_name} from store {store_name}")

        return obj

    return None


def dump(store_name):
    
    os.makedirs(f"../app_data/cache/{store_name}", exist_ok=True)

    for k,v in pn.state.cache[store_name].items():
        with open(f'../app_data/cache/{store_name}/{k}.pickle', 'wb') as handle:
            pickle.dump(v, handle, protocol=pickle.HIGHEST_PROTOCOL)



def cache_plot(name, plot):
    store('plots', name, plot)
    
def get_plot(name):
    return restore('plots', name)
    
def cache_data(name, data):
    store('data', name, data)
    
def get_data(name):
    return restore('data', name)
    
def dump_data():
    dump('data')
    # dump('plots')

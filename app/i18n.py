import json
import panel as pn

_translations = None
def translations():
    global _translations
    if _translations is None : 
        with open("../i18n/translations.json", "r") as f:
            _translations = json.loads(f.read())

    return _translations
    

_countries_translations = None
def countries_translations():
    global _countries_translations
    if _countries_translations is None:
        with open("../i18n/countries_translations.json", "r") as f:
            _countries_translations = json.loads(f.read())
    
    return _countries_translations


_field_positions_colors = {
    'GOALKEEPER' : '#fc4f30',
    'FORWARD' : '#e5ae38', 
    'DEFENDER' :  '#6d904f', 
    'MIDFIELDER' : '#30a2da',
}
def field_positions_colors():
    return _field_positions_colors




def set_lang_id(lg_id):
    print("set lang : ", lg_id)
    pn.state.cookies['lg'] = lg_id
    


def get_lang_id():
    return pn.state.cookies['lg'] if 'lg' in pn.state.cookies else 'en'

def _(x, translations_dict=None, lg_id=None):
    
    if translations_dict is None:
        translations_dict = translations()
        
    if lg_id is None:
        lg_id = get_lang_id()
        
    if x in translations_dict:
        return translations_dict[x][lg_id]
    else:
        return x



def explanations(name):

    #print("EXPL ", name, _lang_id)

    filepath = '../i18n/explanations/%s_%s.md'%(name, get_lang_id())
    f = open(filepath, 'r')
    content = f.read()

    return content
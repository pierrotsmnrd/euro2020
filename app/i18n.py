import json


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



_lang_id = None
def set_lang_id(lg_id):
    global _lang_id
    _lang_id = lg_id


def _(x, translations_dict=None, lg_id=None):
    
    if translations_dict is None:
        translations_dict = translations()
        
    if lg_id is None:
        lg_id = _lang_id
        
    if x in translations_dict:
        return translations_dict[x][lg_id]
    else:
        return x
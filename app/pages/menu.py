import i18n
import panel as pn

def button(url, icon, name, selected, lang_id) :

    color = 'white' if selected else 'lightgray'

    lang_params = f"lg={lang_id}" if lang_id in i18n.available_languages() else ''

    final_url = url + f"?{lang_params}" if lang_params != "" else ""

    return f'''<button class="mdc-button mdc-button--outlined" onclick="location.href='/{final_url}';">
                <span class="mdc-button__ripple"></span>
                    <i class="material-icons mdc-button__icon" style="color:{color};" aria-hidden="true">{icon}</i>
                <span class="mdc-button__label" style="color:{color};">{name}</span>
                </button>'''
    

def menu(current_page, lang_id):

    #overview = button('dashboard', 'Overview', current_page=='overview')
    #teams = button('groups', 'Teams in details', current_page=='teams')

    overview = button('overview', 'mediation', i18n._('menu_overview') , current_page=="overview", lang_id = lang_id)
    teams = button('teams', 'groups', i18n._('menu_teams') , current_page=="overview", lang_id = lang_id)
    matches = button('matches', 'sports_soccer', i18n._('menu_matches') , current_page=="matches", lang_id = lang_id)
    about = button('about', 'info', i18n._('menu_about') , current_page=="about", lang_id = lang_id)

    return pn.Column(overview, teams, matches, about)

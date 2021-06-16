import i18n


def button(url, icon, name, selected):

    color = 'white' if selected else 'lightgray'

    return f'''<button class="mdc-button mdc-button--outlined" onclick="location.href='/{url}';">
                <span class="mdc-button__ripple"></span>
                    <i class="material-icons mdc-button__icon" style="color:{color};" aria-hidden="true">{icon}</i>
                <span class="mdc-button__label" style="color:{color};">{name}</span>
                </button>'''
    

def menu(current_page):

    #overview = button('dashboard', 'Overview', current_page=='overview')
    #teams = button('groups', 'Teams in details', current_page=='teams')

    overview = button('overview', 'groups', i18n._('overview') , current_page=="overview")
    matches = button('matches', 'sports_soccer', i18n._('matches') , current_page=="matches")
    about = button('about', 'info', i18n._('about') , current_page=="about")

    return '<br />'.join([overview, matches, about])




def button(icon, name, selected):

    color = 'white' if selected else 'lightgray'

    return f'''<button class="mdc-button mdc-button--outlined" onclick="location.href='/about';">
                <span class="mdc-button__ripple"></span>
                    <i class="material-icons mdc-button__icon" style="color:{color};" aria-hidden="true">{icon}</i>
                <span class="mdc-button__label" style="color:{color};">{name}</span>
                </button>'''
    

def menu(current_page):

    overview = button('dashboard', 'Overview', current_page=='overview')
    teams = button('groups', 'Teams in details', current_page=='teams')
    matches = button('sports_soccer', 'Matches', current_page=='overview')
    about = button('info', 'About', current_page=='about')

    return '<br />'.join([overview, matches, about])

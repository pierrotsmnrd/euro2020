# .... 
    @param.depends("lang_id", "theme")
    def players_chapter(self):


        #------------

        #players_selections_title
        #players_selections_subtitle


        items += [
            br(3),
            pn.pane.Markdown(f'''### {_('players_selections_title')} '''),

            pn.Row(pn.Spacer(width=50), 
                    pn.pane.Markdown(f''' {_('players_selections_subtitle')} ''', sizing_mode='stretch_width'),
                    
            ),
            
           
            pn.Tabs( 
                    ('All championships', pn.Row(  players_age_nbr_selections(self.full_df,  self.theme, dim="nbr_selections" ),
                                                  players_age_nbr_selections_txt("total")
                                    ) 
                    ),
                    ('UEFA Euro', pn.Row(  players_age_nbr_selections(self.full_df,  self.theme, dim="nbr_selections_euro"),
                                            players_age_nbr_selections_txt("euro")
                                    ) 
                    ),
                    ('FIFA World Cup', pn.Row(  players_age_nbr_selections(self.full_df,  self.theme, dim="nbr_selections_wcup"),
                                                 players_age_nbr_selections_txt("worldcup")
                                        ) 
                    ),
                    tabs_location='left'             
                )
        
        
           ]



        #------------

        items += [
            br(3),
            pn.pane.Markdown(f'''### {_('title_players_funfacts')}'''),

             pn.Row(pn.Spacer(width=50), 
                    pn.pane.Markdown(f'''Le physique des joueurs varient beaucoup d'un poste à l'autre. Regardons la répartition du poids et des taille selon leur position''')
            ),
            pn.Row(pn.Spacer(width=50),
                pn.Tabs( 
                    ('per country', pn.Row(players_height_weight_per_country(self.full_df, self.lang_id, self.theme))),
                    ('per position', pn.Row(players_height_weight(self.full_df, self.lang_id, self.theme) )),
                 tabs_location='left'
                )
            ),

            pn.Row(pn.Spacer(width=50), 
                    pn.pane.Markdown(f''' Nbr selections ''')
            ),
            pn.Row(pn.Spacer(width=50),
            #  pn.Tabs( 
            #         ('Total', players_age_nbr_selections(self.full_df, self.lang_id, self.theme, dim="nbr_selections" ) ),
            #         ('Euro', players_age_nbr_selections(self.full_df, self.lang_id, self.theme, dim="nbr_selections_euro") ),
            #         ('World Cup', players_age_nbr_selections(self.full_df, self.lang_id, self.theme, dim="nbr_selections_wcup") ),
                    
            #      tabs_location='left'
            #     )
            )
            
        ]




        items += [
            br(3),
            pn.pane.Markdown(f'''### {_('title_players_funfacts')}'''),

             pn.Row(pn.Spacer(width=50), 
                    pn.pane.Markdown(f'''Le physique des joueurs varient beaucoup d'un poste à l'autre. Regardons la répartition du poids et des taille selon leur position''')
            ),
            pn.Row(
                pn.Tabs( 
                    ('age',    pn.Row(players_dim_per_country_per_position(self.full_df, self.lang_id, self.theme, 'age'))),
                    ('height', pn.Row(players_dim_per_country_per_position(self.full_df, self.lang_id, self.theme, 'height') )),
                    ('weight', pn.Row(players_dim_per_country_per_position(self.full_df, self.lang_id, self.theme, 'weight') )),
                    ('selections', pn.Row(players_dim_per_country_per_position(self.full_df, self.lang_id, self.theme, 'nbr_selections') )),
                    
                 tabs_location='left'
                )
            ),
        ]

            

        result = pn.Column(objects=items, sizing_mode='stretch_width')

        return result


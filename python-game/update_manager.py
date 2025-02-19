import text_utility as TEXT

""" Updates game each frame and hold timer logics """

def handle_animation(game, delta_time, game_state):
    if game.menu_open: # This freezes/pauses the game if the options menu is open
        return 
    else:

        TEXT.update_typing_effect(game, delta_time) ## This is a key time calculation for the Typewriter effect

            ##----Tracks Title Screen transitions----#
        if game.stage == game_state.TITLE:
            game.time_in_state += delta_time
            if game.time_in_state > 14:
                game.stage = game_state.OUTSIDE
                game.time_in_state = 0.0
        
            ##----Updates house/wind animation----##
        if game.stage == game_state.OUTSIDE:
            game.time_in_state += delta_time
            current_state = game.states[game.state_index]
            if game.time_in_state >= game.durations[current_state]:
                # Move to the next state in the sequence
                #Each state corresponds to an animation frame, we loop through them here to create the animation based on time variables provided above
                game.state_index += 1
                # If we've gone past the last item, loop back to 0
                if game.state_index >= len(game.states):
                    game.state_index = 0

                # Reset the time in the new state
                game.time_in_state = 0.0

                new_state = game.states[game.state_index]

                # block/prevent playing sound on every frame
                if new_state != current_state:
                    
                    if new_state == "LEFT":
                        game.sound_manager.play_sfx("wind", volume=0.5)
                    elif new_state == "RIGHT":
                        game.sound_manager.play_sfx("wind", volume=.5)
                    elif new_state == "CENTER":
                        pass  

            ## ---- Handles Progress Bar ---- ##
        if game.stage == game_state.LOADING:
            
            game.frame_timer += delta_time

            if game.frame_timer >game.frame_rate *4:
                game.frame_timer -= game.frame_rate *4

            if not game.api_call_complete:
                # load progress bar with api is called
                game.loading_progress += delta_time / 5  # adjust speed
                game.loading_progress = min(game.loading_progress, 0.95)  # cap at 95%
            else:
                # finish progress bar if api is done loading first
                game.loading_progress += delta_time / 2  
                if game.loading_progress >= 1.0:
                    game.loading_progress = 1.0
                    if not game.connection_popup_open:
                        game.stage = game_state.READING_INTRO
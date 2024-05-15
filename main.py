from gpt4all import GPT4All

from prompts import GAME_SETUP_MESSAGE, GAMEMASTER_SYSTEM_MESSAGE, PLAYER_SYSTEM_MESSAGE

# kiva 
LLM_MODEL = "orca-mini-3b-gguf2-q4_0.gguf"

def print_gamestate(master_state, player_state):
    print(f"{master_state.current_chat_session} {player_state.current_chat_session[-1]}")

def main():
    try:
        GPU = GPT4All.list_gpus()[0]
    except Exception as e:
        print("no GPU found lol", e)
        quit()

    player = GPT4All(LLM_MODEL, device=GPU)
    game_master = GPT4All(LLM_MODEL, device=GPU)
    print("Starting...")
    with game_master.chat_session(system_prompt=GAMEMASTER_SYSTEM_MESSAGE):
        # lets start with temp 0, so we get always the same start for our epic adventure.
        game_master.generate(prompt=GAME_SETUP_MESSAGE, temp=0)  
        with player.chat_session(system_prompt=PLAYER_SYSTEM_MESSAGE):
            for x in range(3):
                player.generate(prompt=game_master.current_chat_session[-1])
                game_master.generate(prompt=player.current_chat_session[-1])
                print_gamestate(master_state=game_master.current_chat_session, player_state=player.current_chat_session)


if __name__ == "__main__":
    main()


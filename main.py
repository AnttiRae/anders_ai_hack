from gpt4all import GPT4All
from paramiko.client import SSHClient
import select
from prompts import PLAYER_SYSTEM_PROMPT, RECAP_SYSTEM_PROMPT, INSTRUCTIONS_TEXT
import time

#  This model needs a beefy computer. Using smaller models resulted in silly answers.
LLM_MODEL = "nous-hermes-llama2-13b.Q4_0.gguf"
GAME_COMMANDS = ["n", "s", "e", "w", "u", "h"]

def print_gamestate(master_state, player_state):
    print(f"{master_state.current_chat_session} {player_state.current_chat_session[-1]}")


def main():

    # setup gpu and model stuff
    try:
        GPU = GPT4All.list_gpus()[0]
    except Exception:
        print("No GPU found, running with no GPU :(")
        GPU = None

    if GPU is None:
        llm_player = GPT4All(LLM_MODEL)
    else:
        llm_player = GPT4All(LLM_MODEL, device=GPU)

    ssh_client = SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.connect("172.17.0.2", username='bilbo', password='bilbo')
    #  stdin, stdout, stderr = ssh_client.exec_command('cd BashVenture; ./adventure.sh')
    transport = ssh_client.get_transport()
    channel = transport.open_session()
    channel.get_pty()
    channel.exec_command('cd BashVenture; ./adventure.sh')
    time.sleep(5)

    full_game_output = ''
    context = ''
    recap = ''

    with llm_player.chat_session(system_prompt=PLAYER_SYSTEM_PROMPT):
        while True:
            # readable list, writable list, exception list. Maybe I'll use them...
            rl, wl, xl = select.select([channel], [], [], 4)
            game_output = ''

            if len(rl) > 0:
                game_output = channel.recv(1024).decode()
                context += game_output
                full_game_output += game_output
                print(game_output)

            else:  # game seems to be waiting for user input!
                print('context:', context)
                if '[ENTER]' in context:
                    channel.send(b'\n')
                    print('entered enter')
                    context = ''
                elif '>' in context:
                    full_game_output += game_output
                    llm_input = context.split("--- Classic Adventure for Bash ---")[-1].strip()
                    print('lets ask for help from our AI friend')
                    game_command = None
                    confused = False
                    while True:
                        if confused:
                            llm_input = recap + INSTRUCTIONS_TEXT
                        llm_player.generate(prompt=llm_input, max_tokens=1, temp=0.8, repeat_last_n=564, repeat_penalty=1.5)
                        print('our AI friend said this:', llm_player.current_chat_session[-1]["content"])
                        game_command = llm_player.current_chat_session[-1]['content'].strip()

                        if game_command.strip() in GAME_COMMANDS:
                            confused = False
                            break
                        else:
                            print("AI friend got confused... Trying to reset and recap story")
                            confused = True
                            #  Resetting the context should get rid of any silly answers the model sometimes gives us.
                            #  Downside being that the model wont remember what it has done in the past. -> infinite loop
                            #  Lets make a recap of the story so far and use this after reset
                            #  Hacky way to reset context, it's a hackathon after all
                            llm_player._history = [{"role": "assistant", "content": RECAP_SYSTEM_PROMPT}]
                            llm_player.generate(prompt=full_game_output[-500:])
                            recap = llm_player.current_chat_session[-1]['content']
                            print('Story recap: ', recap)
                            llm_player._history = [{"role": "assistant", "content": PLAYER_SYSTEM_PROMPT}]


                    game_command = f"{game_command}\n"
                    channel.send(bytes(game_command, 'utf-8'))
                

                time.sleep(5)

if __name__ == "__main__":
    main()


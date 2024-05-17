from gpt4all import GPT4All
from paramiko.client import SSHClient
import select
from prompts import PLAYER_SYSTEM_MESSAGE
import time

LLM_MODEL = "orca-mini-3b-gguf2-q4_0.gguf"


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

    vitsi_muuttuja_lol = ''

    while True:
        # readable list, writable list, exception list. Maybe I'll use them...
        rl, wl, xl = select.select([channel], [], [], 4)
        game_output = ''
        if len(rl) > 0:
            game_output = channel.recv(1024).decode()
            vitsi_muuttuja_lol += game_output
            print(game_output)

        else:  # game seems to be waiting for user input!
            print('lollero', vitsi_muuttuja_lol)
            if '[ENTER]' in vitsi_muuttuja_lol:
                print('commence pressing of the enter')
                channel.send(b'\n')
                print('entered enter')
                vitsi_muuttuja_lol = ''
            elif '>' in vitsi_muuttuja_lol:
                print('oh no we must ask LLM FOR HELP!!!!')
                llm_input = vitsi_muuttuja_lol.split("--- Classic Adventure for Bash ---")[-1].strip()
                print('lets ask this from our AI friend:', llm_input)
                with llm_player.chat_session(system_prompt=PLAYER_SYSTEM_MESSAGE):
                    llm_player.generate(prompt=llm_input)
                    print('our AI friend said this:', llm_player.current_chat_session[-1])


if __name__ == "__main__":
    main()


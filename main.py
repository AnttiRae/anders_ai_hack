from gpt4all import GPT4All, gpt4all

try:
    GPU = GPT4All.list_gpus()[0]
except Exception as e:
    print("no GPU found lol", e)
    quit()

model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf", device=GPU)

with model.chat_session(system_prompt="You are a player of text adventure game. You must choose your actions wisely and make beneficial choices. Dont mention anything about being an AI or being unable to do physical things. You must end your answer always with a decision for the player. The player will not make any decisions"):
    response = model.generate(prompt="You are presented with a set doors. On the left you see a door with a skull and bones symbol. On your right you see a door with a symbol of food. What do you do?", temp=0)
    print(model.current_chat_session[2])


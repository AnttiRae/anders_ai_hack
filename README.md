# AI hackathon entry
Introducing top of the line text-based game player AI solution. Coming to your terminal hopefully never.
[See demo video](https://www.youtube.com/watch?v=PAD4v-GKBt4)

## How it works
- Make a SSH connection to BashVentures running in docker container with SSH connections enabled
- Read game state
- Pass game state to model that has been told to play the game
- Get model response
    - Check that response is a valid game command
    - if not, reset the model and tell it to recap the story so far and retry.
- Pass response to game and repeat from step 2

## Does it work?
- Yes, but not really. It tends to get stuck in a loop or just do random things.


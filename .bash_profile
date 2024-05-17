#!/bin/bash
# .bash_profile

# Get the aliases and functions
if [ -f ~/.bashrc ]; then
        . ~/.bashrc
fi

# User specific environment and startup programs
if [[ $(pgrep -af "sshd.*"$USER |wc -l) -gt 0 ]];  then
  cd BashVenture && ./adventure.sh
fi

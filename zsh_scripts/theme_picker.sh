#!/bin/bash

# List of strings
strings=("dusk" "embers" "glacial" "iron_gold" "matrix")

# Get the length of the array
length=${#strings[@]}

# Generate a random index
index=$(( RANDOM % length + 1 ))

# Set the randomly selected string to a variable
selected_string=${strings[$index]}

export TERMINAL_THEME="$selected_string"
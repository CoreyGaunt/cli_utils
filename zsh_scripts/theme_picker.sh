#!/bin/bash

# List of strings
strings=("dreambyte" "dusk" "emberglow" "embers" "glacial" "iron_gold" 
        "matrix" "moondust" "neon_void" "retroberry" "solstice" 
        "terminal_flux" "verdant")

# Create cache directory if it doesn't exist
cache_dir="/Users/corey_gaunt/Documents/Personal/theme_picker/.cache"
mkdir -p "$cache_dir"

# Build cache that will persist between runs
strings_cache_file="$cache_dir/used_themes.txt"

# Initialize cache array
strings_cache=()

# Check if the cache file exists and read it
if [[ -f "$strings_cache_file" ]]; then
    # Read the cache file into the array
    while IFS= read -r line; do
        strings_cache+=("$line")
    done < "$strings_cache_file"
fi

# Get the length of the original strings array
length=${#strings[@]}

# If all themes have been used, clear the cache
if [[ ${#strings_cache[@]} -ge $length ]]; then
    strings_cache=()
fi

# Filter out already used themes
available_themes=()
for theme in "${strings[@]}"; do
    if [[ ! " ${strings_cache[@]} " =~ " ${theme} " ]]; then
        available_themes+=("$theme")
    fi
done

# Get the length of available themes
available_length=${#available_themes[@]}

# Generate a random index from available themes
index=$(( RANDOM % available_length + 1))

# Set the randomly selected string to a variable
selected_string=${available_themes[$index]}

# Add the selected theme to the cache
strings_cache+=("$selected_string")

# Write the updated cache to the file
printf "%s\n" "${strings_cache[@]}" > "$strings_cache_file"

export TERMINAL_THEME="$selected_string"

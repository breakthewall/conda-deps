#!/bin/bash

# This script will list all the dependencies
# of a given conda package
pkg=$1
if [ -z "$pkg" ]; then
    echo "Usage: $0 <package>"
    exit 1
fi

# Function to add new dependencies from one list to another
function add_deps {
    local _deps=$1
    local _all_deps=$2
    for dep in $_deps; do
        if [[ ! " ${_all_deps[@]} " =~ " ${dep} " ]]; then
            _all_deps+=($dep)
        fi
    done
    echo ${_all_deps[@]}
}

# Get the list of conda dependencies
all_deps=()
deps=$(conda tree depends $pkg)

# Add the dependencies to the list
all_deps=$(add_deps "$deps" "$all_deps")

# Print the list of dependencies
echo ${all_deps[@]}
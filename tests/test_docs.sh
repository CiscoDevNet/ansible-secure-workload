#!/usr/bin/env bash
# This script is used to run the ansible-doc command and verify that the 
# doc string will render.  If it does, great, if not, it will exit with error code 1

declare -a arr=("tetration_application"
                "tetration_inventory_filter"
                "tetration_rest"
                "tetration_role"
                "tetration_scope_commit_query_changes"
                "tetration_scope_query"
                "tetration_scope"
                "tetration_software_agent_query"
                "tetration_software_agent"
                "tetration_user"
                )

for i in "${arr[@]}"
do
    ansible-doc $i | cat

    if [ $PIPESTATUS -ne 0 ]; then
        exit 1 
    fi
done
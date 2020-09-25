#!/usr/bin/env bash
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
    ansible-doc $i | cat > $i.txt

    if [ $PIPESTATUS -ne 0 ]; then
        exit 1 
    fi
done
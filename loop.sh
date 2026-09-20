#!/bin/bash
routes=('/' '/kunlik' '/kategoriyalar' '/qoshish' '/haqida' '/qoidalar' '/kirish')
for route in "${routes[@]}"; do
    echo -n "$route "
    curl -s -o /dev/null -w "%{http_code}" "http://localhost$route"
    echo
done

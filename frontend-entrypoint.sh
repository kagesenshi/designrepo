#!/bin/sh

# Replace localhost:8000 with BACKEND_URL if it exists
if [ -n "$BACKEND_URL" ]; then
    # Derive WS URL from BACKEND_URL
    # If https://... then wss://...
    # If http://... then ws://...
    case "$BACKEND_URL" in
        https://*) WS_BACKEND_URL=$(echo "$BACKEND_URL" | sed 's|^https://|wss://|') ;;
        http://*)  WS_BACKEND_URL=$(echo "$BACKEND_URL" | sed 's|^http://|ws://|') ;;
        *)         WS_BACKEND_URL="$BACKEND_URL" ;; # Fallback
    esac

    echo "Replacing http://localhost:8000 with $BACKEND_URL"
    echo "Replacing ws://localhost:8000 with $WS_BACKEND_URL"

    # Search for reflex-env-*.js and perform replacements
    for file in /usr/share/nginx/html/assets/reflex-env-*.js; do
        if [ -f "$file" ]; then
            sed -i "s|http://localhost:8000|$BACKEND_URL|g" "$file"
            sed -i "s|ws://localhost:8000|$WS_BACKEND_URL|g" "$file"
        fi
    done
fi

# Execute nginx
exec nginx -g "daemon off;"
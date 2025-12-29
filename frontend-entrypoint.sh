#!/bin/sh

if [ -n "$BACKEND_URL" ]; then
    echo "Updating reflex-env-*.js with base URL: $BACKEND_URL"

    # Identify if relative path before stripping trailing slash
    if echo "$BACKEND_URL" | grep -q "^/"; then
        IS_RELATIVE=true
    else
        IS_RELATIVE=false
    fi

    # Normalize by stripping trailing slash
    BACKEND_URL=$(echo "$BACKEND_URL" | sed 's|/$||')

    if [ "$IS_RELATIVE" = "false" ]; then
        case "$BACKEND_URL" in
            https://*) WS_BASE=$(echo "$BACKEND_URL" | sed 's|^https://|wss://|') ;;
            http://*)  WS_BASE=$(echo "$BACKEND_URL" | sed 's|^http://|ws://|') ;;
            *)         WS_BASE="$BACKEND_URL" ;;
        esac
    fi

    for file in /usr/share/nginx/html/assets/reflex-env-*.js; do
        if [ -f "$file" ]; then
            if [ "$IS_RELATIVE" = "true" ]; then
                # Relative path (e.g., /be) - use JS expressions for dynamic origin
                cat <<EOF > "$file"
var e = {
    PING: \`\${window.location.origin}${BACKEND_URL}/ping\`,
    EVENT: (window.location.protocol === 'https:' ? 'wss://' : 'ws://') + window.location.host + \`${BACKEND_URL}/_event\`,
    UPLOAD: \`\${window.location.origin}${BACKEND_URL}/_upload\`,
    AUTH_CODESPACE: \`\${window.location.origin}${BACKEND_URL}/auth-codespace\`,
    HEALTH: \`\${window.location.origin}${BACKEND_URL}/_health\`,
    ALL_ROUTES: \`\${window.location.origin}${BACKEND_URL}/_all_routes\`,
    TRANSPORT: \`websocket\`,
    TEST_MODE: !1
};
export { e as t };
EOF
            else
                # Absolute path (e.g., http://host:port)
                cat <<EOF > "$file"
var e = {
    PING: \`${BACKEND_URL}/ping\`,
    EVENT: \`${WS_BASE}/_event\`,
    UPLOAD: \`${BACKEND_URL}/_upload\`,
    AUTH_CODESPACE: \`${BACKEND_URL}/auth-codespace\`,
    HEALTH: \`${BACKEND_URL}/_health\`,
    ALL_ROUTES: \`${BACKEND_URL}/_all_routes\`,
    TRANSPORT: \`websocket\`,
    TEST_MODE: !1
};
export { e as t };
EOF
            fi
        fi
    done
else
    echo "BACKEND_URL not set. Skipping configuration."
fi

# Execute nginx
exec nginx -g "daemon off;"

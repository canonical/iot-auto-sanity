#!/bin/bash

# If cloud-init nocloud seed (user-data) is exist,
# change the default account/password with ubuntu/ubuntu
USERDATA="/target/var/lib/cloud/seed/nocloud/user-data"
if [ -f "$USERDATA" ]; then
    rm "$USERDATA"
    cat > "$USERDATA" <<EOF
#cloud-config
chpasswd:
  expire: False
  users:
    - name: ubuntu
      password: ubuntu
      type: text
EOF
echo "The "$USERDATA" is hacked!"
else
echo "The "$USERDATA" is not exist, skipped."
fi

#!/bin/sh

# Terminate wsl: https://stackoverflow.com/questions/66375364
# Restart nginx: sudo service nginx restart
# Dump nginx config: sudo nginx -T

# sudo su -
sqlite3 user.db < ./user.sql
sqlite3 ./var/primary/mount/game.db < ./game.sql
sqlite3 word.db < ./word.sql
sqlite3 score.db < ./score.sql
sudo service nginx restart #&& foreman start --formation userapp=1,gameapp=3,scoreapp=1

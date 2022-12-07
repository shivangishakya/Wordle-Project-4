# appfull: ./hypercorn-wrapper.sh app --reload --debug --bind app.local.gd:$PORT --access-logfile - --error-logfile - --log-level DEBUG
# appless: ./hypercorn-wrapper.sh app --debug --bind app.local.gd:$PORT --access-logfile - --error-logfile - --log-level DEBUG

# app: ./hypercorn-wrapper.sh app --reload --debug --bind app.local.gd:$PORT --access-logfile - --error-logfile - --log-level DEBUG

# appdev: ./hypercorn-wrapper.sh app --debug --bind app.local.gd:$PORT --access-logfile - --error-logfile - --log-level DEBUG

# appdev: ./hypercorn-wrapper.sh app --debug --bind app.local.gd:5678

# primarydb: sudo su -c "./bin/litefs -config ./var/primary/litefs.yml"
# secondarydb: sudo su -c " ./bin/litefs -config ./var/secondary/litefs.yml"

#primarydb: sudo su -c "./bin/litefs -config ./etc/primary.yml"
#secondarydb: sudo su -c "./bin/litefs -config ./etc/secondary.yml"
#tertiarydb: sudo su -c "./bin/litefs -config ./etc/tertiary.yml"

userapp: ./hypercorn-wrapper.sh user --bind app.local.gd:$PORT
scoreapp: ./hypercorn-wrapper.sh scoring --bind app.local.gd:5400
#gameapp: ./hypercorn-wrapper.sh game --bind app.local.gd:$PORT
primary: ./bin/litefs -config ./etc/primary.yml
secondary: ./bin/litefs -config ./etc/secondary.yml
tertiary: ./bin/litefs -config ./etc/tertiary.yml

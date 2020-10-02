#!/bin/bash
while [ true ];
do
	sleep 5
	echo start_script
	sudo git fetch --all && sudo git reset --hard origin/master && sudo jupyter  nbconvert --to script *.ipynb && sudo python3 script_update_data.py > /home/pi/Documents/covid-19/cronlogs 2>&1
	sleep 60
done

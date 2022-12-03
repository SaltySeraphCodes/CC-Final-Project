#! /bin/bash
#echo "day= $day"
# First check if it is wekend
currenttime=$(date +%H:%M)

if [[ $(date +%u) -eq 5 ]] ; then
	if [[ "$currenttime" > "16:10" ]]; then
		echo "The market is closed- $date"
		exit 0
	fi
fi

if [[ $(date +%u) -eq 6 ]] ; then
     	echo "This script shouldn't even run on saturdays"
	exit 1
fi


if [[ $(date +%u) -eq 7 ]] ; then
	if [[ "$currenttime" < "16:50" ]]; then
		echo $currenttime
		echo "The market is not open yet- $date"
		exit 0
	fi
fi



#cd /home/canthony/projects/Ktrade/KTRADER/Data/ #
source ../Environments/ReaperEnv/bin/activate

currency=$1
action=$2
interval_choice=$3
verbose=$4

if [[ $currency = "" ]]
then
        currency="all"
fi


if [[ $action = "" ]]
then
        action="update"
fi

if [[ $interval_choice = "" ]]
then
        interval_choice="D"
fi
if [[ $verbose = "" ]]
then
        verbose="false"
fi


if [[ $interval_choice = "M" ]]
then
        interval_options=('M5')
fi
if [[ $interval_choice = "H" ]]
then
        interval_options=('M5' 'H1')
fi
if [[ $interval_choice = "D" ]]
then
        interval_options=('M5' 'H1' 'D')
fi


date=$(date)
start_time="$(date -u +%s)"

echo ""
echo ""
echo "========================  Starting data processing at: $date ==============================="


if [[ $currency = "all" ]]
then
        while read -r currency; do
                for interval in "${interval_options[@]}"
                do
                        echo "------------ Performing $action on $currency at Interval: $interval  --------------"
                        python3 data_poster.py "$currency" "$interval" "$action" "$verbose"
                done
        done <active_pairs.txt
else


        if  grep -qF "$currency" currency_pairs.txt;then
                for interval in "${interval_options[@]}"
                do
                        echo "------------ Performing $action on $currency at Interval: $interval  --------------"
                        python3 data_poster.py "$currency" "$interval" "$action" "$verbose"
                done
        else
                echo "Chosen Currency: $currency is not supported"
        fi
fi

date=$(date)
end_time="$(date -u +%s)"
elapsed=elapsed="$(($end_time-$start_time))"
echo "======================== Finished data processing at: $date ================================"
echo "Elapsed Time: $elapsed Seconds"
echo ""
echo ""
exit 0


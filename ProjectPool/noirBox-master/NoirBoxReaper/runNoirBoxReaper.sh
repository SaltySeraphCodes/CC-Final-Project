#! /bin/bash
#echo "day= $day"
# First check if it is wekend
currenttime=$(date +%H:%M)

#if [[ $(date +%u) -eq 5 ]] ; then
#	if [[ "$currenttime" > "16:10" ]]; then
#		echo "The market is closed- $date"
#		exit 0
#	fi
#fi

#if [[ $(date +%u) -eq 6 ]] ; then
#     	echo "This script shouldn't even run on saturdays"
#	exit 1
#fi


#if [[ $(date +%u) -eq 7 ]] ; then
#	if [[ "$currenttime" < "16:50" ]]; then
#		echo $currenttime
#		echo "The market is not open yet- $date"
#		exit 0
#	fi
#fi



#cd /home/canthony/projects/Ktrade/KTRADER/Data/ #
source ../Enviornments/ReaperEnv/bin/activate 

profile=$1
currency=$2
interval_choice=$3
action=$4
verbose=$5

if [[ $profile = "" ]]
then
        profile="BroDeuxDemo"
fi

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
        interval_choice="H1"
fi

if [[ $verbose = "" ]]
then
        verbose="false"
fi


if [[ $interval_choice = "M" ]]
then
        interval_options=('M5' 'M15')
fi
if [[ $interval_choice = "H" ]]
then
        interval_options=('M5' 'M15' 'H1' 'H4')
fi

if [[ $interval_choice = "D" ]]
then
        interval_options=('M5' 'M15' 'H1' 'H4' 'D')
fi


date=$(date)
start_time="$(date -u +%s)"

echo ""
echo ""
echo "========================  Starting data reaping  at: $date ==============================="


python3 NoirBoxReaper.py "$profile" "$currency" "$interval_choice" "$action" "$verbose"
#if [[ $currency = "all" ]]
#then
#        while read -r currency; do
#                for interval in "${interval_options[@]}"
#                do
#                        echo "------------ Performing $action on $currency at Interval: $interval  --------------"
#                        python3 NoirBoxReaper.py "$profile" "$currency" "$interval" "$action" "$verbose"
#                done
#        done <active_pairs.txt
#else
#
#	echo "Reading pair"
#        if  grep -F "$currency" currency_pairs.txt;then
#		echo "Found pair"
#                for interval in "${interval_options[@]}"
#                do
#                        echo "------------ Performing $action on $currency at Interval: $interval  --------------"
#                        python3 NoirBoxReaper.py "$profile" "$currency" "$interval" "$action" "$verbose"
#                done
#        else
#                echo "Chosen Currency: $currency is not supported"
#        fi
#fi

date=$(date)
end_time="$(date -u +%s)"
elapsed=elapsed="$(($end_time-$start_time))"
echo "======================== Finished data reaping  at: $date ================================"
echo "Elapsed Time: $elapsed Seconds"
echo ""
echo ""
exit 0


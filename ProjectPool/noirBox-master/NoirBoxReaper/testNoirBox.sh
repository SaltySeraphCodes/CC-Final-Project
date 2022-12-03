#! /bin/bash
#cd /home/canthony/projects/Ktrade/KTRADER/Data/ # for when inserted into cronJob, alter to current working Directory
source ../Enviornments/ReaperEnv/bin/activate 

echo "========================  Starting NBR  tests  ==============================="
#default parameters   ProfileName Ticker Granularity action verbose
#./runNoirBoxReaper.sh BroDeuxDemo EUR_USD H1 load True
./runNoirBoxReaper.sh BroDeuxDemo EUR_USD H1 update True

echo ""
echo "Finished Tests"
exit 0


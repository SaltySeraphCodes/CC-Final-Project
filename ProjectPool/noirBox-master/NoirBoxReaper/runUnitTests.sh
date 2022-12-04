#! /bin/bash
#cd /home/canthony/projects/Ktrade/KTRADER/Data/ # for when inserted into cronJob, alter to current working Directory
source ../Enviornments/ReaperEnv/bin/activate 

echo "========================  Starting unit tests  ==============================="

python3 unitTester.py

echo ""
echo "Finished Unit Tests"
exit 0


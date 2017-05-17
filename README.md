# tuplemaker

This package is to be used on uboonedaq-evb machine only, because apparently that's only place where datatypes compiles.
Well, it might get compiled at another place wherever offline datatypes is built.
But for now I require (in the config script) that this is used @ uboonedaq-evb.fnal.gov machine.
You need to go through ubdaq-prod-ws01 ssh gateway machine.

## 1st time only action (INSTALLATION + CONFIG)
First, set up git ups
```
source /uboonenew/setup_online.sh
setup git
```

Then clone this repository...
```
cd where_you_install_tuplemaker
git clone https://github.com/drinkingkazu/tuplemaker
cd tuplemaker
```

Setting up 1st time will include pulling + building necessary repository
```
source setup_tuplemaker.sh
```

## 2nd time and future (CONFIG)
After log-in, just do:
```
cd where_you_install_tuplemaker
source setup_tuplemaker.sh
```

## Stand-alone Binary Executable
You can run a binary "tuplemaker"
```
tuplemaker UBDAQ_FILE [OUT_FILENAME, NUM_EVENTS]
```
where..
  - UBDAQ_FILE is an input daq file
  - OUT_FILENAME is output root file name (optional)
  - NUM_EVENTS is # of events to process (from 0, optional).

## Launching Example Processing
There is a python script I wrote to automatically process data files sequentially.
This is under ```process_area``` directory.
You see 3 sub-directories:
  - ```tuplefile``` ... where processed output (tuple ROOT) file would exist
  - ```daqfile``` ... where input daq binary file should exist
  - ```garbagefile``` ... where failed daq file is logged (just identical filename is "touched").

Running the script:
```
cd process_area
python start_tuplemaking.py >> log.txt &
```
will launch an automated tuple making process.
The script will detect and abort if you launch start_tuplemaking.py while it is already running in the background.

This script identifies unprocessed files under ```daqfile``` area (by checking corresponding file name does not exist under ```tuplefile``` and ```garbagefile```) and process them.
*Important*: daq binary files under ```daqfile``` must have ```json``` file accompanied (no need to be filled) to be processed by the script.

Additional functionality of the script includes:
  - automatically pulls daq files from a list of run numbers in ```process_area/run.txt``` (you can make one)
  - automatically rsync tuplefile directory to ubdaq-prod-ws01.fnal.gov:/data/$USER/tuplefile area
  
To take a benefit of the first point, you can just do, anytime during the script is running in the background,
```
echo 123456 >> run.txt
```
to add a certain run to a list. By requiring the presence of ```json``` file, it avoids processing unclosed file.

The second point is simply for you to be able to rsync from your laptop w/o setting up tunnel.


 

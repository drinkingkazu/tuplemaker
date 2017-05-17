import os,commands,sys
import time

if not 'TUPLEMAKER_DIR' in os.environ:
    sys.stderr.write('TUPLEMAKER_DIR not set in shell env. ... (cannot run)\n')
    sys.stderr.flush();
    sys.exit(1)

USER=os.environ['USER']
# top area
PROCESS_AREA=os.path.join(os.environ['TUPLEMAKER_DIR'],'process_area')
# local file storage
GARBAGE_DIR=os.path.join(PROCESS_AREA,'garbagefile')
DAQFILE_DIR=os.path.join(PROCESS_AREA,'daqfile')
LITEFILE_DIR=os.path.join(PROCESS_AREA,'tuplefile')
TEMPFILE_PATH='/tmp/tupleout_%s.root' % str(os.getpid())
RUNLIST_FILE='%s/runs.txt' % PROCESS_AREA

def prep_dirs():
    os.system('mkdir -p %s' % GARBAGE_DIR)
    os.system('mkdir -p %s' % DAQFILE_DIR)
    os.system('mkdir -p %s' % LITEFILE_DIR)

def get_flist():

    garbage_flist=[x.rstrip('.ubdaq') for x in os.listdir(GARBAGE_DIR) if x.endswith('.ubdaq')]
    lite_flist=[x.rstrip('.root') for x in os.listdir(LITEFILE_DIR) if x.endswith('.root')]
    done_flist = garbage_flist + lite_flist
    json_flist=[x.rstrip('.json') for x in os.listdir(DAQFILE_DIR) if x.endswith('.json') and x.rstrip('.json') not in done_flist]
    daq_flist=[x.rstrip('.ubdaq') for x in os.listdir(DAQFILE_DIR) if x.endswith('.ubdaq') and x.rstrip('.ubdaq') not in done_flist and x.rstrip('.ubdaq') in json_flist]
    return daq_flist

def sync_input():
    if not os.path.isfile(RUNLIST_FILE): return
    runlist = [int(x) for x in open(RUNLIST_FILE,'r').read().split() if x.isdigit()]
    first=True
    for r in runlist:
        if first:
            print
            print 'Synching input...'
            first=False
        cmd='rsync -v -e ssh -L --progress --update %s@ubdaq-prod-ws01.fnal.gov:/data/uboonedaq/rawdata/*-%07d-*.ubdaq* %s' % (USER,DAQFILE_DIR)
        os.system(cmd)

def start():

    min_dt=60
    next_file_dt=-1
    while 1:
        daq_flist = get_flist()
        sys.stdout.write('Identified %-2d daq files to be processed (time to next: %2d [s])\r' % (len(daq_flist),next_file_dt))
        sys.stdout.flush()
        first_file=True
        next_file_dt=-1
        for f in daq_flist:
            in_path = '%s/%s.ubdaq' % (DAQFILE_DIR,f)
            dt = time.time() - os.path.getctime(in_path)
            if dt < min_dt:
                if next_file_dt<0: next_file_dt=min_dt - dt
                elif next_file_dt>dt: next_file_dt=min_dt - dt
                continue
            if first_file: 
                print
                first_file=False
            out_path = '%s/%s.root' % (LITEFILE_DIR,f)
            garbage_path = '%s/%s.ubdaq' % (GARBAGE_DIR,f)
            print 'Processing',f
            cmd = 'tuplemaker %s %s' % (in_path,TEMPFILE_PATH)
            try:
                if os.system(cmd) == 0:
                    os.system('mv %s %s' % (TEMPFILE_PATH,out_path))
                else: raise Exception
            except Exception:
                cmd='rm -f %s; rm -f %s; touch %s' % (TEMPFILE_PATH,out_path,garbage_path)
                os.system(cmd)

        if not first_file:
            os.system('ssh %s@ubdaq-prod-ws01.fnal.gov "mkdir -p /data/%s/optical_tuple"' % (USER,USER))
            os.system('rsync -v -e ssh -r -L --delete --progress --update %s/ %s@ubdaq-prod-ws01.fnal.gov:/data/%s/optical_tuple' % (LITEFILE_DIR,USER,USER))
        sync_input()
        time.sleep(1)

if __name__=='__main__':
    if not commands.getoutput('which tuplemaker').startswith('/'): 
        sys.stderr.write('Could not find tuplemaker binary...\n')
        sys.stderr.write('\n')
        sys.exit(1)
    if len(commands.getoutput('ps aux | grep %s' % sys.argv[0]).split('\n')) >=4:
        print commands.getoutput('ps aux | grep %s' % sys.argv[0])
        sys.stderr.write('%s already running...\n' % sys.argv[0])
        sys.stderr.flush()
        sys.exit(1)
    prep_dirs()
    start()
    sys.exit(0)

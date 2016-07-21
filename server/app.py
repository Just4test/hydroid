import leancloud
import os, sys
import logging
from util import *

################## GET PARAMETER ##########################
app_id = os.environ.get('APP_ID')
if app_id:
    print('Get App ID from env.')
master_key = os.environ.get('MASTER_KEY')
if app_id:
    print('Get Master Key from env.')

arg = None
argi = 0
def next_arg():
    global argi, arg
    argi = argi + 1
    if argi >= len(sys.argv):
        arg = None
        return None
    arg = sys.argv[argi]
    return arg
    
while next_arg() is not None:
    if '--appid' == arg:
        app_id = next_arg()
        print('Get App ID from args.')
    elif '--masterkey' == arg:
        master_key = next_arg()
        print('Get Master Key from args.')
    else:
        print('Unknown argument {}'.format(arg))
        exit(1)
        
if not app_id:
    print('Haven`t give App ID.')
    exit(1)
if not master_key:
    print('Haven`t give Master Key.')
    exit(1)
    
################## INIT LEANCLOUD ########################
leancloud.init(app_id, master_key = master_key)
init_leancloud()

app = Flask(__name__)
app.debug = True

@app.route('/')
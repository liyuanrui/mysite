

import os,sys
import zipfile
mf = os.path.dirname(__file__)+'/manage.py'

os.system(sys.executable+" "+mf+' runserver')

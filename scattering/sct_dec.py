import re
from . import sct
sct_symbtable = re.split(r'\s+', sct.elnams.tobytes().decode().strip())
sct_cifsymbtable = re.split(r'\s+', sct.cifelnams.tobytes().decode().strip())


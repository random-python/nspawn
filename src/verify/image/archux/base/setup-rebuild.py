#!/usr/bin/env python

import os

this_dir = os.path.dirname(os.path.abspath(__file__))

os.system(f"{this_dir}/setup.py --action=desure --trace-error=yes")

os.system(f"{this_dir}/build.py --trace-error=yes")

os.system(f"{this_dir}/setup.py --action=ensure --trace-error=yes")

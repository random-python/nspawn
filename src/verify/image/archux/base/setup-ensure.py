#!/usr/bin/env python

import os

this_dir = os.path.dirname(os.path.abspath(__file__))

os.system(f"{this_dir}/setup.py --action ensure")

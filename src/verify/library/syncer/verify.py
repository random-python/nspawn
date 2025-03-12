#!/usr/bin/env python3

import os
import time

from library.syncer.sync import *

resource_one = "./store/readme.md"

accesstime, modifiedtime = time.time(), time.time() - 86400 * 3

os.utime(resource_one, (accesstime, modifiedtime))

invoke_module()

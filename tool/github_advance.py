#!/usr/bin/env python

#
# dependency:
# * python-sh
#

import datetime
import logging
from sh import git
from sh import contrib

logging.basicConfig(level=logging.INFO)


instant = datetime.datetime.now().isoformat()
message = f"develop {instant}"

git("add", "--all")
git("commit", "--quiet", f"--message='{message}'")
git(f"push")

#
#
#

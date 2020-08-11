#!/usr/bin/env python

"""
Squash github commits starting from a point
"""

from devrepo import shell

point = "d15a7bb70647828e42ad5da79379b8239e0ffadd"
message = "develop"

shell(f"git reset --soft {point}")
shell(f"git add --all")
shell(f"git commit --message='{message}'")
shell(f"git push --force --follow-tags")

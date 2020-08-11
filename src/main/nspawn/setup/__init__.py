"""
Setup DSL
"""

# invoke engine
import nspawn.app.engine.invoke
nspawn.app.engine.invoke.invoke_main('setup.py')

# publish setup dsl
from nspawn import tool as TOOL
from nspawn.setuper.syntax import *

__all__ = [
    'TOOL',
    'IMAGE',
    'MACHINE',
    'WITH',
    'EXEC',
    'COPY',
    'CAST',
    'RUN',
    'SH',
]

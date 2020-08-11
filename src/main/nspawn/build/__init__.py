"""
Build DSL
"""

# invoke engine
import nspawn.app.engine.invoke
nspawn.app.engine.invoke.invoke_main('build.py')

# publish build dsl
from nspawn import tool as TOOL
from nspawn.builder.syntax import *

__all__ = [
    'TOOL',
    'IMAGE',
    'PULL',
    'EXEC',
    'WITH',
    'FETCH',
    'COPY',
    'CAST',
    'RUN',
    'SH',
    'PUSH',
]

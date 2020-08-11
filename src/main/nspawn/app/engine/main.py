"""
Main program code
"""

import abc
import sys
import logging
import traceback
from argparse import ArgumentParser

from nspawn import CONFIG
from nspawn.app.engine import parser
from nspawn.app.engine import invoke
from nspawn.base.engine import Engine
from nspawn.support.parser import ParseResult

logger = logging.getLogger(__name__)


class Main(abc.ABC):

    @abc.abstractclassmethod
    def engine(self) -> Engine:
        pass

    @abc.abstractclassmethod
    def parser(self) -> ArgumentParser:
        pass

    def verify(self):
        from nspawn.wrapper.base import missing_required_list
        missing_list = missing_required_list()
        if len(missing_list) > 0:
            raise RuntimeError(f"Missing required commands: {missing_list}")

    def perform(self) -> None:
        try:
            self.verify()
            invoke.InvokeState.invoke_set()
            parser = self.parser()
            space, extra = parser.parse_known_args()
            parse_result = ParseResult(space, extra)
            engine = self.engine()
            engine.init_args(parse_result)
            engine.parse_script()
            engine.perform_intent()
        except Exception as error:
            trace_error = CONFIG['main'].getboolean('trace_error')
            if trace_error:
                traceback.print_exc()
            sys.exit(f"Engine failure: {error}")


class BuildMain(Main):

    def engine(self):
        import nspawn.builder.engine
        return nspawn.builder.engine.ENGINE

    def parser(self):
        return parser.build_parser()


class SetupMain(Main):

    def engine(self):
        import nspawn.setuper.engine
        return nspawn.setuper.engine.ENGINE

    def parser(self):
        return parser.setup_parser()

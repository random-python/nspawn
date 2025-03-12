"""
External process invocation
"""

import sys
import shlex
import typing
import asyncio
import subprocess
from enum import Enum
from dataclasses import dataclass, field


async def stream_read(
        stream: asyncio.StreamReader,
        react:typing.Callable[[bytes], None],
        encoding=None,
    ) -> None:
    while True:
        line = await stream.readline()
        if encoding:
            line = line.decode(encoding)
        if line:
            react(line)
        else:
            break


async def stream_write(
        input_list: typing.Iterable[bytes],
        stream: asyncio.StreamWriter,
        encoding=None,
    ) -> None:
    for line in input_list:
        if encoding:
            line = line.encode(encoding)
        stream.write(line)
        await stream.drain()
    stream.close()


def make_task_list(coro_list:list) -> list[asyncio.Task]:
    ""
    task_list = []
    for this_coro in coro_list:
        this_task = asyncio.create_task(this_coro)
        task_list.append(this_task)
    return task_list


async def stream_shell(script, stdin, react_stdout, react_stderr, encoding):
    process = await asyncio.create_subprocess_shell(
        script,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    input_list = [] if stdin is None else stdin.splitlines()
    this_task_list = make_task_list([
        stream_write(input_list, process.stdin, encoding),
        stream_read(process.stdout, react_stdout, encoding),
        stream_read(process.stderr, react_stderr, encoding),
    ])
    await asyncio.wait(this_task_list)
    return await process.wait()


async def stream_program(command, stdin, react_stdout, react_stderr, encoding):
    process = await asyncio.create_subprocess_exec(
        *command,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    input_list = [] if stdin is None else stdin.splitlines()
    this_task_list = make_task_list([
        stream_write(input_list, process.stdin, encoding),
        stream_read(process.stdout, react_stdout, encoding),
        stream_read(process.stderr, react_stderr, encoding),
    ])
    await asyncio.wait(this_task_list)
    return await process.wait()


default_react_stdout = lambda line: sys.stdout.write(f"[stdout] {line}")
default_react_stderr = lambda line: sys.stderr.write(f"[stderr] {line}")


def exectute_program(
        command,
        stdin=None,
        react_stdout=default_react_stdout,
        react_stderr=default_react_stderr,
        encoding='utf-8',
     ):
    loop = asyncio.get_event_loop()
    rc = loop.run_until_complete(
        stream_program(
            command,
            stdin,
            react_stdout,
            react_stderr,
            encoding,
    ))
    return rc


def exectute_shell(
        script,
        stdin=None,
        react_stdout=default_react_stdout,
        react_stderr=default_react_stderr,
        encoding='utf-8',
     ):
    loop = asyncio.get_event_loop()
    rc = loop.run_until_complete(
        stream_shell(
            script,
            stdin,
            react_stdout,
            react_stderr,
            encoding,
    ))
    return rc


def make_solo_line(text:str) -> str:
    return repr(text)


class Command(list):

    def __str__(self):
        return " ".join([ shlex.quote(term) for term in self ])


class RenderType(Enum):
    brief = 1
    short = 2
    total = 3


@dataclass(frozen=True)
class ExecuteResult:
    command:[] = field(default_factory=list)
    rc:int = -1
    stdout:str = None
    stderr:str = None
    error:Exception = None

    def __str__(self) -> str:
        return self.render_status(RenderType.total)

    def assert_return(self, rc:int=0, error:Exception=None, message:str="Command failure") -> 'ExecuteResult':
        assert self.rc == rc and error == error, f"{message}: {str(self)}"
        return self

    def render_status(self, render_type:RenderType) -> str:
        rc = self.rc
        stdout = repr(self.stdout) if self.stdout else None
        stderr = repr(self.stderr) if self.stderr else None
        error = repr(self.error)
        if render_type == RenderType.brief:
            return f"rc={rc} stdout={stdout} stderr={stderr}"
        if render_type == RenderType.short:
            return f"rc={rc} stdout={stdout} stderr={stderr} error={error}"
        if render_type == RenderType.total:
            return f"{self.command} rc={rc} stdout={stdout} stderr={stderr} error={error}"
        raise RuntimeError(f"Invalid render type: {render_type}")


def execute_process_flow(
        command,
        stdin=None,
        react_stdout=default_react_stdout,
        react_stderr=default_react_stderr,
    ) -> ExecuteResult:
    rc = exectute_program(command, stdin=stdin, react_stdout=react_stdout, react_stderr=react_stderr)
    return ExecuteResult(command=command, rc=rc)


def execute_process_unit(command, stdin=None) -> ExecuteResult:
    process = subprocess.Popen(
        command, shell=False, encoding='utf8',
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    try:
        stdout, stderr = process.communicate(stdin)
        rc = process.returncode
        return ExecuteResult(command=command, rc=rc, stdout=stdout, stderr=stderr)
    except Exception as error:
        return ExecuteResult(command=command, error=error)

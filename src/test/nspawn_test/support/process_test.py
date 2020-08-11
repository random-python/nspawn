import pytest

from nspawn.support.process import *


def test_make_solo_line():
    print()
    text = """
    a
    b
    c
    """
    line = make_solo_line(text)
    print(line)


def test_run_result():
    print()
    command = ['/usr/bin/env', 'sh', '-c', 'echo hello-kitty']
    result = ExecuteResult(command=command)
    print(result)
    result = ExecuteResult(command=command, stdout='', stderr='')
    print(result)
    result = ExecuteResult(rc=1, command=command, stdout='a b')
    print(result)
    result = ExecuteResult(rc=2, command=command, stderr='1 2')
    print(result)
    result = ExecuteResult(rc=3, command=command,
        stdout="""
        a
        b
        """,
        stderr="""
        1
        2
        """,
        error=RuntimeError('hello-kitty')
    )
    print(result)
    with pytest.raises(Exception) as trap_info:
        result.assert_return()
    print(trap_info)


def test_execute_shell():
    print()
    script = "read var; echo var=$var; for step in {1..3}; do echo step=$step; sleep 0.1; done"
    exectute_shell(script, stdin="hello")


def test_execute_program():
    print()
    command = ['ls', '-las']
    exectute_program(command)


def test_command():
    print()
    command = Command(['ls', '-las', 'hello kitty "with kittens"', "a a 'b b'"])
    print(command)

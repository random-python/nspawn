import pytest

from functools import partial
from nspawn.base.token import *

parse_intent = partial(parse_intent, mapper=mapper_intent_effect)


def test_image_intent():
    print()
    image = ImageIntent(url="http://test")
    print(image)
    with pytest.raises(Exception) as trap_info:
        image.args = (1, 2)
    assert str(trap_info.value) == 'class is immutable'


def test_image_effect():
    print()
    image = ImageEffect(url="http://test")
    print(image)
    with pytest.raises(Exception) as trap_info:
        image.url = "invalid"
    assert str(trap_info.value) == "cannot assign to field 'url'"


def test_machine_effect():
    print()
    machine = MachineEffect('machine')
    print(machine)
    assert machine.name == 'machine'
    assert machine.template == 'machine-default.service'


def test_effect_list():
    print()
    effect_list = [
        ExecEffect(command=['/usr/lib/systemd/systemd']),
        ProfileEffect(Boot='yes', Bind='/root:/root'),
        RunEffect(command=['/bin/ls', '-las']),
        ShellEffect(script='ls -las'),
        CopyEffect(path='/etc/'),
        CopyEffect(source='/etc/1', target='/etc/2'),
        TemplateEffect(path='/etc/', a=1, b="test"),
        TemplateEffect(source='/etc/1', target='/etc/2', a=1, b="test"),
        FetchEffect(url="http://host/path", path="/root/test"),
        FetchEffect(url="http://host/path", source="/root/test1", target="/root/test2"),
        MachineEffect('machine'),
        MachineEffect(name='machine'),
        MachineEffect('machine', 'machine.service'),
        MachineEffect(name='machine', template='machine.service'),
    ]
    for effect in effect_list:
        print(effect)


def test_parse_intent():
    print()
    parse_intent(ImageIntent(url="http://test"))
    parse_intent(PullIntent(url="http://test"))
    parse_intent(FetchIntent(url="http://test"))
    parse_intent(ShellIntent(script="ls -las"))
    parse_intent(RunIntent(script="/bin/ls -las"))
    parse_intent(RunIntent(command=['/bin/ls', '-las']))
    parse_intent(CopyIntent(path='/etc/test'))
    parse_intent(CopyIntent(source='/etc/test1', target='/etc/test2'))
    parse_intent(TemplateIntent(path='/etc/test'))
    parse_intent(TemplateIntent(source='/etc/test1', target='/etc/test2'))
    parse_intent(PushIntent())


def xxx_test_parse_build():
    print()
    intent_list = [
        ImageIntent(url="http://test"),
        PullIntent(url="http://test"),
        ShellIntent(script="ls -las"),
        CopyIntent(path='/etc/test'),
        CopyIntent(source='/etc/test1', target='/etc/test2'),
        PushIntent(),
    ]

#     result = parse_build(intent_list)
#     print()
#     print(result)

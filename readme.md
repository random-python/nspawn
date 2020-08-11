
## nspawn

[![Travis Status][travis_icon]][travis_link]
[![Appvey Status][appvey_icon]][appvey_link]
[![Package Version][pypi_icon]][pypi_link]
[![Python Versions][python_icon]][python_link]

Containers with [`systemd-nspawn`](https://www.freedesktop.org/software/systemd/man/systemd-nspawn.html)

Features:
* differential image [overlays](https://en.wikipedia.org/wiki/OverlayFS)
* supports multiple inheritance for images
* provides [dsl](https://en.wikipedia.org/wiki/Domain-specific_language)
  for image `build` and machine `setup`
* machine is
  [completely represented](https://github.com/random-python/nspawn/tree/master/src/main/nspawn/template)
  by generated
  [machine.service unit file](https://www.freedesktop.org/software/systemd/man/systemd.unit.html)

### Install

To install python package:

```
sudo pip install nspawn
```

### Build Script

To build an image, provide and invoke executable `build.py` script, for example:
* alpine: https://github.com/random-python/nspawn/blob/master/demo/alpine/base/build.py
* archux: https://github.com/random-python/nspawn/blob/master/demo/archux/base/build.py
* ubuntu: https://github.com/random-python/nspawn/blob/master/demo/ubuntu/base/build.py

For available build options run `./build.py --help`

### Setup Script

To setup a machine, provide and invoke executable `setup.py` script, for example:
* alpine: https://github.com/random-python/nspawn/blob/master/demo/alpine/base/setup.py
* archux: https://github.com/random-python/nspawn/blob/master/demo/archux/base/setup.py
* ubuntu: https://github.com/random-python/nspawn/blob/master/demo/ubuntu/base/setup.py

For available setup options run `./setup.py --help`

### Machine Service

To review provisioned, generated and running machine service, run:
```
machinectl
systemctl status <machine>
cat /etc/systemd/system/<machine>.service
```
for example, demo generated services:
* alpine: https://github.com/random-python/nspawn/blob/master/demo/alpine-base.service
* archux: https://github.com/random-python/nspawn/blob/master/demo/archux-base.service
* ubuntu: https://github.com/random-python/nspawn/blob/master/demo/ubuntu-base.service

### Machine Resources

Location of machine files and folders:
```
/etc/systemd/system/<machine>.service
/var/lib/machines/<machine>
/var/lib/nspawn/runtime/<machine>
```

### Machine Management

To interact with live machine:
* for machines registered with `machinectl`
* for machines with `systemd` `init`, such as `archlinux`
```
# start interactive shell:
sudo machinectl shell <machine> 
```
```
# invoke command with args:
sudo machinectl shell <machine> /bin/command arg1 arg2 ... 
```
* for machines not registered with `machinectl`
* for machines without `systemd` `init`, such as `alpine linux`
```
# start interactive shell:
./setup.py --action=nsenter 
```
* alternatively, use package-provided `nspawn-enter` command:
```
# start interactive shell:
nspawn-enter <machine> 
```
```
# invoke command with args:
nspawn-enter <machine> "command arg1 arg2 ..." 
```

### Configuration

Available configuration options are described in
[config.ini](https://github.com/random-python/nspawn/blob/master/src/main/nspawn/config.ini) 
file.

Use `config/path_list` option to control configuration override file list.

### Image Server

Package comes with provisioning command `nspawn-hatch`
which can build and setup local http/https image server.
```
# review available services:
nspawn-hatch list
```
```
# provision image server service:
nspawn-hatch update image-server
```
```
# verify image server machine status:
machinectl
```

Image server settings:
* https://github.com/random-python/nspawn/tree/master/src/main/nspawn/app/hatcher/service/image-server

Image syncer settings (replicate to Amazon AWS S3):
* https://github.com/random-python/nspawn/tree/master/src/main/nspawn/app/hatcher/service/image-syncer

### Build DSL

Build DSL is used in `build.py`, is activated by `from nspawn.build import *` and provides keywords:
```
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
```

### Setup DSL

Setup DSL is used in `setup.py`, is activated by `from nspawn.setup import *` and provides keywords:
```
    'TOOL',
    'IMAGE',
    'MACHINE',
    'WITH',
    'EXEC',
    'COPY',
    'CAST',
    'RUN',
    'SH',
```

### DSL Syntax

#### `TOOL`

Expose build/setup utility functions:
* https://github.com/random-python/nspawn/tree/master/src/main/nspawn/tool
```
TOOL.<function>(...)
```

#### `IMAGE()`

Declare image identity:
```
IMAGE("http://host/path/package.tar.gz")
IMAGE(url="http://host/path/package.tar.gz")
```

#### `PULL()`

Provision dependency image:
```
PULL("http://host/path/package.tar.gz")
PULL(url="http://host/path/package.tar.gz")
```

#### `EXEC()`

Declare image entry point executable i.e. `COMMAND [ARGS...]`:
* https://www.freedesktop.org/software/systemd/man/systemd-nspawn.html
```
EXEC(['/usr/bin/env', 'sh', '-c', 'echo "hello-kitty"'])
EXEC(command=['/usr/bin/env', 'sh', '-c', 'echo "hello-kitty"'])
```

#### `WITH()`

Customize machine features using nspawn container settings:
* https://www.freedesktop.org/software/systemd/man/systemd.nspawn.html
```
WITH(
    SettingName1='setting 1 value a',
    SettingName2='setting 2 value b',
    ...,
)
```

#### `COPY()`

Copy local resources:
* when used in `build.py`: target is in the image
* when used in `setup.py`: target is on the host
```
COPY("/etc")
COPY(path="/etc")
COPY(source="/root/input.md", target="/root/output.md")
```

#### `CAST()`

Template local resources:
* when used in `build.py`: target is in the image
* when used in `setup.py`: target is on the host
```
CAST("/root/readme.md", variable="template varialbe", ...)
CAST(path="/root/readme.md", variable="template varialbe", ...)
CAST(source="/root/input.md", target="/root/output.md", variable="template varialbe", ...)
```

Template uses [python/jinja](https://jinja.palletsprojects.com/en/2.10.x/)
format, i.e:
```
this template variable will be substituted: {{variable}}
```

#### `FETCH()`

Download and extract remote resource:
```
FETCH( # use when source and target are the same
   url="http://server/package.tar.gz", # url for remote resource
   path="/common-path", # path inside the package source and image target
)
FETCH( # use when source and target are different
   url="http://server/package.tar.gz", # url for remote resource
   source="/package-path", # path inside the package extract
   target="/opt/resource", # path inside the build image target
)
```

#### `RUN()`

Invoke command, with target depending on the context:
* when used in `build.py`: invoke inside the image
* when used in `setup.py`: invoke on the host
```
RUN(['/usr/bin/env', 'ls', '-las'])
RUN(command=['/usr/bin/env', 'ls', '-las'])
```

#### `SH()`

Invoke shell script, with target depending on the context:
* when used in `build.py`: invoke inside the image
* when used in `setup.py`: invoke on the host
```
SH("ls -las")
SH(script="ls -las")
```
Note:
* `SH(script)` is equivalent to `RUN(command=['/usr/bin/env', 'sh', '-c', script])`

#### `PUSH()`

Publish image result to the declared url:
```
PUSH()
```

#### `MACHINE()`

Declare machine service:
```
MACHINE('machine-name')
MACHINE(name='machine-name')
MACHINE(name='machine-name', template='/path/to/service/template/machine.service')
```

Provide inline service unit changes:
```
MACHINE(
    name='machine-name',
    # extra entries for [Unit] section
    unit_conf=[
        "Description=hello-world",  # override description
    ],
    # extra entries for [Service] section
    service_conf=[
        "CPUQuota=10%",  # throttle processor usage
    ],
    # extra entries for [Install] section
    install_conf=[
        "WantedBy=machines.target",  # inject unit dependency
    ],
)
```

Design custom service templates based on package-provided defaults, for example:
* https://github.com/random-python/nspawn/tree/master/src/main/nspawn/template




[travis_icon]: https://travis-ci.org/random-python/nspawn.svg?branch=master
[travis_link]: https://travis-ci.org/random-python/nspawn/builds

[appvey_icon]: https://ci.appveyor.com/api/projects/status/fbjgg6ana9kkww6p?svg=true
[appvey_link]: https://ci.appveyor.com/project/Andrei-Pozolotin/nspawn/history 

[pypi_icon]: https://badge.fury.io/py/nspawn.svg
[pypi_link]: https://pypi.python.org/pypi/nspawn

[python_icon]: https://img.shields.io/pypi/pyversions/nspawn.svg
[python_link]: https://pypi.python.org/pypi/nspawn

[tokei_icon]: https://tokei.rs/b1/github/random-python/nspawn
[tokei_link]: https://github.com/random-python/nspawn/tree/master/src

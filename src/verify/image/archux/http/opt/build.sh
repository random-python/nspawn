#!/bin/bash

set -e -x

base_dir="/usr/share/webapps/roundcubemail"
plug_dir="$base_dir/plugins"

setup() {
    cd "$base_dir"
    rm -f composer.lock
    composer install --no-dev
}

clone() {
    local "$@"
    cd "$plug_dir"
    rm -r -f "$dir"
    git clone "$url" "$dir"
}

# php installer (use arch)
#curl -sS https://getcomposer.org/installer | php

### external

clone dir=carddav  url=https://github.com/random-cuber/carddav.git

cd "$base_dir/plugins/carddav"
composer install

clone dir=contextmenu            url=https://github.com/random-cuber/contextmenu.git
clone dir=identity_smtp          url=https://github.com/random-cuber/identity_smtp.git
# clone dir=keyboard_shortcuts     url=https://github.com/random-cuber/keyboard_shortcuts.git
# clone dir=keyboard_shortcuts_ng  url=https://github.com/random-cuber/keyboard_shortcuts_ng.git
clone dir=automatic_addressbook  url=https://github.com/random-cuber/automatic_addressbook.git

### internal

clone dir=hotkeys                url=https://github.com/random-cuber/hotkeys.git
clone dir=responses                url=https://github.com/random-cuber/responses.git
clone dir=styled_popups          url=https://github.com/random-cuber/styled_popups.git
# clone dir=font_awesome           url=https://github.com/random-cuber/font_awesome.git
clone dir=contextmenu_folder     url=https://github.com/random-cuber/contextmenu_folder.git


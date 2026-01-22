# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

cd ~/Dropbox/projects/lynx/js
npm run build
cd ~/Dropbox/projects/lynx
uv pip install -e . --force-reinstall --no-deps
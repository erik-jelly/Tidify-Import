# Copyright (C) 2026 Erik Jelezarov (@erik-jelly)
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of Tidify-Import, licensed under the GNU GPL v3 or later.
# See the LICENSE file in the project root for details.

import json

def importCredentials():
    with open("credentials.json", 'r') as f:
            credentials = json.load(f)

    return credentials

def exportCredentials(credentials):
    with open("credentials.json", 'w') as f:
        json.dump(credentials, f, indent=4)
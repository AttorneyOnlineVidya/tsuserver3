# tsuserver3, an Attorney Online server
#
# Copyright (C) 2016 argoneus <argoneuscze@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import ipaddress
import json
import yaml

from server.exceptions import ServerError


class BanManager:
    def __init__(self):
        self.bans = {}
        self.load_banlist()
        self.hdid_exempt = {}
        self.load_hdidexceptions()

    def load_banlist(self):
        try:
            with open('storage/banlist.json', 'r') as banlist_file:
                self.bans = json.load(banlist_file)
        except FileNotFoundError:
            with open('storage/banlist.json', 'w') as poll_list_file:
                json.dump({}, poll_list_file)

    def write_banlist(self):
        with open('storage/banlist.json', 'w') as banlist_file:
            json.dump(self.bans, banlist_file)

    def add_ban(self, ip):
        try:
            x = len(ip)
        except AttributeError:
            raise ServerError('Argument must be an 12-digit number.')
        if x == 12:
            self.bans[ip] = True
            self.write_banlist()

    def remove_ban(self, client, ip):
        try:
            try:
                int(ip)
            except ValueError:
                ipaddress.ip_address(ip)
                ip = client.server.get_ipid(ip)
        except ValueError:
            if not len(ip) == 12:
                raise ServerError('Argument must be an IP address or 10-digit number.')
        del self.bans[ip]
        self.write_banlist()

    def is_banned(self, ipid):
        try:
            return self.bans[ipid]
        except KeyError:
            return False

    def load_hdidexceptions(self):
        with open('config/hdid_exceptions.yaml', 'r', encoding='utf-8') as hdid:
            self.hdid_exempt = yaml.load(hdid)
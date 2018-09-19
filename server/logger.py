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

import logging
import logging.handlers
import os
from server import area_manager

import time


def setup_logger(debug, log_size, log_backups, areas):
    logging.Formatter.converter = time.gmtime
    debug_formatter = logging.Formatter('[%(asctime)s UTC]%(message)s')
    srv_formatter = logging.Formatter('[%(asctime)s UTC]%(message)s')

    debug_log = logging.getLogger('debug')
    debug_log.setLevel(logging.DEBUG)

    # 0 maxBytes = no rotation
    # backupCount = number of old logs to save
    debug_handler = logging.handlers.RotatingFileHandler('logs/debug.log', maxBytes=log_size, backupCount=log_backups,
                                                         encoding='utf-8')
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(debug_formatter)
    debug_log.addHandler(debug_handler)

    if not debug:
        debug_log.disabled = True

    server_log = logging.getLogger('server')
    server_log.setLevel(logging.INFO)

    server_handler = logging.handlers.RotatingFileHandler('logs/server.log', maxBytes=log_size, backupCount=log_backups,
                                                          encoding='utf-8')
    server_handler.setLevel(logging.INFO)
    server_handler.setFormatter(srv_formatter)
    server_log.addHandler(server_handler)

    mod_log = logging.getLogger('mod')
    mod_log.setLevel(logging.INFO)

    mod_handler = logging.handlers.RotatingFileHandler('logs/mod.log', maxBytes=log_size, backupCount=log_backups,
                                                          encoding='utf-8')
    mod_handler.setLevel(logging.INFO)
    mod_handler.setFormatter(srv_formatter)
    mod_log.addHandler(mod_handler)

    user_log = logging.getLogger('user')
    user_log.setLevel(logging.INFO)

    user_handler = logging.handlers.RotatingFileHandler('logs/user.log', maxBytes=log_size, backupCount=log_backups,
                                                       encoding='utf-8')
    user_handler.setLevel(logging.INFO)
    user_handler.setFormatter(srv_formatter)
    user_log.addHandler(user_handler)

    connection_log = logging.getLogger('connect')
    connection_log.setLevel(logging.INFO)
    connection_handler = logging.FileHandler('logs/connection.log', encoding='utf-8')
    connection_handler.setLevel(logging.INFO)
    connection_handler.setFormatter(srv_formatter)
    connection_log.addHandler(connection_handler)

    serverpoll_log = logging.getLogger('serverpoll')
    serverpoll_log.setLevel(logging.INFO)
    serverpoll_handler = logging.FileHandler('logs/serverpoll.log', encoding='utf-8')
    serverpoll_handler.setLevel(logging.INFO)
    serverpoll_handler.setFormatter(srv_formatter)
    serverpoll_log.addHandler(serverpoll_handler)

    area_logs = []
    area_handler = []
    i = 0
    if not os.path.exists('logs/area/'):
        os.makedirs('logs/area/')
    for area in areas:
        area_logs.append(logging.getLogger(area.name))
        area_logs[i].setLevel(logging.INFO)
        area_handler.append(logging.handlers.RotatingFileHandler('logs/area/'+ area.name + '.log', maxBytes=log_size, backupCount=log_backups,
                                                           encoding='utf-8'))
        area_handler[i].setLevel(logging.INFO)
        area_handler[i].setFormatter(srv_formatter)
        area_logs[i].addHandler(area_handler[i])
        i += 1

def log_debug(msg, client=None):
    msg = parse_client_info(client) + msg
    logging.getLogger('debug').debug(msg)


def log_server(msg, client=None):
    msg = parse_client_info(client) + msg
    if client:
        logging.getLogger(client.area.name).info(msg)
    logging.getLogger('user').info(msg)
    logging.getLogger('server').info(msg)


def log_mod(msg, client=None):
    msg = parse_client_info(client) + msg
    logging.getLogger('mod').info(msg)
    logging.getLogger('server').info(msg)

def log_serverpoll(msg, client=None):
    msg = parse_client_info(client) + msg
    logging.getLogger('serverpoll').info(msg)

def log_connect(msg, client=None):
    msg = parse_client_info(client) + msg
    logging.getLogger('connect').info(msg)
    logging.getLogger('server').info(msg)

def parse_client_info(client):
    if client is None:
        return ''
    info = client.get_ipreal()
    if client.is_mod:
        return '[{:<15}][{}][{}][MOD]'.format(info, client.ipid, client.id)
    return '[{:<15}][{}][{}]'.format(info, client.ipid, client.id)

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
# possible keys: ip, OOC, id, cname, ipid, hdid
import hashlib
import random
import string

from server import logger
from server.constants import TargetType
from server.exceptions import ClientError, ServerError, ArgumentError, AreaError

targetreturntype = {
    'ip': TargetType.IP,
    'ipid': TargetType.IPID,
    'hdid': TargetType.HDID,
    'ooc': TargetType.OOC_NAME,
    'char': TargetType.CHAR_NAME,
    'id': TargetType.ID
}


def ooc_cmd_switch(client, arg):
    if len(arg) == 0:
        raise ArgumentError('You must specify a character name.')
    try:
        cid = client.server.get_char_id_by_name(arg)
    except ServerError:
        raise
    try:
        client.change_character(cid, client.is_mod)
    except ClientError:
        raise
    client.send_host_message('Character changed.')


def ooc_cmd_bg(client, arg):
    if len(arg) == 0:
        raise ArgumentError('You must specify a name. Use /bg <background>.')
    if not client.is_mod and client.area.bg_lock == "true":
        raise AreaError("This area's background is locked")
    try:
        client.area.change_background(arg)
    except AreaError:
        raise
    client.area.send_host_message('{} changed the background to {}.'.format(client.get_char_name(), arg))
    logger.log_server('[{}][{}]Changed background to {}'.format(client.area.id, client.get_char_name(), arg), client)


def ooc_cmd_bglock(client, arg):
    if not client.is_mod:
        raise ClientError('You must be authorized to do that.')
    if len(arg) != 0:
        raise ArgumentError('This command has no arguments.')
    if client.area.bg_lock == "true":
        client.area.bg_lock = "false"
    else:
        client.area.bg_lock = "true"
    client.area.send_host_message('A mod has set the background lock to {}.'.format(client.area.bg_lock))
    logger.log_mod(
        '[{}][{}]Changed bglock to {}'.format(client.area.id, client.get_char_name(), client.area.bg_lock), client)


def ooc_cmd_evidence_mod(client, arg):
    if not client.is_mod:
        raise ClientError('You must be authorized to do that.')
    if not arg:
        client.send_host_message('current evidence mod: {}'.format(client.area.evidence_mod))
        return
    if arg in ['FFA', 'Mods', 'CM', 'HiddenCM']:
        if arg == client.area.evidence_mod:
            client.send_host_message('current evidence mod: {}'.format(client.area.evidence_mod))
            return
        if client.area.evidence_mod == 'HiddenCM':
            for i in range(len(client.area.evi_list.evidences)):
                client.area.evi_list.evidences[i].pos = 'all'
        client.area.evidence_mod = arg
        client.send_host_message('current evidence mod: {}'.format(client.area.evidence_mod))
        return
    else:
        raise ArgumentError('Wrong Argument. Use /evidence_mod <MOD>. Possible values: FFA, CM, Mods, HiddenCM')
        return


def ooc_cmd_allow_iniswap(client, arg):
    if not client.is_mod:
        raise ClientError('You must be authorized to do that.')
    client.area.iniswap_allowed = not client.area.iniswap_allowed
    answer = {True: 'allowed', False: 'forbidden'}
    client.send_host_message('iniswap is {}.'.format(answer[client.area.iniswap_allowed]))
    return


def ooc_cmd_roll(client, arg):
    roll_max = 11037
    if len(arg) != 0:
        try:
            val = list(map(int, arg.split(' ')))
            if not 1 <= val[0] <= roll_max:
                raise ArgumentError('Roll value must be between 1 and {}.'.format(roll_max))
        except ValueError:
            raise ArgumentError('Wrong argument. Use /roll [<max>] [<num of rolls>]')
    else:
        val = [6]
    if len(val) == 1:
        val.append(1)
    if len(val) > 2:
        raise ArgumentError('Too many arguments. Use /roll [<max>] [<num of rolls>]')
    if val[1] > 20 or val[1] < 1:
        raise ArgumentError('Num of rolls must be between 1 and 20')
    roll = ''
    for i in range(val[1]):
        roll += str(random.randint(1, val[0])) + ', '
    roll = roll[:-2]
    if val[1] > 1:
        roll = '(' + roll + ')'
    client.area.send_host_message('{} rolled {} out of {}.'.format(client.get_char_name(), roll, val[0]))
    logger.log_server(
        '[{}][{}]Used /roll and got {} out of {}.'.format(client.area.id, client.get_char_name(), roll, val[0]))


def ooc_cmd_rollp(client, arg):
    roll_max = 11037
    if len(arg) != 0:
        try:
            val = list(map(int, arg.split(' ')))
            if not 1 <= val[0] <= roll_max:
                raise ArgumentError('Roll value must be between 1 and {}.'.format(roll_max))
        except ValueError:
            raise ArgumentError('Wrong argument. Use /roll [<max>] [<num of rolls>]')
    else:
        val = [6]
    if len(val) == 1:
        val.append(1)
    if len(val) > 2:
        raise ArgumentError('Too many arguments. Use /roll [<max>] [<num of rolls>]')
    if val[1] > 20 or val[1] < 1:
        raise ArgumentError('Num of rolls must be between 1 and 20')
    roll = ''
    for i in range(val[1]):
        roll += str(random.randint(1, val[0])) + ', '
    roll = roll[:-2]
    if val[1] > 1:
        roll = '(' + roll + ')'
    client.send_host_message('{} rolled {} out of {}.'.format(client.get_char_name(), roll, val[0]))
    client.area.send_host_message('{} rolled.'.format(client.get_char_name(), roll, val[0]))
    SALT = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    logger.log_server(
        '[{}][{}]Used /roll and got {} out of {}.'.format(client.area.id, client.get_char_name(), hashlib.sha1(
            (str(roll) + SALT).encode('utf-8')).hexdigest() + '|' + SALT, val[0]))


def ooc_cmd_currentmusic(client, arg):
    if len(arg) != 0:
        raise ArgumentError('This command has no arguments.')
    if client.area.current_music == '':
        raise ClientError('There is no music currently playing.')
    client.send_host_message('The current music is {} and was played by {}.'.format(client.area.current_music,
                                                                                    client.area.current_music_player))
def ooc_cmd_coinflip(client, arg):
    if len(arg) != 0:
        raise ArgumentError('This command has no arguments.')
    coin = ['heads', 'tails']
    flip = random.choice(coin)
    client.area.send_host_message('{} flipped a coin and got {}.'.format(client.get_char_name(), flip))
    logger.log_server(
        '[{}][{}]Used /coinflip and got {}.'.format(client.area.id, client.get_char_name(), flip))

def ooc_cmd_motd(client, arg):
    if len(arg) != 0:
        raise ArgumentError("This command doesn't take any arguments")
    client.send_motd()

def ooc_cmd_pos(client, arg):
    if len(arg) == 0:
        client.change_position()
        client.send_host_message('Position reset.')
    else:
        try:
            client.change_position(arg)
        except ClientError:
            raise
        client.area.broadcast_evidence_list()
        client.send_host_message('Position changed.')


def ooc_cmd_forcepos(client, arg):
    if not client.is_cm and not client.is_mod:
        raise ClientError('You must be authorized to do that.')
    args = arg.split()
    if len(args) < 1:
        raise ArgumentError(
            'Not enough arguments. Use /forcepos <pos> <target>. Target should be ID, OOC-name or char-name. Use /getarea for getting info like "[ID] char-name".')
    targets = []
    pos = args[0]
    if len(args) > 1:
        targets = client.server.client_manager.get_targets(
            client, TargetType.CHAR_NAME, " ".join(args[1:]), True)
        if len(targets) == 0 and args[1].isdigit():
            targets = client.server.client_manager.get_targets(
                client, TargetType.ID, int(arg[1]), True)
        if len(targets) == 0:
            targets = client.server.client_manager.get_targets(
                client, TargetType.OOC_NAME, " ".join(args[1:]), True)
        if len(targets) == 0:
            raise ArgumentError('No targets found.')
    else:
        for c in client.area.clients:
            targets.append(c)

    for t in targets:
        try:
            t.change_position(pos)
            t.area.broadcast_evidence_list()
            t.send_host_message('Forced into /pos {}.'.format(pos))
        except ClientError:
            raise

    client.area.send_host_message(
        '{} forced {} client(s) into /pos {}.'.format(client.get_char_name(), len(targets), pos))
    logger.log_mod(
        '[{}][{}]Used /forcepos {} for {} client(s).'.format(client.area.id, client.get_char_name(), pos, len(targets)), client)


def ooc_cmd_help(client, arg):
    if len(arg) != 0:
        raise ArgumentError('This command has no arguments.')
    help_url = 'https://github.com/Fronku/Attorney-Online-Vidya'
    help_msg = 'Available commands, source code and issues can be found here: {}'.format(help_url)
    client.send_host_message(help_msg)


def ooc_cmd_kick(client, arg):
    if not client.is_mod:
        raise ClientError('You must be authorized to do that.')
    kicklist = []
    args = arg.split()
    if not len(args) >= 2:
        raise ClientError(
            'You must specify kick type. /kick [\'ip\',\'ipid\', \'hdid\', \'id\',\'char\' or \'ooc\'] [\'value\'] ')
    if args[0].lower() == 'ip':
        kicklist = client.server.client_manager.get_targets(client, TargetType.IP, ''.join(args[1:]).strip(), False)
    elif args[0].lower() == 'ipid':
        kicklist = client.server.client_manager.get_targets(client, TargetType.IPID, ''.join(args[1:]).strip(), False)
    elif args[0].lower() == 'hdid':
        kicklist = client.server.client_manager.get_targets(client, TargetType.HDID, ''.join(args[1:]).strip(), False)
    elif args[0].lower() == 'id':
        kicklist = client.server.client_manager.get_targets(client, TargetType.ID, ''.join(args[1:]).strip(), False)
    elif args[0].lower() == 'char':
        kicklist = client.server.client_manager.get_targets(client, TargetType.CHAR_NAME, ' '.join(args[1:]), True)
    elif args[0].lower() == 'ooc':
        kicklist = client.server.client_manager.get_targets(client, TargetType.OOC_NAME, ' '.join(args[1:]), True)
    print(kicklist)
    if kicklist:
        for c in kicklist:
            logger.log_server('Kicked {}.'.format(c.ipid), client)
            client.send_host_message("{} was kicked.".format(c.get_char_name()))
            c.disconnect()
        logger.log_mod(
                '[{}][{}] kicked {}: {}, with {} clients.'.format(client.area.id, client.get_char_name(), args[0],
                                                                  ''.join(args[1:]).strip(), len(kicklist)), client)

def ooc_cmd_ban(client, arg):
    if not client.is_mod:
        raise ClientError('You must be authorized to do that.')
    banlist = []
    args = arg.split()
    if not len(args) == 2:
        raise ClientError('You must specify ban type. /ban [\'ip\',\'ipid\', \'hdid\' or \'id\'] [\'value\'] ')
    if args[0].lower() == 'ip':
        banlist = client.server.client_manager.get_targets(client, TargetType.IP, ''.join(args[1:]).strip(), False)
    elif args[0].lower() == 'ipid':
        banlist = client.server.client_manager.get_targets(client, TargetType.IPID, ''.join(args[1:]).strip(), False)
    elif args[0].lower() == 'hdid':
        banlist = client.server.client_manager.get_targets(client, TargetType.HDID, ''.join(args[1:]).strip(), False)
    elif args[0].lower() == 'id':
        banlist = client.server.client_manager.get_targets(client, TargetType.ID, ''.join(args[1:]).strip(), False)
    if banlist or args[0].lower() == 'ip':
        try:
            ban = banlist[0].ipid
            actual = ban
        except IndexError:
            ban = ''.join(args[1:]).strip()
            actual = client.server.get_ipid(ban)
        try:
            client.server.ban_manager.add_ban(actual)
        except ServerError:
            raise
        for c in banlist:
            c.disconnect()
        client.send_host_message('{} clients were kicked.'.format(len(banlist)))
        client.send_host_message('{} was banned.'.format(ban))
        logger.log_mod(
                '[{}][{}] banned {}: {}, with {} clients.'.format(client.area.id, client.get_char_name(), args[0],
                                                                  ''.join(args[1:]).strip(), len(banlist)), client)
    else:
        client.send_host_message('No targets found.')


def ooc_cmd_unban(client, arg):
    if not client.is_mod:
        raise ClientError('You must be authorized to do that.')
    try:
        client.server.ban_manager.remove_ban(client, arg)
    except:
        raise ClientError('Must be IP or IPID, or client already unbanned.')
    logger.log_mod(
        '[{}][{}] unbanned {}.'.format(client.area.id, client.get_char_name(), arg),
        client)
    client.send_host_message('Unbanned {}'.format(arg))


def ooc_cmd_play(client, arg):
    if not client.is_mod:
        raise ClientError('You must be authorized to do that.')
    if len(arg) == 0:
        raise ArgumentError('You must specify a song.')
    a = ['..', '/', '\\']
    if any(x in arg for x in a):
        raise ArgumentError('You can only play songs from the music folder.')
    client.area.play_music(arg, client.char_id, -1)
    client.area.add_music_playing(client, arg)
    logger.log_mod('[{}][{}]Changed music to {}.'.format(client.area.id, client.get_char_name(), arg), client)


def ooc_cmd_mute(client, arg):
    if not client.is_mod:
        raise ClientError('You must be authorized to do that.')
    mutelist = []
    args = arg.split()
    if not len(args) >= 2 and not args[0].lower() == 'all':
        raise ClientError(
            'You must specify mute type. /mute [\'ip\',\'ipid\', \'hdid\', \'id\',\'char\', \'ooc\'] [\'value\'] or /unmute all ')
    if args[0].lower() == 'ip':
        mutelist = client.server.client_manager.get_targets(client, TargetType.IP, ''.join(args[1:]).strip(), False)
    elif args[0].lower() == 'ipid':
        mutelist = client.server.client_manager.get_targets(client, TargetType.IPID, ''.join(args[1:]).strip(), False)
    elif args[0].lower() == 'hdid':
        mutelist = client.server.client_manager.get_targets(client, TargetType.HDID, ''.join(args[1:]).strip(), False)
    elif args[0].lower() == 'id':
        mutelist = client.server.client_manager.get_targets(client, TargetType.ID, ''.join(args[1:]).strip(), False)
    elif args[0].lower() == 'char':
        mutelist = client.server.client_manager.get_targets(client, TargetType.CHAR_NAME, ' '.join(args[1:]), True)
    elif args[0].lower() == 'ooc':
        mutelist = client.server.client_manager.get_targets(client, TargetType.OOC_NAME, ' '.join(args[1:]), True)
    elif args[0].lower() == 'all':
        mutelist = client.area.clients
    else:
        raise ClientError('Type error. Values taken are: [ip,ipid, hdid, id, char, ooc, all] ')
    if len(mutelist) > 0:
        try:
            mod_num = 0
            for c in mutelist:
                if c.is_mod:
                    mod_num += 1
                else:
                    c.is_muted = True
                    logger.log_mod(
                    '[{}][{}] muted {} [{}].'.format(client.area.id, client.get_char_name(), c.ipid, c.get_char_name()),
                        client)
            client.send_host_message('Muted {} existing client(s).'.format(len(mutelist) - mod_num))
        except:
            client.send_host_message(
                "No targets found. Use /mute [\'ip\',\'ipid\', \'hdid\', \'id\',\'char\', \'ooc\'] [\'value\'] or /unmute all")
    else:
        client.send_host_message('No targets found.')


def ooc_cmd_unmute(client, arg):
    if not client.is_mod:
        raise ClientError('You must be authorized to do that.')
    mutelist = []
    args = arg.split()
    if not len(args) == 2 and not args[0].lower() == 'all':
        raise ClientError(
            'You must specify mute type. /unmute [\'ip\',\'ipid\', \'hdid\', \'id\',\'char\', \'ooc\'] [\'value\'] or /unmute all ')
    if args[0].lower() == 'ip':
        mutelist = client.server.client_manager.get_targets(client, TargetType.IP, ''.join(args[1:]).strip(), False)
    elif args[0].lower() == 'ipid':
        mutelist = client.server.client_manager.get_targets(client, TargetType.IPID, ''.join(args[1:]).strip(), False)
    elif args[0].lower() == 'hdid':
        mutelist = client.server.client_manager.get_targets(client, TargetType.HDID, ''.join(args[1:]).strip(), False)
    elif args[0].lower() == 'id':
        mutelist = client.server.client_manager.get_targets(client, TargetType.ID, ''.join(args[1:]).strip(), False)
    elif args[0].lower() == 'char':
        mutelist = client.server.client_manager.get_targets(client, TargetType.CHAR_NAME, ' '.join(args[1:]), True)
    elif args[0].lower() == 'ooc':
        mutelist = client.server.client_manager.get_targets(client, TargetType.OOC_NAME, ' '.join(args[1:]), True)
    elif args[0].lower() == 'all':
        mutelist = client.area.clients
    else:
        raise ClientError('Type error. Values taken are: [ip,ipid, hdid, id, char, ooc, all] ')
    if len(mutelist) > 0:
        try:
            mod_num = 0
            for c in mutelist:
                if c.is_mod:
                    mod_num += 1
                else:
                    c.is_muted = False
                    logger.log_mod(
                    '[{}][{}] unmuted {} [{}].'.format(client.area.id, client.get_char_name(), c.ipid, c.get_char_name()),
                        client)
            client.send_host_message('Unmuted {} existing client(s).'.format(len(mutelist) - mod_num))
        except:
            client.send_host_message(
                "No targets found. Use /unmute [\'ip\',\'ipid\', \'hdid\', \'id\',\'char\', \'ooc\'] [\ 'value\'] or /unmute all")
    else:
        client.send_host_message('No targets found.')


def ooc_cmd_login(client, arg):
    if len(arg) == 0:
        raise ArgumentError('You must specify the password.')
    try:
        client.auth_mod(arg)
    except ClientError:
        raise
    if client.area.evidence_mod == 'HiddenCM':
        client.area.broadcast_evidence_list()
    client.send_host_message('Logged in as a moderator.')
    logger.log_mod('[{}][{}] Logged in as moderator.'.format(client.area.id, client.get_char_name() ), client)


def ooc_cmd_g(client, arg):
    if client.muted_global:
        raise ClientError('Global chat toggled off.')
    if len(arg) == 0:
        raise ArgumentError("You can't send an empty message.")
    client.server.broadcast_global(client, arg)
    logger.log_server('[{}][{}][GLOBAL]{}.'.format(client.area.id, client.get_char_name(), arg), client)


def ooc_cmd_gm(client, arg):
    if not client.is_mod:
        raise ClientError('You must be authorized to do that.')
    if client.muted_global:
        raise ClientError('You have the global chat muted.')
    if len(arg) == 0:
        raise ArgumentError("Can't send an empty message.")
    client.server.broadcast_global(client, arg, True)
    logger.log_server('[{}][{}][GLOBAL-MOD]{}.'.format(client.area.id, client.get_char_name(), arg), client)
    logger.log_mod('[{}][{}][GLOBAL-MOD]{}.'.format(client.area.id, client.get_char_name(), arg), client)


def ooc_cmd_lm(client, arg):
    if not client.is_mod:
        raise ClientError('You must be authorized to do that.')
    if len(arg) == 0:
        raise ArgumentError("Can't send an empty message.")
    client.area.send_command('CT', '{}[MOD][{}]'
                             .format(client.server.config['hostname'], client.get_char_name()), arg)
    logger.log_server('[{}][{}][LOCAL-MOD]{}.'.format(client.area.id, client.get_char_name(), arg), client)
    logger.log_mod('[{}][{}][LOCAL-MOD]{}.'.format(client.area.id, client.get_char_name(), arg), client)


def ooc_cmd_announce(client, arg):
    if not client.is_mod:
        raise ClientError('You must be authorized to do that.')
    if len(arg) == 0:
        raise ArgumentError("Can't send an empty message.")
    client.server.send_all_cmd_pred('CT', '{}'.format(client.server.config['hostname']),
                                    '=== Announcement ===\r\n{}\r\n=================='.format(arg))
    logger.log_server('[{}][{}][ANNOUNCEMENT]{}.'.format(client.area.id, client.get_char_name(), arg), client)


def ooc_cmd_toggleglobal(client, arg):
    if len(arg) != 0:
        raise ArgumentError("This command doesn't take any arguments")
    client.muted_global = not client.muted_global
    glob_stat = 'on'
    if client.muted_global:
        glob_stat = 'off'
    client.send_host_message('Global chat turned {}.'.format(glob_stat))


def ooc_cmd_need(client, arg):
    if client.muted_adverts:
        raise ClientError('You have advertisements muted.')
    if len(arg) == 0:
        raise ArgumentError("You must specify what you need.")
    client.server.broadcast_need(client, arg)
    logger.log_server('[{}][{}][NEED]{}.'.format(client.area.id, client.get_char_name(), arg), client)


def ooc_cmd_toggleadverts(client, arg):
    if len(arg) != 0:
        raise ArgumentError("This command doesn't take any arguments")
    client.muted_adverts = not client.muted_adverts
    adv_stat = 'on'
    if client.muted_adverts:
        adv_stat = 'off'
    client.send_host_message('Advertisements turned {}.'.format(adv_stat))


def ooc_cmd_doc(client, arg):
    if len(arg) == 0:
        client.send_host_message('Document: {}'.format(client.area.doc))
        logger.log_server(
            '[{}][{}]Requested document. Link: {}'.format(client.area.id, client.get_char_name(), client.area.doc))
    else:
        client.area.change_doc(arg)
        client.area.send_host_message('{} changed the doc link.'.format(client.get_char_name()))
        logger.log_server('[{}][{}]Changed document to: {}'.format(client.area.id, client.get_char_name(), arg))


def ooc_cmd_cleardoc(client, arg):
    if len(arg) != 0:
        raise ArgumentError('This command has no arguments.')
    client.area.send_host_message('{} cleared the doc link.'.format(client.get_char_name()))
    logger.log_server('[{}][{}]Cleared document. Old link: {}'
                      .format(client.area.id, client.get_char_name(), client.area.doc))
    client.area.change_doc()


def ooc_cmd_status(client, arg):
    if len(arg) == 0:
        client.send_host_message('Current status: {}'.format(client.area.status))
    else:
        try:
            client.area.change_status(arg)
            client.area.send_host_message('{} changed status to {}.'.format(client.get_char_name(), client.area.status))
            logger.log_server(
                '[{}][{}]Changed status to {}'.format(client.area.id, client.get_char_name(), client.area.status))
        except AreaError:
            raise


def ooc_cmd_online(client, _):
    client.send_player_count()


def ooc_cmd_area(client, arg):
    args = arg.split()
    if len(args) == 0:
        client.send_area_list()
    elif len(args) == 1:
        try:
            area = client.server.area_manager.get_area_by_id(int(args[0]))
            client.change_area(area)
        except ValueError:
            raise ArgumentError('Area ID must be a number.')
        except (AreaError, ClientError):
            raise
    else:
        raise ArgumentError('Too many arguments. Use /area <id>.')


def ooc_cmd_pm(client, arg):
    args = arg.split()
    ooc_name = 1
    if len(args) < 2:
        raise ArgumentError('Not enough arguments. Use /pm <target>: <message>.')
    target_clients = []
    for word in args:
        if word.lower().endswith(':'):
            break
        else:
            ooc_name += 1
    if ooc_name == len(args) + 1:
        raise ArgumentError('Invalid syntax. Add \':\' in the end of target.')
    namedrop = ' '.join(args[:ooc_name])
    namedrop = namedrop[:len(namedrop) - 1]
    msg = ' '.join(args[ooc_name:])
    if not msg:
        raise ArgumentError('Not enough arguments. Use /pm <target>: <message>.')
    for char_name in client.server.char_list:
        if namedrop.lower() == char_name.lower():
            try:
                c = client.server.client_manager.get_targets(client, TargetType.CHAR_NAME, char_name, True)
            except Exception as n:
                client.send_host_message('{}'.format(n))
            if c:
                target_clients += c
    if not target_clients:
        try:
            target_clients = client.server.client_manager.get_targets(client, TargetType.OOC_NAME, namedrop, False)
        except Exception as n:
            client.send_host_message('{}'.format(n))
    if not target_clients:
        client.send_host_message('No targets {} found.'.format(namedrop))
    else:
        sent_num = 0
        for c in target_clients:
            if not c.pm_mute:
                c.send_host_message(
                    'PM from {} in {} ({}): {}'.format(client.name, client.area.name, client.get_char_name(), msg))
                sent_num += 1
        if sent_num == 0:
            client.send_host_message('Target(s) not receiving PMs because of mute.')
        else:
            client.send_host_message('PM sent to {}, {} user(s). Message: {}'.format(namedrop, sent_num, msg))
            logger.log_server('[{}][{}] sent a PM to {}: {}.'.format(client.area.id, client.get_char_name(), namedrop, msg)
                              , client)


def ooc_cmd_mutepm(client, arg):
    if len(arg) != 0:
        raise ArgumentError("This command doesn't take any arguments")
    client.pm_mute = not client.pm_mute
    client.send_host_message({True: 'You stopped receiving PMs', False: 'You are now receiving PMs'}[client.pm_mute])


def ooc_cmd_charselect(client, arg):
    if not arg:
        client.char_select()
    else:
        if client.is_mod:
            try:
                target = client.server.client_manager.get_targets(client, TargetType.ID, int(arg), False)
                logger.log_mod('[{}][{}] forced charselect to {} [{}].'.format(client.area.id, client.get_char_name(),
                                                                               target[0].get_ip(),
                                                                               target[0].get_char_name()), client)
                target[0].char_select()
            except Exception as E:
                print(E)
                raise ArgumentError('Wrong arguments. Use /charselect <target\'s id>')


def ooc_cmd_reload(client, arg):
    if len(arg) != 0:
        raise ArgumentError("This command doesn't take any arguments")
    try:
        client.reload_character()
    except ClientError:
        raise
    client.send_host_message('Character reloaded.')


def ooc_cmd_randomchar(client, arg):
    if len(arg) != 0:
        raise ArgumentError('This command has no arguments.')
    try:
        free_id = client.area.get_rand_avail_char_id()
    except AreaError:
        raise
    try:
        client.change_character(free_id)
    except ClientError:
        raise
    client.send_host_message('Randomly switched to {}'.format(client.get_char_name()))


def ooc_cmd_getarea(client, arg):
    client.send_area_info(client.area.id, False)


def ooc_cmd_getareas(client, arg):
    client.send_area_info(-1, False)


def ooc_cmd_mods(client, arg):
    try:
        client.send_host_message("There are {} mods online, and {} mods in the area.".format(len(client.get_mods()),len(client.area.get_mods())))
    except Exception as E:
        print(E)

def ooc_cmd_evi_swap(client, arg):
    args = list(arg.split(' '))
    if len(args) != 2:
        raise ClientError("you must specify 2 numbers")
    try:
        client.area.evi_list.evidence_swap(client, int(args[0]), int(args[1]))
        client.area.broadcast_evidence_list()
    except:
        raise ClientError("you must specify 2 numbers")


def ooc_cmd_cm(client, arg):
    if 'CM' not in client.area.evidence_mod:
        raise ClientError('You can\'t become a CM in this area')
    if client.area.owned == False:
        client.area.owned = True
        client.is_cm = True
        if client.area.evidence_mod == 'HiddenCM':
            client.area.broadcast_evidence_list()
        client.area.send_host_message('{} is CM in this area now.'.format(client.get_char_name()))


def ooc_cmd_logout(client, arg):
    client.is_mod = False
    if client.area.evidence_mod == 'HiddenCM':
        client.area.broadcast_evidence_list()
    client.send_host_message('you\'re not a mod now')
    logger.log_mod('[{}][{}] logged out of modship.'.format(client.area.id, client.get_char_name())
                              , client)


def ooc_cmd_area_lock(client, arg):
    if not client.area.locking_allowed:
        client.send_host_message('Area locking is disabled in this area.')
        return
    if client.area.is_locked:
        client.send_host_message('Area is already locked.')
    if client.is_cm:
        client.area.is_locked = True
        client.area.send_host_message('Area is locked.')
        for i in client.area.clients:
            client.area.invite_list[i.ipid] = None
        return
    else:
        raise ClientError('Only CM can lock the area.')


def ooc_cmd_area_unlock(client, arg):
    if not client.area.is_locked:
        raise ClientError('Area is already unlocked.')
    if not client.is_cm:
        raise ClientError('Only CM can unlock area.')
    client.area.unlock()
    client.send_host_message('Area is unlocked.')


def ooc_cmd_invite(client, arg):
    if not arg:
        raise ClientError('You must specify a target. Use /invite <id>')
    if not client.area.is_locked:
        raise ClientError('Area isn\'t locked.')
    if not client.is_cm or client.is_mod:
        raise ClientError('You must be authorized to do that.')
    try:
        c = client.server.client_manager.get_targets(client, TargetType.ID, int(arg), False)[0]
        client.area.invite_list[c.ipid] = None
        client.send_host_message('{} is invited to your area.'.format(c.get_char_name()))
        c.send_host_message('You were invited and given access to area {}.'.format(client.area.id))
    except:
        raise ClientError('You must specify a target. Use /invite <id>')


def ooc_cmd_uninvite(client, arg):
    if not client.is_cm or client.is_mod:
        raise ClientError('You must be authorized to do that.')
    if not client.area.is_locked and not client.is_mod:
        raise ClientError('Area isn\'t locked.')
    if not arg:
        raise ClientError('You must specify a target. Use /uninvite <id>')
    arg = arg.split(' ')
    targets = client.server.client_manager.get_targets(client, TargetType.ID, int(arg[0]), True)
    if targets:
        try:
            for c in targets:
                client.send_host_message("You have removed {} from the whitelist.".format(c.get_char_name()))
                c.send_host_message("You were removed from the area whitelist.")
                if client.area.is_locked:
                    client.area.invite_list.pop(c.ipid)
        except AreaError:
            raise
        except ClientError:
            raise
    else:
        client.send_host_message("No targets found.")


def ooc_cmd_area_kick(client, arg):
    if not client.is_mod:
        raise ClientError('You must be authorized to do that.')
    if not client.area.is_locked and not client.is_mod:
        raise ClientError('Area isn\'t locked.')
    if not arg:
        raise ClientError('You must specify a target. Use /area_kick <id> [destination #]')
    arg = arg.split(' ')
    targets = client.server.client_manager.get_targets(client, TargetType.ID, int(arg[0]), False)
    if targets:
        try:
            for c in targets:
                if len(arg) == 1:
                    area = client.server.area_manager.get_area_by_id(int(0))
                    output = 0
                else:
                    try:
                        area = client.server.area_manager.get_area_by_id(int(arg[1]))
                        output = arg[1]
                    except AreaError:
                        raise
                client.send_host_message("Attempting to kick {} to area {}.".format(c.get_char_name(), output))
                c.change_area(area)
                c.send_host_message("You were kicked from the area to area {}.".format(output))
                if client.area.is_locked:
                    client.area.invite_list.pop(c.ipid)
        except AreaError:
            raise
        except ClientError:
            raise
    else:
        client.send_host_message("No targets found.")


def ooc_cmd_ooc_mute(client, arg):
    if not client.is_mod:
        raise ClientError('You must be authorized to do that.')
    if len(arg) == 0:
        raise ArgumentError('You must specify a target. Use /ooc_mute <OOC-name>.')
    targets = client.server.client_manager.get_targets(client, TargetType.OOC_NAME, arg, False)
    if not targets:
        raise ArgumentError('Targets not found. Use /ooc_mute <OOC-name>.')
    for c in targets:
        c.is_ooc_muted = True
    client.send_host_message('Muted {} existing client(s).'.format(len(targets)))


def ooc_cmd_ooc_unmute(client, arg):
    if not client.is_mod:
        raise ClientError('You must be authorized to do that.')
    if len(arg) == 0:
        raise ArgumentError('You must specify a target. Use /ooc_mute <OOC-name>.')
    targets = client.server.client_manager.get_targets(client, TargetType.OOC_NAME, arg, False)
    if not targets:
        raise ArgumentError('Target not found. Use /ooc_mute <OOC-name>.')
    for target in targets:
        target.is_ooc_muted = False
    client.send_host_message('Unmuted {} existing client(s).'.format(len(targets)))


def ooc_cmd_disemvowel(client, arg):
    if not client.is_mod:
        raise ClientError('You must be authorized to do that.')
    elif len(arg) == 0:
        raise ArgumentError('You must specify a target.')
    try:
        targets = client.server.client_manager.get_targets(client, TargetType.ID, int(arg), False)
    except:
        raise ArgumentError('You must specify a target. Use /disemvowel <id>.')
    if targets:
        for c in targets:
            logger.log_mod('[{}][{}] disemvowelled {} [{}].'.format(client.area.id, client.get_char_name(), c.get_ip(),
                                                                     c.get_char_name()), client)
            c.disemvowel = True
        client.send_host_message('Disemvowelled {} existing client(s).'.format(len(targets)))
    else:
        client.send_host_message('No targets found.')


def ooc_cmd_undisemvowel(client, arg):
    if not client.is_mod:
        raise ClientError('You must be authorized to do that.')
    elif len(arg) == 0:
        raise ArgumentError('You must specify a target.')
    try:
        targets = client.server.client_manager.get_targets(client, TargetType.ID, int(arg), False)
    except:
        raise ArgumentError('You must specify a target. Use /disemvowel <id>.')
    if targets:
        for c in targets:
            logger.log_mod('[{}][{}] undisemvowelled {} [{}].'.format(client.area.id, client.get_char_name(), c.get_ip(),
                                                                     c.get_char_name()), client)
            c.disemvowel = False
        client.send_host_message('Undisemvowelled {} existing client(s).'.format(len(targets)))
    else:
        client.send_host_message('No targets found.')


def ooc_cmd_gimp(client, arg):
    if not client.is_mod:
        raise ClientError('You must be authorized to do that.')
    elif len(arg) == 0:
        raise ArgumentError('You must specify a target.')
    try:
        if len(arg) == 12:
            targets = client.server.client_manager.get_targets(client, TargetType.IPID, arg, False)
        elif len(arg) < 12 and arg.isdigit():
            targets = client.server.client_manager.get_targets(client, TargetType.ID, int(arg), False)
        else:
            raise ArgumentError()
    except:
        raise ArgumentError('You must specify a target. Use /gimp <id> or <ipid>.')
        return
    if targets:
        for c in targets:
            logger.log_mod('[{}][{}] gimped {} [{}].'.format(client.area.id, client.get_char_name(), c.get_ip(),
                                                                     c.get_char_name()), client)
            c.gimp = True
        client.send_host_message('Gimped {} targets.'.format(len(targets)))
    else:
        client.send_host_message('No targets found.')


def ooc_cmd_ungimp(client, arg):
    if not client.is_mod:
        raise ClientError('You must be authorized to do that.')
    elif len(arg) == 0:
        raise ArgumentError('You must specify a target.')
    try:
        if len(arg) == 12 and arg.isdigit():
            targets = client.server.client_manager.get_targets(client, TargetType.IPID, arg, False)
        elif len(arg) < 12 and arg.isdigit():
            targets = client.server.client_manager.get_targets(client, TargetType.ID, int(arg), False)
    except:
        raise ArgumentError('You must specify a target. Use /gimp <id>.')
    if targets:
        for c in targets:
            logger.log_mod('[{}][{}] ungimped {} [{}].'.format(client.area.id, client.get_char_name(), c.get_ip(),
                                                                     c.get_char_name()), client)
            c.gimp = False
        client.send_host_message('Ungimped {} targets.'.format(len(targets)))
    else:
        client.send_host_message('No targets found.')


def ooc_cmd_blockdj(client, arg):
    if not client.is_mod:
        raise ClientError('You must be authorized to do that.')
    if len(arg) == 0:
        raise ArgumentError('You must specify a target. Use /blockdj <id>.')
    try:
        targets = client.server.client_manager.get_targets(client, TargetType.ID, int(arg), False)
    except:
        raise ArgumentError('You must enter a number. Use /blockdj <id>.')
    if not targets:
        raise ArgumentError('Target not found. Use /blockdj <id>.')
    for target in targets:
        target.is_dj = False
        target.send_host_message('A moderator muted you from changing the music.')
        logger.log_mod('[{}][{}] blocked {} [{}] from changing music.'.format(client.area.id, client.get_char_name(),
                        target.get_ip(), target.get_char_name()), client)
    client.send_host_message('You blocked {} from changing the music.'.format(targets[0].get_char_name()))


def ooc_cmd_unblockdj(client, arg):
    if not client.is_mod:
        raise ClientError('You must be authorized to do that.')
    if len(arg) == 0:
        raise ArgumentError('You must specify a target. Use /unblockdj <id>.')
    try:
        targets = client.server.client_manager.get_targets(client, TargetType.ID, int(arg), False)
    except:
        raise ArgumentError('You must enter a number. Use /unblockdj <id>.')
    if not targets:
        raise ArgumentError('Target not found. Use /blockdj <id>.')
    for target in targets:
        target.is_dj = True
        target.send_host_message('A moderator unmuted you from changing the music.')
        logger.log_mod('[{}][{}] unblocked {} [{}] from changing music.'.format(client.area.id, client.get_char_name(),
                        target.get_ip(), target.get_char_name()), client)
    client.send_host_message('You unblocked {} from changing the music.'.format(targets[0].get_char_name()))


def ooc_cmd_blockwtce(client, arg):
    if not client.is_mod:
        raise ClientError('You must be authorized to do that.')
    if len(arg) == 0:
        raise ArgumentError('You must specify a target. Use /blockwtce <id>.')
    try:
        targets = client.server.client_manager.get_targets(client, TargetType.ID, int(arg), False)
    except:
        raise ArgumentError('You must enter a number. Use /blockwtce <id>.')
    if not targets:
        raise ArgumentError('Target not found. Use /blockwtce <id>.')
    for target in targets:
        target.can_wtce = False
        target.send_host_message('A moderator blocked you from using judge signs.')
        logger.log_mod('[{}][{}] blocked {} [{}] from using judge signs.'.format(client.area.id, client.get_char_name(),
                        target.get_ip(), target.get_char_name()), client)
    client.send_host_message('You blocked {} from using the WT/CE buttons.'.format(targets[0].get_char_name()))


def ooc_cmd_unblockwtce(client, arg):
    if not client.is_mod:
        raise ClientError('You must be authorized to do that.')
    if len(arg) == 0:
        raise ArgumentError('You must specify a target. Use /unblockwtce <id>.')
    try:
        targets = client.server.client_manager.get_targets(client, TargetType.ID, int(arg), False)
    except:
        raise ArgumentError('You must enter a number. Use /unblockwtce <id>.')
    if not targets:
        raise ArgumentError('Target not found. Use /unblockwtce <id>.')
    for target in targets:
        target.can_wtce = True
        target.send_host_message('A moderator unblocked you from using judge signs.')
        logger.log_mod('[{}][{}] blocked {} [{}] from using judge signs.'.format(client.area.id, client.get_char_name(),
                        target.get_ip(), target.get_char_name()), client)
    client.send_host_message('You unblocked {} from using the WT/CE buttons. {}.'.format(targets[0].get_char_name()))


def ooc_cmd_vote(client, arg):
    if len(arg) == 0:
        polls = client.server.serverpoll_manager.show_poll_list()
        if not polls:
            client.send_host_message('There are currently no polls to vote for. Have a nice day, and God bless.')
        else:
            message = 'Current polls:'
            for x, poll in enumerate(polls):
                message += '\n{}. {}'.format(x + 1, poll)
            message += '\nEnter the number of the poll in which you would like to vote in. Enter 0 to cancel.'
            client.send_host_message(message)
            client.voting += 1
    else:
        client.send_host_message('This command doesn\'t take arguments')


def ooc_cmd_votelist(client, arg):
    if len(arg) > 0:
        client.send_host_message('This command doesn\'t take arguments')
    else:
        polls = client.server.serverpoll_manager.show_poll_list()
        if not polls:
            client.send_host_message('There are currently no polls.')
        else:
            message = 'Current polls:'
            for x, poll in enumerate(polls):
                message += '\n{}. {}'.format(x + 1, poll)
            client.send_host_message(message)


def ooc_cmd_pollset(client, arg):
    if client.is_mod:
        client.server.serverpoll_manager.add_poll(arg)
        client.send_host_message('Added {} as a poll.'.format(arg))
        logger.log_mod('[{}][{}] added {} as a poll.'.format(client.area.id, client.get_char_name(),
                        arg), client)
    else:
        return


def ooc_cmd_pollremove(client, arg):
    if client.is_mod:
        client.server.serverpoll_manager.remove_poll(arg)
        client.send_host_message('Removed {} as a poll.'.format(arg))
        logger.log_mod('[{}][{}] removed {} as a poll.'.format(client.area.id, client.get_char_name(),
                        arg), client)
    else:
        return


def ooc_cmd_addpolldetail(client, arg):
    if client.is_mod:
        if len(arg) == 0:
            client.send_host_message('Command must have an argument!')
        else:
            args = arg.split()
            poll = 1
            for word in args:
                if word.lower().endswith(':'):
                    break
                else:
                    poll += 1
            if poll == len(args):
                raise ArgumentError(
                    'Invalid syntax. Add \':\' in the end of pollname. \n \'/addpolldetail <poll name>: <detail>\'')
            poll_name = ' '.join(args[:poll])
            poll_name = poll_name[:len(poll_name) - 1]
            detail = ' '.join(args[poll:])
            if not detail:
                raise ArgumentError(
                    'Invalid syntax. Expected message after \':\'. \n \'/addpolldetail <poll name>: <detail>\'')
            x = client.server.serverpoll_manager.polldetail(poll_name, detail)
            if x == 1:
                client.send_host_message('Added "{}" as details in poll "{}"'.format(detail, poll_name))
                logger.log_mod('[{}][{}] detail to poll {}.'.format(client.area.id, client.get_char_name(),
                                                                     poll_name), client)
            else:
                client.send_host_message('Poll does not exist!')
    else:
        return


def ooc_cmd_kms(client, arg):
    targets = client.server.client_manager.get_targets(client, TargetType.IPID, client.ipid, False)
    for target in targets:
        if target != client:
            target.disconnect()
    client.send_host_message('Kicked other instances of client.')


def ooc_cmd_setupdate(client, arg):
    if client.is_mod:
        client.server.data['update'] = arg
        client.server.save_data()
        client.send_host_message('Update set!')
        logger.log_mod('[{}][{}] set the update to {}.'.format(client.area.id, client.get_char_name(),
                        arg), client)


def ooc_cmd_update(client, arg):
    try:
        client.send_host_message('Latest Update: {}'.format(client.server.data['update']))
    except ServerError:
        client.send_host_message('Update not set!')


def ooc_cmd_setthread(client, arg):
    if client.is_mod:
        client.server.data['thread'] = arg
        client.server.save_data()
        client.send_host_message('Thread set!')
        logger.log_mod('[{}][{}] set the thread to {}.'.format(client.area.id, client.get_char_name(),
                        arg), client)


def ooc_cmd_thread(client, arg):
    try:
        client.send_host_message('Curent Thread: {}'.format(client.server.data['thread']))
    except Exception as n:
        client.send_host_message(n)


def ooc_cmd_notecard(client, arg):
    if len(arg) == 0:
        raise ArgumentError('You must specify the contents of the note card.')
    client.area.cards[client.get_char_name()] = arg
    client.area.send_host_message('{} wrote a note card.'.format(client.get_char_name()))


def ooc_cmd_notecard_clear(client, arg):
    try:
        del client.area.cards[client.get_char_name()]
        client.area.send_host_message('{} erased their note card.'.format(client.get_char_name()))
    except KeyError:
        raise ClientError('You do not have a note card.')


def ooc_cmd_notecard_reveal(client, arg):
    if not client.is_cm and not client.is_mod:
        raise ClientError('You must be a CM or moderator to reveal cards.')
    if len(client.area.cards) == 0:
        raise ClientError('There are no cards to reveal in this area.')
    msg = 'Note cards have been revealed.\n'
    for card_owner, card_msg in client.area.cards.items():
        msg += '{}: {}\n'.format(card_owner, card_msg)
    client.area.cards.clear()
    client.area.send_host_message(msg)


def ooc_cmd_refresh(client, arg):
    if not client.is_mod:
        raise ClientError('You must be authorized to do that.')
    if len(arg) > 0:
        raise ClientError('This command does not take in any arguments!')
    else:
        try:
            client.server.refresh()
            client.send_host_message('You have reloaded the server.')
        except ServerError:
            raise


def ooc_cmd_judgelog(client, arg):
    if not client.is_mod:
        raise ClientError('You must be authorized to do that.')
    if len(arg) != 0:
        raise ArgumentError('This command does not take any arguments.')
    jlog = client.area.judgelog
    if len(jlog) > 0:
        jlog_msg = '== Judge Log =='
        for x in jlog:
            jlog_msg += '\r\n{}'.format(x)
        client.send_host_message(jlog_msg)
    else:
        raise ServerError('There have been no judge actions in this area since start of session.')


def ooc_cmd_togglemodcall(client, arg):
    if len(arg) != 0:
        raise ArgumentError("This command doesn't take any arguments")
    client.muted_modcall = not client.muted_modcall
    glob_stat = 'on'
    if client.muted_modcall:
        glob_stat = 'off'
    client.send_host_message('Modcalls turned {}.'.format(glob_stat))


def ooc_cmd_pollchoiceclear(client, arg):
    if client.is_mod:
        client.server.serverpoll_manager.clear_poll_choice(arg)
        client.send_host_message('Poll {} choices cleared.'.format(arg))
        logger.log_mod('[{}][{}] cleared poll {} choices.'.format(client.area.id, client.get_char_name(),
                        arg), client)
    else:
        return


def ooc_cmd_pollchoiceremove(client, arg):
    if client.is_mod:
        args = arg.split()
        ooc_name = 1
        for word in args:
            if word.lower().endswith(':'):
                break
            else:
                ooc_name += 1
        if ooc_name == len(args) + 1:
            raise ArgumentError('Invalid syntax. Add \':\' in the end of target.')
        poll = ' '.join(args[:ooc_name])
        poll = poll[:len(poll) - 1]
        choice = ' '.join(args[ooc_name:])
        if not choice:
            raise ArgumentError('Not enough arguments. Use /pollchoiceremove <poll>: <choice to be removed>.')
        x = client.server.serverpoll_manager.remove_poll_choice(client, poll, choice)
        if x is None:
            return
        client.send_host_message(
            'Removed {} as a choice in poll {}. Current choices:\n{} '.format(choice, poll, "\n".join(x)))
        logger.log_mod('[{}][{}] removed {} as a choice in poll {}.'.format(client.area.id, client.get_char_name(),
                        choice, poll), client)
    else:
        return


def ooc_cmd_pollchoiceadd(client, arg):
    if client.is_mod:
        args = arg.split()
        ooc_name = 1
        for word in args:
            if word.lower().endswith(':'):
                break
            else:
                ooc_name += 1
        if ooc_name == len(args) + 1:
            raise ArgumentError('Invalid syntax. Add \':\' in the end of target.')
        poll = ' '.join(args[:ooc_name])
        poll = poll[:len(poll) - 1]
        choice = ' '.join(args[ooc_name:])
        if not choice:
            raise ArgumentError('Not enough arguments. Use /pollchoiceremove <poll>: <choice to be removed>.')
        x = client.server.serverpoll_manager.add_poll_choice(client, poll, choice)
        if x is None:
            return
        client.send_host_message(
            'Added {} as a choice in poll {}. Current choices:\n{} '.format(choice, poll, "\n".join(x)))
        logger.log_mod('[{}][{}] added {} as a choice in poll {}.'.format(client.area.id, client.get_char_name(),
                        choice, poll), client)
    else:
        return


def ooc_cmd_makepollmulti(client, arg):
    if client.is_mod:
        x = client.server.serverpoll_manager.make_multipoll(arg)
        if x:
            client.send_host_message('Poll {} made multipoll.'.format(arg))
            logger.log_mod('[{}][{}] made poll {} a multipoll.'.format(client.area.id, client.get_char_name(),
                        arg), client)
        else:
            client.send_host_message('Poll {} made single poll.'.format(arg))
            logger.log_mod('[{}][{}] made poll {} a singlepoll.'.format(client.area.id, client.get_char_name(),
                        arg), client)
    else:
        return

"""
This module implements game server related status checks.
"""

import socket
import pickle
import os

from mcstatus import LegacyServer #remove on release of mcstatus 13
import discord

from Inglewood.decorator import retry


def server_status_check(
        server_name: str, domain: str, ports: list) -> str:
    """
    Performs status checks on Minecraft servers and returns a status
    string.

    Parameters:
        server_name : str
            the name of the Minecraft server
        domain : str
            the domain or IP address
        ports: int
            the game ports
    Returns:
        server_msg : str
            status information describing online status and web address
    """
    server_msg = f'**{server_name}**'
    for server_type, port_dict in ports.items():
        port = port_dict['port']
        if server_type != LegacyServer: #remove on release of mcstatus 13
            try:
                version = server_type(domain, port).status().version.name
                if 'Version' in port_dict:
                    version = port_dict['Version']
                server_msg += f'\nJava {version}: {domain}:{port}'
            except OSError:
                server_msg += '\nJava: Unavailable'

        else:  #remove on release of mcstatus 13
            server_msg += legacy_server_status_check( #remove on release of mcstatus 13
                domain, port, port_dict['Version']) #remove on release of mcstatus 13

    server_msg += '\n\n'
    return server_msg


async def initialisation(channel):
    if os.path.exists('message_id.pkl'):
        with open('message_id.pkl', 'rb') as f:
            message_id = pickle.load(f)
        try:
            message = await channel.fetch_message(message_id)
        except discord.errors.NotFound:
            os.remove('message_id.pkl')
            message = await initialisation_message(channel)
    else:
        message = await initialisation_message(channel)
    return message


async def initialisation_message(channel):
    message = await channel.send('placeholder')
    await message.pin()
    message_id = message.id
    with open('message_id.pkl', 'wb') as f:
        pickle.dump(message_id, f)
    return message


@retry(5, 'Java: Unavailable\n')
def legacy_server_status_check(
        domain: str, port: int, fail_over_ver: str) -> str:
    """
    Performs status checks on pre-1.7 Minecraft servers and returns a
    status string.

    Parameters:
        domain : str
            the domain or IP address
        port: int
            the game port
        fail_over_ver : str | None
            the java version number of the server 
    Returns:
        string : str
            status string describing online status and web address
    """
    server = socket.socket()
    server.connect((domain, port))
    server.sendall(b'\xfe\x01\xfa')
    server.recv(1024)
    string = f'\nJava {fail_over_ver}: {domain}:{port}'
    return string

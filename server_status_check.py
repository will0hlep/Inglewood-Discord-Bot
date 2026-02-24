"""
This module implements game server related status checks.
"""

import socket

from mcstatus import JavaServer, BedrockServer

from decorators import retry


def server_status_check(
        server_name: str, domain: str, port: int, bed_port: int | None = None,
        fail_over_ver: str | None = None) -> str:
    """
    Performs status checks on Minecraft servers and returns a status
    string.

    Parameters:
        server_name : str
            the name of the Minecraft server
        domain : str
            the domain or IP address
        port: int
            the game port
        bed_port : int | None
            the geyser game port
        fail_over_ver : str | None
            the java version number of the server 
    Returns:
        string : str
            status string describing online status and web address
    """
    string = f'**{server_name}**\n'
    try:
        jarversion = JavaServer.lookup(f"{domain}:{port}").status().version.name
        string += f'Java {jarversion}: {domain}:{port}\n'
    except OSError:
        if fail_over_ver is not None:
            string += legacy_server_status_check(domain, port, fail_over_ver)
        else:
            string += 'Java: Unavailable\n'
    if bed_port is not None:
        try:
            bedversion = BedrockServer.lookup(f"{domain}:{bed_port}").status().version.name
            string += f'Bedrock {bedversion}: {domain}:{bed_port}\n'
        except OSError:
            string += 'Bedrock: Unavailable\n'
    string += '\n'
    return string


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
    string = f'Java {fail_over_ver}: {domain}:{port}\n'
    return string

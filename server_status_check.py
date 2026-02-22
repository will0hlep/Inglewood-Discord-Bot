import socket
from mcstatus import JavaServer, BedrockServer
from decorators import retry

def server_status_check(server, domain, port, bed_port = None, fail_over_ver = None):
    string = f'**{server}**\n'
    try:
        jarversion = JavaServer.lookup(f"{domain}:{port}").status().version.name
        string += f'Java {jarversion}: {domain}:{port}\n' #\nBedrock: williamrpaine.com:23376\n
    except:
        if fail_over_ver is not None:
            string += legacy_server_status_check(server, domain, port, fail_over_ver)
        else:
            string += f'Java: Unavailable\n'
    if bed_port is not None:
        try:
            bedversion = BedrockServer.lookup(f"{domain}:{bed_port}").status().version.name
            string += f'Bedrock {bedversion}: {domain}:{bed_port}\n'
        except:
            string += f'Bedrock: Unavailable\n'
    string += '\n'
    return string

@retry(5, f'Java: Unavailable\n')
def legacy_server_status_check(server, domain, port, fail_over_ver):
    server = socket.socket()
    server.connect((domain, port))
    server.sendall(b'\xfe\x01\xfa')
    server.recv(1024)
    string = f'Java {fail_over_ver}: {domain}:{port}\n'
    return string
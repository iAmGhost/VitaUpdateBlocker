import os
import socket
from urlparse import parse_qs
from libmproxy import controller, proxy
import re
import time
import sys
import urllib


class VitaUpdateBlockerMaster(controller.Master):
    request_version_string = None

    def __init__(self, server):
        controller.Master.__init__(self, server)
        self.stickyhosts = {}

    def run(self):
        try:
            return controller.Master.run(self)
        except KeyboardInterrupt:
            self.shutdown()

    def handle_request(self, msg):
        if 'psp2-updatelist.xml' in msg.path:
            query = parse_qs(msg.path.split('?')[1])
            version = query['ver'][0]

            self.request_version_string = "%s.%s.%s" % (version[0:2],
                                                        version[2:5],
                                                        version[5:9])

            log("Vita's real version is: %s" % self.request_version_string)

            path = msg.path[0:msg.path.find('&sid')]
            content = urllib.urlopen("http://%s%s" % (msg.host, path)).read()

            latest_version = re.search(r'level1_system_version="(.+?)"',
                                       content).group(1)

            log("latest version is: %s" % latest_version)

            latest_version = latest_version.replace('.', '')

            msg.path = msg.path.replace('?ver=%s' % query['ver'],
                                        latest_version)
        else:
            msg.path = '/'
            msg.host = '255.255.255.255'

        msg.reply()

    def handle_response(self, msg):
        if 'psp2.update.playstation.net' in msg.request.host:
            version = self.request_version_string

            msg.content = re.sub(r'level1_system_version=".+?"',
                                 'level1_system_version="%s"' % version,
                                 msg.content)
            msg.content = re.sub(r'level2_system_version=".+?"',
                                 'level2_system_version="%s"' % version,
                                 msg.content)

            msg.content = re.sub(r'<version system_version=".+" ',
                                 '<version system_version="%s" ' % version,
                                 msg.content)

            log("Spoofed latest version to %s." % version)
            log("You can disable proxy settings now.")
        else:
            msg.content = '._.)?'

        msg.reply()


def show_intro():
    print ("""
==================================
VitaUpdateBlocker v1.1
http://iamghost.kr
==================================
""".strip())


def show_network_info(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("www.google.com", 80))
    host = s.getsockname()[0]
    s.close()

    log("Listening on %s:%d" % (host, port))


def log(text):
    time_str = time.asctime(time.localtime(time.time()))
    print("[%s] %s" % (time_str, text))


def main():
    port = 8080

    try:
        port = int(sys.argv[1])
    except Exception:
        pass

    show_intro()
    show_network_info(port)

    config = proxy.ProxyConfig(
        cacert=os.path.expanduser("~/.mitmproxy/mitmproxy-ca.pem")
    )
    server = proxy.ProxyServer(config, port)
    m = VitaUpdateBlockerMaster(server)
    m.run()

if __name__ == '__main__':
    main()

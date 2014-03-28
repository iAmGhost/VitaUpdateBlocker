import os
import socket
from urlparse import parse_qs
from libmproxy import controller, proxy
import re
import time
import sys


class VitaUpdateBlockerMaster(controller.Master):
    def __init__(self, server):
        controller.Master.__init__(self, server)
        self.stickyhosts = {}

    def run(self):
        try:
            return controller.Master.run(self)
        except KeyboardInterrupt:
            self.shutdown()

    def handle_request(self, msg):
        msg.reply()

    def handle_response(self, msg):
        if 'psp2.update.playstation.net' in msg.request.host:
            query = parse_qs(msg.request.path.split('?')[1])
            version = re.sub('(\d{2})(\d{3})(\d{3})',
                             '\g<1>.\g<2>.\g<3>',
                             query['ver'][0])

            msg.content = re.sub('level1_system_version=".+?"',
                                 'level1_system_version="%s"' % version,
                                 msg.content)
            msg.content = re.sub('level2_system_version=".+?"',
                                 'level2_system_version="%s"' % version,
                                 msg.content)

            msg.content = re.sub('<version system_version=".+" ',
                                 '<version system_version="%s" ' % version,
                                 msg.content)

            log("Spoofed latest version to %s." % version)

        msg.reply()


def show_intro():
    print ("""
==================================
VitaUpdateBlocker v1.0
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
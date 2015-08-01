import os
import socket
from urlparse import parse_qs
from libmproxy import controller, proxy
from libmproxy.proxy.server import ProxyServer
import re
import time
import sys
import urllib
import argparse


class VitaUpdateBlockerMaster(controller.Master):
    request_version_string = None

    def __init__(self, server, block_traffics=False):
        controller.Master.__init__(self, server)
        self.stickyhosts = {}
        self.block_traffics = block_traffics

    def run(self):
        try:
            return controller.Master.run(self)
        except KeyboardInterrupt:
            self.shutdown()

    def handle_request(self, msg):
        req = msg.request
        if 'psp2-updatelist.xml' in req.path and \
           req.host[-15:] == 'playstation.net':
            query = parse_qs(req.path.split('?')[1])
            version = query['ver'][0]

            self.request_version_string = "%s.%s.%s" % (version[0:2],
                                                        version[2:5],
                                                        version[5:9])

            log("Vita's real version is: %s" % self.request_version_string)

            path = req.path[0:req.path.find('&sid')]
            content = urllib.urlopen("http://%s%s" % (req.host, path)).read()

            latest_version = re.search(r'level1_system_version="(.+?)"',
                                       content).group(1)

            log("latest version is: %s" % latest_version)

            latest_version = latest_version.replace('.', '')

            req.path = req.path.replace('?ver=%s' % query['ver'],
                                        latest_version)
        else:
            if self.block_traffics:
                req.path = '/'
                req.host = '255.255.255.255'

        msg.reply()

    def handle_response(self, msg):
        req = msg.request
        res = msg.response
        if 'psp2-updatelist.xml' in req.path and \
           req.host[-15:] == 'playstation.net':
            version = self.request_version_string

            res.content = re.sub(r'level1_system_version=".+?"',
                                 'level1_system_version="%s"' % version,
                                 res.content)
            res.content = re.sub(r'level2_system_version=".+?"',
                                 'level2_system_version="%s"' % version,
                                 res.content)

            res.content = re.sub(r'<version system_version=".+" ',
                                 '<version system_version="%s" ' % version,
                                 res.content)

            log("Spoofed latest version to %s." % version)
            log("You can disable proxy settings now.")
        else:
            if self.block_traffics:
                res.content = '._.)?'

        msg.reply()


def show_intro():
    print ("""
==================================
VitaUpdateBlocker v1.2a
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
    parser = argparse.ArgumentParser(prog='PROG',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--port', type=int, default=8080, help='Proxy port')
    parser.add_argument('--block-traffics', default=False, action='store_true')

    args = parser.parse_args(sys.argv[1:])

    port = args.port

    show_intro()
    show_network_info(port)

    if not args.block_traffics:
        log("Blocking non-related traffic is DISABLED.")
    else:
        log("Blocking non-related traffic is ENABLED.")

    config = proxy.ProxyConfig(port=port)
    server = ProxyServer(config)
    m = VitaUpdateBlockerMaster(server, block_traffics=args.block_traffics)
    m.run()

if __name__ == '__main__':
    main()

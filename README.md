VitaUpdateBlocker
=================
This application does what [Chales Proxy Trick](http://wololo.net/2013/01/25/psn-and-online-features-on-without-updating-on-fw-2-02-charles-proxy/) does but without hassle.

Also this is Python based cross-platform application so you can even install this application to 24/7 running server to access PSN anyhwere.

Features
========
* Automatically detects latest OFW version and Vita's version.
* Blocks other requests than update information so you can host this script without worrying about consuming traffic.

Portable Version
================
You can get portable executable for Windows [here](https://www.mediafire.com/folder/hgd33h95ooh9p/VitaUpdateBlocker)

Instructions
============
1. Start VitaUpdateBlocker.exe (or python vita_update_blocker.py)
2. Open Settings app on your Vita, Go to Network-Wi-Fi Setting-AP Name-Advances Settings.
3. Change proxy settings to ip:port that shown on VitaUpdateBlocker.
4. Save settings and open PS Store application.
5. You'll see front page of store, go Settings app again and disable proxy.
6. Download contents from store or play games online.

Requirements
============
To use VitaUpdateBlocker you need these requirements(portable version users can ignore this)

* Python 2.7.6 (Python 3 is not supported due to compatibility with mitmproxy)
* [mitmproxy](http://mitmproxy.org)
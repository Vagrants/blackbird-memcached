blackbird-memcached
===================

Get result of following command(not shell command) result.

* stats

config file
-----------

| name                              | default   | type                | notes                         |
|-----------------------------------|-----------|---------------------|-------------------------------|
| host                              | 127.0.0.1 | string              | memcached host                |
| port                              | 11211     | interger(1 - 65535) | memcached lisetn port         |
| timeout                           | 10        | interger            | socket timeout of this script |
| profile\_include\_conn\_establish | False     | boolean             |                               |
| module                            | memcached | string              | only require option           |

Pleases see the "scripts/memcached.cfg".

### profile\_include\_conn\_establish
memcached.py script get response time("set" and "get" command). If you set "profile\_include\_conn\_establish" is True, response time includes time that connection establishing.

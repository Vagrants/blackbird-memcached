#!/usr/bin/env python
# -*- coding: utf-8 -*-
u"""\"memcached-tool 127.0.0.1:11211 stats\" to ZabbixServer."""

import telnetlib
from datetime import datetime

from blackbird.plugins import base


class ConcreteJob(base.JobBase):
    """
    This Class is called by "Executer"
    ConcreteJob is registerd as a job of Executer.
    """

    def __init__(self, options, queue=None, logger=None):
        super(ConcreteJob, self).__init__(options, queue, logger)

    def looped_method(self):
        """
        Get stats data of memcached by using telnet.
        """

        conn = telnetlib.Telnet()
        conn.open(
            host=self.options['host'],
            port=self.options['port'],
            timeout=self.options['timeout']
        )

        conn.write('stats\r\n')
        result = conn.read_until('END').splitlines()
        conn.close()

        # send stats data
        for line in result:
            if line.startswith('END'):
                break

            line = line.split()
            key = line[1]
            value = line[2]
            self._enqueue(key, value, self.options['hostname'])
            self.logger.debug(
                ('Inserted to queue memcached.{key}:{value}'
                 ''.format(key=key, value=value)
                 )
            )

        # send response time
        key = 'set_response_time'
        value = self._set_command_response_time(
            host=self.options['host'],
            port=self.options['port'],
            timeout=self.options['timeout'],
            profile_include_conn_establish=
            self.options['profile_include_conn_establish']
        )
        self._enqueue(key, value, self.options['hostname'])
        self.logger.debug(
            ('Inserted to queue memcached.{key}:{value}'
             ''.format(key=key, value=value)
             )
        )

        key = 'get_response_time'
        value = self._get_command_response_time(
            host=self.options['host'],
            port=self.options['port'],
            timeout=self.options['timeout'],
            profile_include_conn_establish=
            self.options['profile_include_conn_establish']
        )
        self._enqueue(key, value, self.options['hostname'])
        self.logger.debug(
            ('Inserted to queue memcached.{key}:{value}'
             ''.format(key=key, value=value)
             )
        )

    def _enqueue(self, item_key, item_value, item_host):
        item = MemcachedItem(
            key=item_key,
            value=item_value,
            host=item_host
        )
        self.queue.put(item, block=False)

    def _set_command_response_time(self, host, port, timeout=10,
                                   key='__zabbix_check',
                                   profile_include_conn_establish=False):
        """
        Get "set" command response time.
        """

        value = datetime.now()
        value = value.strftime('%Y%m%d%H%M%S')
        length = len(value)
        value = '{0}\r\n'.format(value)
        data = (
            'set {key} 0 86400 {length}\r\n'
            ''.format(key=key, length=length)
        )

        if profile_include_conn_establish:
            with base.Timer() as timer:
                conn = telnetlib.Telnet()
                conn.open(
                    host=host,
                    port=port,
                    timeout=timeout
                )
                conn.write(data)
                conn.write(value)
                data = conn.read_some()
                conn.close()

        else:
            conn = telnetlib.Telnet()
            conn.open(
                host=host,
                port=port,
                timeout=timeout
            )
            with base.Timer() as timer:
                conn.write(data)
                conn.write(value)
                data = conn.read_some()
            conn.close()

        if 'STORED' in data:
            return timer.sec
        elif 'ERROR' in data:
            return None
        else:
            return None

    def _get_command_response_time(self, host, port, timeout=10,
                                   key='__zabbix_check',
                                   profile_include_conn_establish=False):
        """
        Get "get" command response time.
        """

        data = 'get {0}\r\n'.format(key)

        if profile_include_conn_establish:
            with base.Timer() as timer:
                conn = telnetlib.Telnet()
                conn.open(
                    host=host,
                    port=port,
                    timeout=timeout
                )
                conn.write(data)
                data = conn.read_some()
                conn.close()

        else:
            conn = telnetlib.Telnet()
            conn.open(
                host=host,
                port=port,
                timeout=timeout
            )
            with base.Timer() as timer:
                conn.write(data)
                data = conn.read_some()
            conn.close()

        if not 'ERROR' in data:
            return timer.sec
        else:
            return None


class MemcachedItem(base.ItemBase):
    """
    Enqueued item.
    Take key(used by zabbix) and value as argument.
    """

    def __init__(self, key, value, host):
        super(MemcachedItem, self).__init__(key, value, host)

        self.__data = {}
        self._generate()

    @property
    def data(self):
        """Dequeued data."""

        return self.__data

    def _generate(self):
        """
        Convert to the following format:
        MemcachedItem(key='uptime', value='65535')
        {host:host, key:key1, value:value1, clock:clock}
        """

        self.__data['key'] = 'memcached.{0}'.format(self.key)
        self.__data['value'] = self.value
        self.__data['host'] = self.host
        self.__data['clock'] = self.clock


class Validator(base.ValidatorBase):
    """
    This class store information
    which is used by validation config file.
    """

    def __init__(self):
        self.__spec = None

    @property
    def spec(self):
        self.__spec = (
            "[{0}]".format(__name__),
            "host = ipaddress(default='127.0.0.1')",
            "port = integer(0, 65535, default=11211)",
            "timeout = integer(default=10)",
            "hostname = string(default={0})".format(self.gethostname()),
            "profile_include_conn_establish = boolean(default=False)",
        )
        return self.__spec


if __name__ == '__main__':
    OPTIONS = {
        'host': '127.0.0.1',
        'port': 11211,
        'timeout': 1
    }
    MEMCACHED_JOB = ConcreteJob(options=OPTIONS)
    RESULT = MEMCACHED_JOB._set_command_response_time(
        host=OPTIONS['host'],
        port=OPTIONS['port'],
        timeout=OPTIONS['timeout']
    )
    print('"set" command response time: {0}sec'.format(RESULT))
    RESULT = MEMCACHED_JOB._get_command_response_time(
        host=OPTIONS['host'],
        port=OPTIONS['port'],
        timeout=OPTIONS['timeout']
    )
    print('"get" command response time: {0}sec'.format(RESULT))

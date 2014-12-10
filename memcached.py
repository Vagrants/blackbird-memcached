#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=protected-access,too-few-public-methods
u"""\"memcached-tool 127.0.0.1:11211 stats\" to ZabbixServer."""

__VERSION__ = '0.1.4'

import telnetlib
import socket
from datetime import datetime

from blackbird.plugins import base


class ConcreteJob(base.JobBase):
    """
    This Class is called by "Executer"
    ConcreteJob is registerd as a job of Executer.
    """

    def __init__(self, options, queue=None, logger=None):
        super(ConcreteJob, self).__init__(options, queue, logger)

    def build_items(self):
        """
        Get stats data of memcached by using telnet.
        """

        # ping item
        self._ping()

        # send stats data
        self._get_stats()

        # send setting value
        self._get_settings()

        # send response time
        self._response_time()

    def _ping(self):
        """
        send ping item
        """
        self._enqueue('blackbird.memcached.ping', 1)
        self._enqueue('blackbird.memcached.version', __VERSION__)

    def _get_stats(self):
        """
        get memcached stats
        """
        conn = self._connect()
        conn.write('stats\r\n')
        result = conn.read_until('END').splitlines()
        conn.close()

        for line in result:
            if line.startswith('END'):
                break

            line = line.split()
            key = 'memcached.{0}'.format(line[1])
            value = line[2]
            self._enqueue(key, value)

    def _get_settings(self):
        """
        get memcached setting value
        """
        conn = self._connect()
        conn.write('stats settings\r\n')
        result = conn.read_until('END').splitlines()
        conn.close()

        for line in result:
            if line.startswith('END'):
                break

            line = line.split()
            key = 'memcached.settings.{0}'.format(line[1])
            value = line[2]
            self._enqueue(key, value)

    def _response_time(self):
        """
        get response time
        """
        self._enqueue(
            'memcached.set_response_time',
            self._set_command_response_time()
        )
        self._enqueue(
            'memcached.get_response_time',
            self._get_command_response_time()
        )

    def _connect(self):
        """
        connect to memcached
        """
        conn = telnetlib.Telnet()

        try:
            conn.open(
                host=self.options['host'],
                port=self.options['port'],
                timeout=self.options['timeout']
            )
        except socket.error as err:
            raise base.BlackbirdPluginError(
                'connect failed. {0}'.format(err)
            )

        return conn

    def _enqueue(self, key, value):
        """
        insert MemcachedItem to queue
        """
        item = MemcachedItem(
            key=key,
            value=value,
            host=self.options['hostname']
        )
        self.queue.put(item, block=False)
        self.logger.debug(
            'Inserted to queue {key}:{value}'
            ''.format(key=key, value=value)
        )

    def _set_command_response_time(self, key='__zabbix_check'):
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

        if self.options['profile_include_conn_establish']:
            with base.Timer() as timer:
                conn = self._connect()
                conn.write(data)
                conn.write(value)
                data = conn.read_some()
                conn.close()

        else:
            conn = self._connect()
            with base.Timer() as timer:
                conn.write(data)
                conn.write(value)
                data = conn.read_some()
            conn.close()

        if 'STORED' in data:
            return timer.sec
        else:
            return 0

    def _get_command_response_time(self, key='__zabbix_check'):
        """
        Get "get" command response time.
        """

        data = 'get {0}\r\n'.format(key)

        if self.options['profile_include_conn_establish']:
            with base.Timer() as timer:
                conn = self._connect()
                conn.write(data)
                data = conn.read_some()
                conn.close()

        else:
            conn = self._connect()
            with base.Timer() as timer:
                conn.write(data)
                data = conn.read_some()
            conn.close()

        if not 'ERROR' in data:
            return timer.sec
        else:
            return 0


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

        self.__data['key'] = self.key
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
            "host = string(default='127.0.0.1')",
            "port = integer(0, 65535, default=11211)",
            "timeout = integer(default=10)",
            "hostname = string(default={0})".format(self.detect_hostname()),
            "profile_include_conn_establish = boolean(default=False)",
        )
        return self.__spec


if __name__ == '__main__':
    # pylint: disable=pointless-string-statement
    """
    For debug

    $ python memcached.py
    "set" command response time: 0.000669sec
    "get" command response time: 0.000484sec
    """

    OPTIONS = {
        'host': '127.0.0.1',
        'port': 11211,
        'timeout': 1,
        'profile_include_conn_establish': True
    }
    MEMCACHED_JOB = ConcreteJob(options=OPTIONS)

    print (
        '"set" command response time: {0}sec'
        ''.format(MEMCACHED_JOB._set_command_response_time())
    )

    print (
        '"get" command response time: {0}sec'
        ''.format(MEMCACHED_JOB._get_command_response_time())
    )

#!/usr/bin/env python
# -*- coding: utf-8 -*-
u"""\"memcached-tool 127.0.0.1:11211 stats\" to ZabbixServer."""

import telnetlib
import math
from datetime import datetime

from blackbird.plugins import base


class ConcreteJob(base.JobBase):
    """
    This Class is called by "Executer"
    ConcreteJob is registerd as a job of Executer.
    """

    def __init__(self, options, queue=None, logger=None):
        super(ConcreteJob, self).__init__(options, queue, logger)
        self.set_time = 0.0
        self.get_time = 0.0

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

        with base.Timer() as timer:
            self._set_zabbix_check(conn=conn)

        self.set_time = str(round(timer.sec,4))

        with base.Timer() as timer:
            self._get_response_time(conn=conn)

        self.get_time = str(round(timer.sec,4))

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
        set_key = 'set_response_time'
        self._enqueue(set_key, self.set_time, self.options['hostname'])
        self.logger.debug(
            ('Inserted to queue memcached.{key}:{value}'
             ''.format(key=set_key, value=self.set_time)
             )
        )

        get_key = 'get_response_time'
        self._enqueue(get_key, self.get_time, self.options['hostname'])
        self.logger.debug(
            ('Inserted to queue memcached.{key}:{value}'
             ''.format(key=get_key, value=self.get_time)
             )
        )
        

    def _enqueue(self, item_key, item_value, item_host):
        item = MemcachedItem(
            key=item_key,
            value=item_value,
            host=item_host
        )
        self.queue.put(item, block=False)

    def _set_zabbix_check(self, conn, key='__zabbix_check'):
        """
        Set zabbix_check value for checking response time.
        value length is 14(hard-corded).
        """

        value = datetime.now()
        value = value.strftime('%Y%m%d%H%M%S')
        value = '{0}\r\n'.format(value)
        data = 'set {0} 0 10 14\r\n'.format(key)

        conn.write(data)
        conn.write(value)
        conn.read_until('STORED')

    def _get_response_time(self, conn, key='__zabbix_check'):
        """
        Get memcached response time.
        """

        data = 'get {0}\r\n'.format(key)
        conn.write(data)
        conn.read_until('END')


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
        )
        return self.__spec


if __name__ == '__main__':
    OPTIONS = {
        'host': '127.0.0.1',
        'port': 11211,
        'timeout': 1
    }
    MEMCACHED_CONN = telnetlib.Telnet()
    MEMCACHED_CONN.open(
        host=OPTIONS['host'],
        port=OPTIONS['port'],
        timeout=OPTIONS['timeout']
    )
    MEMCACHED_JOB = ConcreteJob(options=OPTIONS)
    print MEMCACHED_JOB._set_zabbix_check(conn=MEMCACHED_CONN)
    print MEMCACHED_JOB._get_response_time(conn=MEMCACHED_CONN)
    MEMCACHED_CONN.close()


import time
from .constants import *
import socket
import struct
import datetime
import select


class PingSocket:
    def __init__(self, ip, identifier):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        self._ip = ip
        self._identifier = identifier
        self._sequence = 0
        self._start_time = datetime.datetime.now()
        self._packet = None

    @property
    def ip(self):
        return self._ip

    @ip.setter
    def ip(self, ip):
        if ip != self._ip:
            self._ip = ip

    @property
    def is_timeout(self):
        return (datetime.datetime.now() - self._start_time).total_seconds() > self._socket.gettimeout()

    @staticmethod
    def cal_checksum(data):
        checksum = 0
        num_words = len(data) // 2
        for i in range(num_words):
            word = (data[i * 2] << 8) + data[i * 2 + 1]
            checksum += word
        checksum = (checksum >> 16) + (checksum & 0xffff)
        return ~checksum & 0xffff

    def _get_header(self, checksum=0):
        return struct.pack('!BBHHH', ICMP_ECHO_REQUEST, 0, checksum, self._identifier, self._sequence)

    def _get_packet(self, count):
        self._sequence = (self._sequence + 1) % 2 ** 16
        header = self._get_header()
        payload = bytes(bytearray([i % 256 for i in range(count)]))
        checksum = self.cal_checksum(header + payload)
        header = self._get_header(checksum)
        return header + payload

    def send(self, buffer_size=32, ttl=128, timeout=4000):
        self._socket.settimeout(timeout / 1000)
        self._socket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
        self._packet = self._get_packet(buffer_size)
        self._socket.sendto(self._packet, (self._ip, 0))
        self._start_time = datetime.datetime.now()

    def receive(self):
        answer = None
        while not answer:
            response = None
            while not (self.is_timeout or response):
                r, _, _ = select.select([self._socket], [], [], 0)
                if r:
                    response, src_ip = self._socket.recvfrom(2**16)
                    response_identifier, response_sequence = struct.unpack('!HH', response[24:28])
                    rtt = int((datetime.datetime.now() - self._start_time).total_seconds() * 1000) + 1
                    response_type = response[20]
                    ttl = struct.unpack('!B', response[8:9])[0]
                    if response_identifier != self._identifier or response_sequence != self._sequence:
                        continue
                    if response_type == 0:
                        answer = (f'Reply from {src_ip[0]}: bytes={len(self._packet)} time={rtt}ms TTL={ttl}', rtt)
                    elif response_type == 3:
                        answer = (f'Reply from {src_ip[0]}: Destination host unreachable.', 0)
                    elif response_type == 11:
                        answer = (f'Reply from {src_ip[0]}: TTL expired in transit.', 0)
                    else:
                        answer = ('Unknown response.', 0)
                else:
                    time.sleep(0.01)
            else:
                if self.is_timeout:
                    answer = ('Request timed out.', 0)
        return answer

    def close(self):
        self._socket.close()


def main():
    p1 = PingSocket('223.255.135.120', 90)
    # p2 = PingSocket('223.255.135.8', 1)
    p3 = PingSocket('223.255.135.17', 2)
    while True:
        # p3.send()
        # p2.send()
        p1.send()
        print(p1.receive())
        # print(p2.receive())
        # print(p3.receive())


if __name__ == '__main__':
    main()

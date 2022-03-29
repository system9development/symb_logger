import logging
import asyncio
import aiohttp
import socket
import sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(message)s',
                              '%m-%d-%Y %H:%M:%S')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler('./logs/symb_ips.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stdout_handler)

URL = "wss://matching-spot-sandbox.symbridge.com:8081"


async def main():
    while True:
        await asyncio.sleep(1.0)
        # Logging out first IP (AF_INET, SOCK_STREAM, since websockets == TCP, but all socket types leading to same IP anyways)
        try:
            ip = socket.getaddrinfo("matching-spot-sandbox.symbridge.com", 8081)[0][4]
            ip = f"{ip[0]}:{ip[1]}"
            logger.info(f"{ip}")
        except Exception as e:
            logger.info(f"{e}")

if __name__ == '__main__':
    asyncio.run(main())

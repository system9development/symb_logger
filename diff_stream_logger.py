import logging
import ujson
import rsa
import base64
import websockets
import asyncio
import time
from datetime import datetime, timedelta

test_url = "wss://matching-spot-sandbox.symbridge.com:8081"

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(message)s',
                              '%m-%d-%Y %H:%M:%S')
file_handler = logging.FileHandler('./logs/symb_diff_stream.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

async def main():
    try:
        conn = await websockets.connect(test_url)

        ibooks_payload = {
            "request": [{
                "msg": "ibook",
                "security": "BTCUSD"
            }],
            "type": "subscribe"
        }

        await conn.send(ujson.dumps(ibooks_payload))

        snapshot = False
        while True:
            res = await conn.recv()
            res = ujson.loads(res)
            if res.get("type") == "book" and not snapshot:
                snapshot = True
                logger.info(f"\nTHIS IS A SNAPSHOT WITH TYPE \'BOOK\'\n {res}")
            else:
                logger.info(f"\nTHIS IS A DIFF WITH TYPE \'BOOK\' \n {res}")

    except Exception as e:
        logger.error(f"ERROR:{e}", exc_info=True)

if __name__ == '__main__':
    asyncio.run(main())
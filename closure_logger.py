import logging
import websockets
import asyncio
import ujson
import datetime
import sys
import rsa
import base64

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(message)s',
                              '%m-%d-%Y %H:%M:%S')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler('./logs/symb_closure_metrics.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stdout_handler)


class ConnTester:
    """
    Issue is that when one of the tasks leaves WS connections unclosed, the 1000 code is sent to websockets besides the ones left open
    """

    def __init__(self):
        self.url = "wss://matching-spot-sandbox.symbridge.com:8081"
        self.pwd = ""

    async def start_ws(self):
        while True:
            try:
                ws = await asyncio.wait_for(websockets.connect(self.url), timeout=5.0)
                payload = {"type": "challenge"}
                await asyncio.wait_for(ws.send(ujson.dumps(payload)), timeout=5.0)
                res = await ws.recv()
                pub_key = ujson.loads(res).get("key")

                test_pub_key = b'-----BEGIN PUBLIC KEY-----\n' + bytes(pub_key.encode('ascii')) + b'\n-----END PUBLIC KEY-----\n'

                test_pub_key = rsa.PublicKey.load_pkcs1_openssl_pem(test_pub_key)
                cipher_pwd = base64.b64encode(rsa.encrypt(bytes(self.pwd, 'utf-8'), test_pub_key))

                auth_payload = {
                    "type": "login",
                    "userid": "justin@system9.io",
                    "pass": cipher_pwd.decode('utf-8')
                }
                await ws.send(ujson.dumps(auth_payload))
                res = await ws.recv()
                res = ujson.loads(res)
                while res.get('type') != "login":
                    res = await ws.recv()
                    res = ujson.loads(res)
                if res.get('result') == "OK":
                    logger.info("START_WS_OK")
                else:
                    raise Exception(f"{res.get(result)}")
                await ws.close()
            except Exception as e:
                print(e)
                if "1000" in str(e):
                    logger.error(f"WS_ERROR:{e}")
            finally:
                await asyncio.sleep(1.0)

    async def start_other_ws(self):
        while True:
            try:
                ws = await asyncio.wait_for(websockets.connect(self.url), timeout=5.0)
                payload = {"type": "challenge"}
                await asyncio.wait_for(ws.send(ujson.dumps(payload)), timeout=5.0)
                res = await ws.recv()
                pub_key = ujson.loads(res).get("key")

                test_pub_key = b'-----BEGIN PUBLIC KEY-----\n' + bytes(pub_key.encode('ascii')) + b'\n-----END PUBLIC KEY-----\n'

                test_pub_key = rsa.PublicKey.load_pkcs1_openssl_pem(test_pub_key)
                cipher_pwd = base64.b64encode(rsa.encrypt(bytes(self.pwd, 'utf-8'), test_pub_key))

                auth_payload = {
                    "type": "login",
                    "userid": "justin@system9.io",
                    "pass": cipher_pwd.decode('utf-8')
                }
                await ws.send(ujson.dumps(auth_payload))
                res = await ws.recv()
                res = ujson.loads(res)
                while res.get('type') != "login":
                    res = await ws.recv()
                    res = ujson.loads(res)
                if res.get('result') == "OK":
                    logger.info("START_OTHER_WS_OK")
                else:
                    raise Exception(f"{res.get('result')}")
                # We don't close these connections, but receive 1000 codes in OTHER method's connections
                # await ws.close()
            except Exception as e:
                if "1000" in str(e):
                    logger.error(f"OTHER_WS_ERROR:{e}")
            finally:
                await asyncio.sleep(1.0)
async def main():
    our_obj = ConnTester()
    await asyncio.gather(our_obj.start_ws(), our_obj.start_other_ws())

if __name__ == '__main__':
    asyncio.run(main())
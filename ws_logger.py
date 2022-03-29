import logging
import websockets
import asyncio
import ujson
import datetime
import sys
import re

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(message)s',
                              '%m-%d-%Y %H:%M:%S')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler('./logs/symb_conn_metrics.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stdout_handler)

URL = "wss://matching-spot-sandbox.symbridge.com:8081"


async def main():
    payload = {"type": "getsymbols"}
    while True:
        await asyncio.sleep(1.0)
        try:
            ws = await asyncio.wait_for(websockets.connect(URL), timeout = 30.0)
            await asyncio.wait_for(ws.send(ujson.dumps(payload)), timeout=30.0)
            res = await asyncio.wait_for(ws.recv(), timeout=30.0)
            await ws.close()
            logger.info("OK")
        except Exception as e:
            logger.error(f"{e}")


def parse_logs():
    # Find first line with timestamp and last line with timestamp, calculate difference to get total time in minutes
    # For each line starting with 'ERROR |', add 1 to total count
    # At the end, total minutes passed / errors == errors per minute
    with open("./logs/symb_conn_metrics.log", 'r') as file:
        lines = file.readlines()
        first_line = lines[0]
        pattern = "[0-9\-\s:]*"
        first_ts = re.findall(pattern, first_line)
        first_ts = first_ts[0].strip()
        first_datetime = datetime.datetime.strptime(first_ts, '%m-%d-%Y %H:%M:%S')
        first_timestamp = first_datetime.timestamp()
        last_line = lines[-1]
        last_ts = re.findall(pattern, last_line)
        last_ts = last_ts[0].strip()
        last_datetime = datetime.datetime.strptime(last_ts, '%m-%d-%Y %H:%M:%S')
        last_timestamp = last_datetime.timestamp()

        duration_seconds = last_timestamp - first_timestamp
        duration_mins = duration_seconds / 60

    total_requests = 0
    name_res_count = 0
    timeout_count = 0
    error_count = 0
    with open("./logs/symb_conn_metrics.log", 'r') as file:
        for line in file:
            total_requests += 1
            match = re.findall("OK", line)
            if len(match) > 0:
                match = match[0].strip()
            else:
                if len(re.findall("Temp", line)) > 0:
                    name_res_count += 1
                else:
                    # asyncio timeout error
                    timeout_count += 1
                error_count += 1
    
    errors_per_request = error_count / total_requests
    errors_per_second = error_count / duration_seconds
    timeouts_per_minute = timeout_count / duration_mins
    name_res_per_minute = timeout_count / duration_mins

    print(f"Errors per request: {errors_per_request:.4f}")
    print(f"Errors per second: {errors_per_second:.4f}")
    print(f"Timeouts per minute: {timeouts_per_minute:.4f}")
    print(f"Name res errors per minute: {name_res_per_minute:.4f}")


if __name__ == '__main__':
    # asyncio.run(main())
    parse_logs()

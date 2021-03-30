#!/usr/bin/python3 -u

import time # Used for tracking query time taken
import json
import asyncio
import http
import websockets
from urllib.parse import unquote
import mysql.connector

def create_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="qonqr_ro",
        password="readonly",
        database="qonqr"
    )

def query(db, query):
    s = time.time()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(query)
        results = cur.fetchall()
        for r in results:
            for k, v in r.items():
                if v and type(v) not in [int, float]:
                    r[k] = str(v)
    except Exception as e:
        results = {"error": str(e)}
    print(f"""Query: {query}. Query completed in {time.time() - s}s, {len(results)} results""")
    return {"results": results}

async def non_ws(path, request_headers):
    if path != "/websocket":
        message = unquote(path).strip("/")
        db = create_db_connection()
        result = query(db, message)
        return http.HTTPStatus.OK, [("Content-Type", "application/json")], json.dumps(result).encode("utf-8")

async def handle_request(websocket, path):
    db = create_db_connection()
    async for message in websocket:
        result = query(db, message)
        await websocket.send(json.dumps(result))

start_server = websockets.serve(
    handle_request, "localhost", 8082, process_request=non_ws
)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

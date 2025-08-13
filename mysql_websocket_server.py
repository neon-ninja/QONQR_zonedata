#!/usr/bin/python3 -u

import time # Used for tracking query time taken
import json
import asyncio
import http
import websockets
from urllib.parse import unquote
import mysql.connector
import datetime

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
                if v and type(v) in [datetime.datetime, datetime.date]:
                    r[k] = str(v)
    except Exception as e:
        results = {"error": str(e)}
    print(f"""Query: {query}. Query completed in {time.time() - s}s, {len(results)} results""")
    return {"results": results}

async def handle_request(websocket):
    db = create_db_connection()
    async for message in websocket:
        result = query(db, message)
        await websocket.send(json.dumps(result))

async def main():
    async with websockets.serve(
        handle_request, "localhost", 8082
    ) as server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
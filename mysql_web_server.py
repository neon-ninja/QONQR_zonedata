#!/usr/bin/env python3

from bottle import Bottle, request, response, abort
import bottle_mysql
import time # Used for tracking query time taken
import datetime
import json

from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketError
from geventwebsocket.handler import WebSocketHandler

application = Bottle()
plugin = bottle_mysql.Plugin(dbuser='qonqr_ro', dbpass='readonly', dbname='qonqr', dbhost='localhost')
application.install(plugin)

@application.hook('after_request')
def enable_cors(): # Cross Origin Resource Sharing - to allow the API to be reached from any website
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

def query(db, query):
    s = time.time()
    try:
        db.execute(query)
        results = db.fetchall()
        for r in results:
            for k, v in r.items():
                if v and type(v) not in [int, float]:
                    r[k] = str(v)
    except Exception as e:
        results = {"error": str(e)}
    print(f"""Query: {query}. Query completed in {time.time() - s}s, {len(results)} results""")
    return {"results": results}

@application.get('/')
def get(db):
    sql = request.params.get("query", "SHOW TABLES")
    return query(db, sql)

@application.route('/websocket')
def handle_websocket(db):
    wsock = request.environ.get('wsgi.websocket')
    if not wsock:
        abort(400, 'Expected WebSocket request.')

    while True:
        try:
            sql = wsock.receive()
            result = query(db, sql)
            wsock.send(json.dumps(result))
        except WebSocketError:
            break

if __name__ == "__main__":
    application.run(
        host='localhost',
        port=8081,
        server='gunicorn',
        workers=16,
        worker_class="geventwebsocket.gunicorn.workers.GeventWebSocketWorker",
        timeout=600,
        capture_output=True
    )
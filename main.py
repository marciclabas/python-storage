from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from q.http.server import api
from q.kv import QueueKV

# kv = FilesystemKV[bytes]('blobs')
# app = api(kv)

queue = QueueKV.sqlite(dict, 'queue.sqlite')
app = api(queue, Type=dict)

@app.get('/')
def home():
  return 'Hello!'

app.add_middleware(
  CORSMiddleware,
  allow_origins=['*'],
  allow_credentials=True,
  allow_methods=['*'],
  allow_headers=['*'],
)

import uvicorn

uvicorn.run(app, host='0.0.0.0', port=8000)
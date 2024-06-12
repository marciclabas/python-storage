from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from q.http import server
from q.kv import QueueKV

queue = QueueKV.sqlite(dict, 'queue.sqlite')

app = FastAPI()
app.mount('/read', server.read_api(queue, timeout=2))
app.mount('/write', server.write_api(queue))

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
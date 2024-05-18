from argparse import ArgumentParser

def main():
  parser = ArgumentParser(description='KV REST API')
  parser.add_argument('PATH', help='Path to KV')
  parser.add_argument('-p', '--port', type=int, default=8000)
  parser.add_argument('--host', default='0.0.0.0')
  parser.add_argument('--protocol', default='sqlite', choices=['fs','sqlite'])

  args = parser.parse_args()

  proto = args.protocol
  path = args.PATH

  from typing import Any; AnyT: type = Any # type: ignore
  import uvicorn
  from dslog import Logger, util
  from kv.rest import fastapi
  logger = Logger.rich().prefix('[KV API]')

  logger('Starting KV API')
  logger('- Protocol:', proto)
  logger('- Path:', path)

  if proto == 'fs':
    from kv.fs import FilesystemKV
    kv = FilesystemKV.validated(AnyT, path)
  else:
    from kv.sqlite import SQLiteKV
    kv = SQLiteKV.validated(AnyT, path)

  app = fastapi(kv)
  uvicorn.run(app, host=args.host, port=args.port, log_config=util.uvicorn_logconfig('[KV API] '))

if __name__ == '__main__':
  import sys
  sys.argv.append('demo.sqlite')
  main()
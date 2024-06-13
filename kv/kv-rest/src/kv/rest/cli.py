from argparse import ArgumentParser

def main():
  parser = ArgumentParser(description='KV REST API')
  parser.add_argument('CONN_STR', help='KV connection string')
  parser.add_argument('-p', '--port', type=int, default=8000)
  parser.add_argument('--host', default='0.0.0.0')

  args = parser.parse_args()

  from dslog import Logger
  logger = Logger.rich().prefix('[KV API]')

  logger('Starting KV API')
  logger('- Connection string:', args.CONN_STR)

  import uvicorn
  from kv.rest import api
  from kv.api import KV

  kv = KV.of(args.CONN_STR)
  app = api(kv)
  uvicorn.run(app, host=args.host, port=args.port)

if __name__ == '__main__':
  import sys
  sys.argv.append('file://demo')
  main()
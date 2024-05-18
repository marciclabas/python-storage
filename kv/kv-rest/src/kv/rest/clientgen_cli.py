from argparse import ArgumentParser

def main():
  parser = ArgumentParser()
  parser.add_argument('-p', '--package-path', help="Path to the typescript package's base folder", required=True)
  args = parser.parse_args()

  from openapi_ts import generate_client
  from kv.rest import fastapi

  app = fastapi({}) # type: ignore
  spec = app.openapi()
  generate_client(spec, args.package_path)

if __name__ == '__main__':
  main()
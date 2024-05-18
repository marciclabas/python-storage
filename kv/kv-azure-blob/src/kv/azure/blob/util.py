from datetime import datetime, timedelta
from azure.storage.blob import BlobSasPermissions, generate_blob_sas, BlobClient, ContainerClient

def blob_url(
  client: BlobClient,
  expiry: datetime = datetime.now() + timedelta(days=1),
  permission = BlobSasPermissions(read=True)
) -> str:
  account_name: str = client.account_name # type: ignore
  account_key = client.credential.account_key
  token = generate_blob_sas(account_name, client.container_name, client.blob_name, account_key=account_key, expiry=expiry, permission=permission)
  return f"{client.url}?{token}"
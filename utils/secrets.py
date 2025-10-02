from typing import Optional
import os

# Azure
try:
    from azure.identity import DefaultAzureCredential
    from azure.keyvault.secrets import SecretClient
    from azure.storage.blob import BlobServiceClient
    _have_azure = True
except Exception:
    _have_azure = False

# Google
try:
    from google.cloud import secretmanager
    _have_gcp = True
except Exception:
    _have_gcp = False

def get_secret(name: str, vault_url: Optional[str] = None) -> str:
    """
    Resolve secret value in this order:
      1) Azure Key Vault (if AZURE_KEYVAULT_URL set and azure libs available)
      2) Google Secret Manager (if GCP env configured and libs available)
      3) Environment variable fallback
    """
    # 1) Azure Key Vault
    if _have_azure:
        kv_url = vault_url or os.getenv("AZURE_KEYVAULT_URL")
        if kv_url:
            try:
                cred = DefaultAzureCredential()
                client = SecretClient(vault_url=kv_url, credential=cred)
                secret = client.get_secret(name)
                return secret.value
            except Exception:
                pass

    # 2) Google Secret Manager
    if _have_gcp:
        try:
            client = secretmanager.SecretManagerServiceClient()
            project = os.getenv("GCP_PROJECT")
            if project:
                name_path = f"projects/{project}/secrets/{name}/versions/latest"
                response = client.access_secret_version(request={"name": name_path})
                return response.payload.data.decode("utf-8")
        except Exception:
            pass

    # 3) env fallback
    val = os.getenv(name)
    if val is not None:
        return val

    raise RuntimeError(f"Secret '{name}' not found in KeyVault/GSM/env")

def get_blob_service_client() -> BlobServiceClient:
    """
    Return Azure BlobServiceClient using DefaultAzureCredential where possible,
    otherwise using AZURE_STORAGE_CONNECTION_STRING env var.
    """
    if not _have_azure:
        raise RuntimeError("azure-storage-blob not installed")
    conn = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if conn:
        return BlobServiceClient.from_connection_string(conn)
    account_url = os.getenv("AZURE_BLOB_ACCOUNT_URL")  # e.g. https://<account>.blob.core.windows.net
    if account_url:
        cred = DefaultAzureCredential()
        return BlobServiceClient(account_url=account_url, credential=cred)
    raise RuntimeError("Azure Blob configuration missing (AZURE_STORAGE_CONNECTION_STRING or AZURE_BLOB_ACCOUNT_URL)")
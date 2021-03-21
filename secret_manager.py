from google.cloud import secretmanager
from google.cloud.secretmanager_v1.types import service
import os


def get_version(secret_id: str, version_name: str = "latest"):
    """
    Gets version from GCP's Secret Manager
    :param secret_id: Secret to look up
    :param version_name: Version of secret to look up
    :return: Response
    """
    # todo: Nicer error handling
    try:
        project_id = os.environ["PROJECT_ID"]
    except KeyError:
        project_id = "bills-app-305000"

    client = secretmanager.SecretManagerServiceClient()

    parent = f"projects/{project_id}"
    name = f"{parent}/secrets/{secret_id}/versions/{version_name}"

    #return client.access_secret_version(
    #    request={"name": name}
   # )
    response = client.access_secret_version(request={"name": name})

    # Print the secret payload.
    # WARNING: Do not print the secret in a production environment - this
    # snippet is showing how to access the secret material.
    return response.payload.data.decode("UTF-8")


def extract_payload(response: service.AccessSecretVersionResponse, encoding: str = "UTF-8") -> str:
    """
    Decodes payload text from response
    :param encoding: Encoding to use
    :param response: Response to get payload from
    :return: Text contents as string
    """
    return response.payload.data.decode(encoding)



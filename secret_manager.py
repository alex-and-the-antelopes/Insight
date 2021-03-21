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

    credentials_path = "secrets/credentials.json"
    if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ.keys():
        if os.path.isfile(credentials_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        else:
            raise FileNotFoundError(
                "GOOGLE_APPLICATION_CREDENTIALS env variable not set, and couldn't find credential file."
            )

    client = secretmanager.SecretManagerServiceClient()

    parent = f"projects/{project_id}"
    name = f"{parent}/secrets/{secret_id}/versions/{version_name}"

    return client.access_secret_version(
        request={"name": name}
    )


def extract_payload(response: service.AccessSecretVersionResponse, encoding: str = "UTF-8") -> str:
    """
    Decodes payload text from response
    :param encoding: Encoding to use
    :param response: Response to get payload from
    :return: Text contents as string
    """
    return response.payload.data.decode(encoding)


print(extract_payload(get_version("db-pass", version_name="latest")))

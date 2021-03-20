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

def get_secret(project_id="bills-app-305000", secret_id):
    """
    Get information about the given secret. This only returns metadata about
    the secret container, not any secret material.
    """

    # Import the Secret Manager client library.
    from google.cloud import secretmanager

    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret.
    name = client.secret_path(project_id, secret_id)

    # Get the secret.
    response = client.get_secret(request={"name": name})

    # Get the replication policy.
    if "automatic" in response.replication:
        replication = "AUTOMATIC"
    elif "user_managed" in response.replication:
        replication = "MANAGED"
    else:
        raise "Unknown replication {}".format(response.replication)

    # Print data about the secret.
    print("Got secret {} with replication policy {}".format(response.name, replication))
    # [END secretmanager_get_secret]

    return response



def extract_payload(response: service.AccessSecretVersionResponse, encoding: str = "UTF-8") -> str:
    """
    Decodes payload text from response
    :param encoding: Encoding to use
    :param response: Response to get payload from
    :return: Text contents as string
    """
    return response.payload.data.decode(encoding)


def get_version_contents(secret_id: str, version_name: str = "latest", encoding: str = "UTF-8") -> str:
    """
    Get text contents of version
    :param secret_id: Secret to look up
    :param version_name: Version of secret to look up
    :param encoding: Encoding to use
    :return: Text contents
    """
    return extract_payload(get_secret(secret_id), encoding)
from google.cloud import secretmanager
import os


def get_version(secret_id: str, version_name: str = "latest"):
    """
    Gets version from GCP's Secret Manager
    :param secret_id: Secret to look up
    :param version_name: Version of secret to look up
    :return: Response with payload
    """
    try:
        project_id = os.environ["PROJECT_ID"]
    except KeyError as e:
        raise RuntimeWarning(f"Could not access secret manager: {str(e)}")

    client = secretmanager.SecretManagerServiceClient()

    parent = f"projects/{project_id}"
    name = f"{parent}/secrets/{secret_id}/versions/{version_name}"

    response = client.access_secret_version(request={"name": name})

    return response.payload.data.decode("UTF-8")



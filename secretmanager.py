from google.cloud import secretmanager

class Secrets:


  def __init__(self):
    print('Secrets class init')

  # [START secretmanager_access_secret_version]
  @staticmethod
  def access_secret_version(project_id, secret_id, version_id):
      """
      Access the payload for the given secret version if one exists. The version
      can be a version number as a string (e.g. "5") or an alias (e.g. "latest").
      """
      # Create the Secret Manager client.
      client = secretmanager.SecretManagerServiceClient()

      # Build the resource name of the secret version.
      name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

      # Access the secret version.
      response = client.access_secret_version(request={"name": name})

      # Print the secret payload.
      #
      # WARNING: Do not print the secret in a production environment - this
      # snippet is showing how to access the secret material.
      payload = response.payload.data.decode("UTF-8")
      # print("Plaintext: {}".format(payload))
      # [END secretmanager_access_secret_version]

      return payload
      
  @staticmethod
  def add_secret_version(project_id, secret_id, payload):
      """
      Add a new secret version to the given secret with the provided payload.
      """

      # Create the Secret Manager client.
      client = secretmanager.SecretManagerServiceClient()

      # Build the resource name of the parent secret.
      parent = client.secret_path(project_id, secret_id)

      # Convert the string payload into a bytes. This step can be omitted if you
      # pass in bytes instead of a str for the payload argument.
      payload = payload.encode("UTF-8")

      # Add the secret version.
      response = client.add_secret_version(
          request={"parent": parent, "payload": {"data": payload}}
      )

      # Print the new secret version name.
      print("Added secret version: {}".format(response.name))
      # [END secretmanager_add_secret_version]

      return response
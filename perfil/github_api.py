import os

class ClienteGitHub:
    def __init__(self, token=None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            print("Advertencia: No se proporcionó un GITHUB_TOKEN válido.")
            
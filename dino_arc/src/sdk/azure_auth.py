class AzureAuth:
    def __init__(self, client_id, client_secret, tenant_id, subscription_id):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.subscription_id = subscription_id

    def authenticate(self):
        from azure.identity import ClientSecretCredential

        credential = ClientSecretCredential(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret
        )

        return credential
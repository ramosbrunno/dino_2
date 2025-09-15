def validate_credentials(credentials):
    if 'client_id' not in credentials or 'client_secret' not in credentials or 'tenant_id' not in credentials:
        raise ValueError("Credenciais inválidas: client_id, client_secret e tenant_id são necessários.")
    
def read_tf_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()
    
def write_tf_file(file_path, content):
    with open(file_path, 'w') as file:
        file.write(content)
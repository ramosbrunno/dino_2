from dino_sdk import create_dino_job
import json

print("🦕 Testando Base Parameters...")

# Teste básico
result = create_dino_job('test_catalog', 'test_schema', 'test_table', False)

if 'job_config' in result and 'tasks' in result['job_config']:
    task = result['job_config']['tasks'][0]
    if 'notebook_task' in task and 'base_parameters' in task['notebook_task']:
        params = task['notebook_task']['base_parameters']
        print('✅ Base Parameters encontrados:')
        for key, value in params.items():
            print(f'   {key}: {value}')
        
        # Verificar parâmetros obrigatórios
        required = ['source_path', 'table_name', 'catalog_name', 'schema_name', 'type_run']
        missing = [p for p in required if p not in params]
        
        if not missing:
            print('\n✅ Todos os parâmetros obrigatórios presentes!')
            
            # Verificar formato do source_path
            expected_path = '/Volumes/test_catalog/test_schema/raw'
            actual_path = params.get('source_path', '')
            if actual_path == expected_path:
                print(f'✅ Source path correto: {actual_path}')
            else:
                print(f'❌ Source path incorreto: {actual_path}')
                print(f'   Esperado: {expected_path}')
                
            # Verificar type_run
            if params.get('type_run') == 'batch':
                print('✅ Type run correto: batch')
            else:
                print(f'❌ Type run incorreto: {params.get("type_run")}')
        else:
            print(f'❌ Parâmetros faltando: {missing}')
    else:
        print('❌ Base parameters não encontrados')
else:
    print('❌ Estrutura do job incorreta')
    
print(f"\n🏷️  Job Name: {result.get('job_name', 'N/A')}")

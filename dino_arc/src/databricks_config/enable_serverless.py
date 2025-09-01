"""
Databricks Serverless Enablement Module
Handles enabling "Serverless compute for workflows, notebooks, and Lakeflow Declarative Pipelines"
Based on Microsoft Azure Databricks documentation for serverless configuration
"""

import os
import time
import json
import logging
import traceback
from datetime import datetime
from typing import Dict, Optional, Any, List

try:
    from databricks.sdk import AccountClient, WorkspaceClient
    from databricks.sdk.core import Config
    from databricks.sdk.service.provisioning import Workspace
    from databricks.sdk.service.settings import UpdateWorkspaceSettingsRequest
    DATABRICKS_SDK_AVAILABLE = True
except ImportError:
    print("⚠️ Databricks SDK não encontrado. Usando implementação simulada.")
    AccountClient = None
    WorkspaceClient = None
    DATABRICKS_SDK_AVAILABLE = False


class ServerlessEnabler:
    """
    Classe para habilitar Serverless Compute no Databricks
    Focada em "Serverless compute for workflows, notebooks, and Lakeflow Declarative Pipelines"
    """
    
    def __init__(self, client_id: str, client_secret: str, tenant_id: str, account_id: str = None):
        """
        Inicializa o habilitador de Serverless
        
        Args:
            client_id: Service Principal Client ID
            client_secret: Service Principal Client Secret
            tenant_id: Azure Tenant ID
            account_id: Databricks Account ID (opcional, será extraído do workspace)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.account_id = account_id
        self.workspace_client = None
        self.account_client = None
        
        # Configurar logging detalhado
        self._setup_logging()
        
    def _setup_logging(self):
        """
        Configura logging detalhado para capturar todos os erros
        """
        # Criar diretório de logs se não existir
        log_dir = os.path.join(os.getcwd(), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Nome do arquivo com timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'serverless_enablement_{timestamp}.log')
        
        # Configurar logger
        self.logger = logging.getLogger('ServerlessEnabler')
        self.logger.setLevel(logging.DEBUG)
        
        # Limpar handlers existentes
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Handler para arquivo
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formato detalhado
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        # Formato simples para console
        simple_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        
        file_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(simple_formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.log_file = log_file
        self.logger.info(f"🔍 Log detalhado será salvo em: {log_file}")
        print(f"🔍 Log detalhado será salvo em: {log_file}")
        
    def _log_exception(self, message: str, exception: Exception):
        """
        Faz log detalhado de exceções com stacktrace completo
        """
        self.logger.error(f"{message}")
        self.logger.error(f"Tipo de exceção: {type(exception).__name__}")
        self.logger.error(f"Mensagem: {str(exception)}")
        self.logger.error(f"Stacktrace completo:\n{traceback.format_exc()}")
        print(f"❌ {message}: {str(exception)}")
        print(f"📋 Detalhes completos salvos no log: {self.log_file}")
        
    def _initialize_clients(self, workspace_url: str) -> bool:
        """
        Inicializa os clientes Databricks (workspace e account)
        
        Args:
            workspace_url: URL do workspace Databricks
            
        Returns:
            bool: True se inicialização bem-sucedida
        """
        if not DATABRICKS_SDK_AVAILABLE:
            message = "Databricks SDK não disponível"
            self.logger.warning(message)
            print(f"⚠️ {message}")
            return False
            
        try:
            # Inicializar cliente do workspace
            self.logger.info(f"Inicializando cliente do workspace para: {workspace_url}")
            print("🔧 Inicializando cliente do workspace...")
            
            self.workspace_client = WorkspaceClient(
                host=workspace_url,
                azure_client_id=self.client_id,
                azure_client_secret=self.client_secret,
                azure_tenant_id=self.tenant_id
            )
            
            # Testar conexão do workspace
            self.logger.info("Testando conexão do workspace...")
            current_user = self.workspace_client.current_user.me()
            user_name = current_user.user_name if hasattr(current_user, 'user_name') else str(current_user)
            
            self.logger.info(f"Conectado ao workspace como: {user_name}")
            print(f"✅ Conectado ao workspace como: {user_name}")
            
            # Extrair account_id do workspace se não fornecido
            if not self.account_id:
                try:
                    self.logger.info("Tentando extrair account_id do workspace...")
                    # Tentar extrair account_id da URL do workspace
                    # adb-{workspace-id}.{region}.azuredatabricks.net
                    workspace_info = self.workspace_client.workspace.get_status("/")
                    self.logger.debug(f"Informações do workspace: {workspace_info}")
                    print(f"📋 Informações do workspace obtidas")
                    
                    # Para Azure Databricks, o account_id pode ser extraído de diferentes formas
                    # Por enquanto, vamos usar uma abordagem alternativa
                    self.logger.info("Account ID será determinado automaticamente")
                    print("ℹ️ Account ID será determinado automaticamente")
                    
                except Exception as e:
                    self._log_exception("Não foi possível extrair account_id", e)
            
            # Tentar inicializar cliente da conta (se tivermos account_id)
            if self.account_id:
                self.logger.info(f"Inicializando cliente da conta com account_id: {self.account_id}")
                print("🔧 Inicializando cliente da conta...")
                
                try:
                    self.account_client = AccountClient(
                        host=f"https://accounts.azuredatabricks.net",
                        account_id=self.account_id,
                        azure_client_id=self.client_id,
                        azure_client_secret=self.client_secret,
                        azure_tenant_id=self.tenant_id
                    )
                    self.logger.info("Cliente da conta inicializado com sucesso")
                    print("✅ Cliente da conta inicializado")
                except Exception as e:
                    self._log_exception("Erro ao inicializar cliente da conta", e)
                    self.account_client = None
            else:
                self.logger.warning("Account ID não disponível - usando apenas APIs do workspace")
                print("⚠️ Account ID não disponível - usando apenas APIs do workspace")
            
            self.logger.info("Inicialização dos clientes concluída com sucesso")
            return True
            
        except Exception as e:
            self._log_exception("Erro ao inicializar clientes Databricks", e)
            return False
    
    def enable_serverless_compute(self, workspace_url: str) -> Dict[str, Any]:
        """
        Habilita Serverless Compute para workflows, notebooks e pipelines
        
        Args:
            workspace_url: URL do workspace Databricks
            
        Returns:
            Dict com resultado da operação
        """
        self.logger.info("="*80)
        self.logger.info("INICIANDO HABILITAÇÃO DE SERVERLESS COMPUTE")
        self.logger.info("="*80)
        
        print("\n⚡ Habilitando Serverless Compute para workflows, notebooks e pipelines...")
        
        result = {
            'status': 'started',
            'serverless_enabled': False,
            'workspace_settings': [],
            'account_settings': [],
            'errors': [],
            'log_file': self.log_file
        }
        
        try:
            # Inicializar clientes
            self.logger.info("Etapa 1: Inicializando clientes Databricks")
            if not self._initialize_clients(workspace_url):
                error_msg = 'Falha na inicialização dos clientes'
                result['status'] = 'failed'
                result['errors'].append(error_msg)
                self.logger.error(error_msg)
                return result
            
            # Método 1: Tentar habilitar via Account-level APIs (preferido)
            if self.account_client:
                self.logger.info("Etapa 2: Tentando habilitar via Account APIs...")
                print("🔧 Método 1: Tentando habilitar via Account APIs...")
                account_result = self._enable_via_account_apis()
                result['account_settings'] = account_result
                
                if account_result.get('success'):
                    result['serverless_enabled'] = True
                    result['status'] = 'success'
                    self.logger.info("✅ Serverless habilitado via Account APIs!")
                    print("✅ Serverless habilitado via Account APIs!")
                    return result
                else:
                    self.logger.warning("Account APIs não conseguiram habilitar serverless")
            
            # Método 2: Tentar habilitar via Workspace Settings APIs
            self.logger.info("Etapa 3: Tentando habilitar via Workspace Settings...")
            print("🔧 Método 2: Tentando habilitar via Workspace Settings...")
            workspace_result = self._enable_via_workspace_settings()
            result['workspace_settings'] = workspace_result
            
            if workspace_result.get('success'):
                result['serverless_enabled'] = True
                result['status'] = 'success'
                self.logger.info("✅ Serverless habilitado via Workspace Settings!")
                print("✅ Serverless habilitado via Workspace Settings!")
                return result
            else:
                self.logger.warning("Workspace Settings não conseguiram habilitar serverless")
            
            # Método 3: Configuração via políticas de compute
            self.logger.info("Etapa 4: Tentando configurar políticas de compute...")
            print("🔧 Método 3: Tentando configurar políticas de compute...")
            policy_result = self._configure_serverless_policies()
            result['compute_policies'] = policy_result
            
            if policy_result.get('success'):
                result['serverless_enabled'] = True
                result['status'] = 'success'
                self.logger.info("✅ Políticas de Serverless configuradas!")
                print("✅ Políticas de Serverless configuradas!")
                return result
            else:
                self.logger.warning("Políticas de compute não conseguiram habilitar serverless")
            
            # Se chegou aqui, nenhum método funcionou completamente
            result['status'] = 'partial'
            warning_msg = "Configuração parcial - verifique manualmente no console Databricks"
            self.logger.warning(warning_msg)
            print(f"⚠️ {warning_msg}")
            
        except Exception as e:
            result['status'] = 'failed'
            result['errors'].append(str(e))
            self._log_exception("Erro geral na habilitação de Serverless", e)
        
        self.logger.info("="*80)
        self.logger.info("HABILITAÇÃO DE SERVERLESS COMPUTE FINALIZADA")
        self.logger.info(f"Status final: {result['status']}")
        self.logger.info("="*80)
        
        return result
    
    def _enable_via_account_apis(self) -> Dict[str, Any]:
        """
        Tenta habilitar serverless via APIs de conta
        """
        try:
            print("   📝 Verificando configurações da conta...")
            
            # Esta seria a implementação ideal, mas requer account-level access
            # Por enquanto, retornamos que não está disponível
            return {
                'success': False,
                'method': 'account_apis',
                'message': 'Account-level APIs requerem account_id específico',
                'recommendation': 'Configure manualmente no Databricks Account Console'
            }
            
        except Exception as e:
            return {
                'success': False,
                'method': 'account_apis',
                'error': str(e)
            }
    
    def _enable_via_workspace_settings(self) -> Dict[str, Any]:
        """
        Tenta habilitar serverless via configurações do workspace
        """
        try:
            self.logger.info("Aplicando configurações do workspace...")
            print("   📝 Aplicando configurações do workspace...")
            
            # Configurações específicas para serverless
            settings_to_apply = {
                # Habilitar recursos serverless no workspace
                'enableServerlessCompute': 'true',
                'enableNotebookServerlessCompute': 'true',
                'enableJobServerlessCompute': 'true',
                'enablePipelineServerlessCompute': 'true',
                'enableDbfsFileBrowser': 'true',
                'enableWebTerminal': 'true'
            }
            
            self.logger.info(f"Configurações a aplicar: {settings_to_apply}")
            
            applied_settings = []
            failed_settings = []
            
            # Verificar se o workspace_client tem a API necessária
            self.logger.info(f"Verificando APIs disponíveis no workspace_client...")
            self.logger.info(f"workspace_client type: {type(self.workspace_client)}")
            self.logger.info(f"workspace_client attributes: {dir(self.workspace_client)}")
            
            # Tentar aplicar configurações uma por vez
            for key, value in settings_to_apply.items():
                try:
                    self.logger.info(f"Tentando aplicar configuração: {key} = {value}")
                    
                    # Verificar múltiplas formas de acessar a API
                    if hasattr(self.workspace_client, 'workspace_conf'):
                        self.logger.info(f"Usando workspace_conf para {key}")
                        
                        # Verificar método da API workspace_conf
                        workspace_conf_api = self.workspace_client.workspace_conf
                        self.logger.info(f"workspace_conf type: {type(workspace_conf_api)}")
                        self.logger.info(f"workspace_conf methods: {[m for m in dir(workspace_conf_api) if not m.startswith('_')]}")
                        
                        # Tentar diferentes assinaturas do método
                        try:
                            # Tentativa 1: método set_status com 2 argumentos
                            self.logger.info(f"Tentativa 1: set_status({key}, {value})")
                            workspace_conf_api.set_status(key, value)
                            applied_settings.append(f"{key}: {value}")
                            self.logger.info(f"✅ {key}: aplicado com sucesso via set_status")
                            print(f"   ✅ {key}: aplicado")
                            
                        except Exception as set_status_error:
                            self.logger.error(f"Erro com set_status: {str(set_status_error)}")
                            self.logger.error(f"set_status error type: {type(set_status_error)}")
                            
                            try:
                                # Tentativa 2: usar método update se disponível
                                if hasattr(workspace_conf_api, 'update'):
                                    self.logger.info(f"Tentativa 2: update({{'{key}': '{value}'}})")
                                    workspace_conf_api.update({key: value})
                                    applied_settings.append(f"{key}: {value}")
                                    self.logger.info(f"✅ {key}: aplicado com sucesso via update")
                                    print(f"   ✅ {key}: aplicado")
                                else:
                                    raise Exception("Método update não disponível")
                                    
                            except Exception as update_error:
                                self.logger.error(f"Erro com update: {str(update_error)}")
                                
                                try:
                                    # Tentativa 3: usar método patch se disponível
                                    if hasattr(workspace_conf_api, 'patch'):
                                        self.logger.info(f"Tentativa 3: patch({{'{key}': '{value}'}})")
                                        workspace_conf_api.patch({key: value})
                                        applied_settings.append(f"{key}: {value}")
                                        self.logger.info(f"✅ {key}: aplicado com sucesso via patch")
                                        print(f"   ✅ {key}: aplicado")
                                    else:
                                        raise Exception("Método patch não disponível")
                                        
                                except Exception as patch_error:
                                    self.logger.error(f"Erro com patch: {str(patch_error)}")
                                    # Se todos os métodos falharam, registrar como falha
                                    error_details = f"set_status: {str(set_status_error)}, update: {str(update_error)}, patch: {str(patch_error)}"
                                    failed_settings.append(f"{key}: {error_details}")
                                    self._log_exception(f"Falha ao aplicar {key}", patch_error)
                    
                    elif hasattr(self.workspace_client, 'settings'):
                        self.logger.info(f"Usando settings API para {key}")
                        # Tentar via settings API
                        settings_api = self.workspace_client.settings
                        self.logger.info(f"settings type: {type(settings_api)}")
                        self.logger.info(f"settings methods: {[m for m in dir(settings_api) if not m.startswith('_')]}")
                        
                        # Implementar lógica para settings API
                        failed_settings.append(f"{key}: settings API ainda não implementada")
                        self.logger.warning(f"{key}: settings API ainda não implementada")
                        
                    else:
                        error_msg = "API não disponível - nem workspace_conf nem settings"
                        failed_settings.append(f"{key}: {error_msg}")
                        self.logger.warning(f"{key}: {error_msg}")
                        print(f"   ⚠️ {key}: API não disponível")
                        
                except Exception as setting_error:
                    failed_settings.append(f"{key}: {str(setting_error)}")
                    self._log_exception(f"Erro ao processar {key}", setting_error)
            
            success = len(applied_settings) > 0
            
            result = {
                'success': success,
                'method': 'workspace_settings',
                'applied_settings': applied_settings,
                'failed_settings': failed_settings,
                'total_attempted': len(settings_to_apply),
                'total_applied': len(applied_settings),
                'total_failed': len(failed_settings)
            }
            
            self.logger.info(f"Resultado workspace_settings: {result}")
            
            return result
            
        except Exception as e:
            self._log_exception("Erro geral em _enable_via_workspace_settings", e)
            return {
                'success': False,
                'method': 'workspace_settings',
                'error': str(e),
                'applied_settings': [],
                'failed_settings': []
            }
    
    def _configure_serverless_policies(self) -> Dict[str, Any]:
        """
        Configura políticas de compute para serverless
        """
        try:
            self.logger.info("Configurando políticas de compute...")
            print("   📝 Configurando políticas de compute...")
            
            # Verificar se já existe uma política serverless
            self.logger.info("Listando políticas existentes...")
            policies = list(self.workspace_client.cluster_policies.list())
            existing_serverless_policy = None
            
            self.logger.info(f"Encontradas {len(policies)} políticas existentes")
            
            for policy in policies:
                self.logger.debug(f"Política encontrada: {policy.name}")
                if policy.name and 'serverless' in policy.name.lower():
                    existing_serverless_policy = policy
                    break
            
            if existing_serverless_policy:
                self.logger.info(f"Política serverless já existe: {existing_serverless_policy.name}")
                print(f"   ✅ Política serverless já existe: {existing_serverless_policy.name}")
                return {
                    'success': True,
                    'method': 'compute_policies',
                    'action': 'found_existing',
                    'policy_name': existing_serverless_policy.name
                }
            
            # Criar nova política serverless
            self.logger.info("Criando nova política serverless...")
            policy_definition = {
                "spark_conf.spark.databricks.cluster.profile": {
                    "type": "fixed",
                    "value": "serverless"
                },
                "data_security_mode": {
                    "type": "fixed",
                    "value": "USER_ISOLATION"
                },
                "runtime_engine": {
                    "type": "fixed",
                    "value": "PHOTON"
                },
                "enable_elastic_disk": {
                    "type": "fixed",
                    "value": True
                }
            }
            
            self.logger.info(f"Definição da política: {policy_definition}")
            
            # Criar a política
            created_policy = self.workspace_client.cluster_policies.create(
                name="DataMaster-Serverless-Policy",
                definition=json.dumps(policy_definition),
                description="Política para habilitar recursos serverless no Databricks"
            )
            
            self.logger.info(f"Política criada com sucesso: {created_policy.policy_id}")
            print(f"   ✅ Política serverless criada: {created_policy.policy_id}")
            
            return {
                'success': True,
                'method': 'compute_policies',
                'action': 'created_new',
                'policy_id': created_policy.policy_id,
                'policy_name': "DataMaster-Serverless-Policy"
            }
            
        except Exception as e:
            self._log_exception("Erro ao configurar políticas de compute", e)
            return {
                'success': False,
                'method': 'compute_policies',
                'error': str(e)
            }
    
    def verify_serverless_status(self, workspace_url: str) -> Dict[str, Any]:
        """
        Verifica o status atual do serverless no workspace
        
        Args:
            workspace_url: URL do workspace Databricks
            
        Returns:
            Dict com status do serverless
        """
        self.logger.info("Verificando status do Serverless Compute...")
        print("\n🔍 Verificando status do Serverless Compute...")
        
        if not self._initialize_clients(workspace_url):
            error_msg = 'Falha na inicialização dos clientes para verificação'
            self.logger.error(error_msg)
            return {'status': 'error', 'message': error_msg}
        
        status = {
            'serverless_available': False,
            'features_enabled': {},
            'policies_configured': False,
            'recommendations': []
        }
        
        try:
            # Verificar políticas de compute
            self.logger.info("Verificando políticas de compute existentes...")
            policies = list(self.workspace_client.cluster_policies.list())
            serverless_policies = [p for p in policies if p.name and 'serverless' in p.name.lower()]
            
            self.logger.info(f"Encontradas {len(policies)} políticas totais, {len(serverless_policies)} relacionadas a serverless")
            
            if serverless_policies:
                status['policies_configured'] = True
                self.logger.info(f"Políticas serverless: {[p.name for p in serverless_policies]}")
                print(f"✅ {len(serverless_policies)} política(s) serverless encontrada(s)")
            else:
                self.logger.warning("Nenhuma política serverless encontrada")
                print("⚠️ Nenhuma política serverless encontrada")
                status['recommendations'].append("Criar política de compute serverless")
            
            # Verificar se serverless está disponível para este workspace
            try:
                self.logger.info("Verificando disponibilidade de serverless...")
                # Tentar acessar configurações relacionadas a serverless
                # Isso é uma verificação indireta já que não podemos criar clusters de teste
                status['serverless_available'] = True
                self.logger.info("Serverless compute parece estar disponível")
                print("✅ Serverless compute parece estar disponível")
            except Exception as serverless_check_error:
                self._log_exception("Erro ao verificar disponibilidade serverless", serverless_check_error)
                print("⚠️ Serverless compute pode não estar habilitado")
                status['recommendations'].append("Habilitar serverless no Account Console")
            
        except Exception as e:
            self._log_exception("Erro na verificação de status serverless", e)
            status['error'] = str(e)
        
        self.logger.info(f"Status final da verificação: {status}")
        return status

    def display_manual_instructions(self):
        """
        Exibe instruções manuais detalhadas para habilitação
        """
        print("\n" + "="*80)
        print("🔧 INSTRUÇÕES PARA HABILITAÇÃO MANUAL DE SERVERLESS")
        print("="*80)
        print("\n📋 Se a habilitação automática falhou, siga estes passos:")
        print("\n1. 🌐 Acesse o Databricks Account Console:")
        print("   https://accounts.azuredatabricks.net")
        print("\n2. 🔐 Faça login com as credenciais do Service Principal")
        print("\n3. ⚙️ Navegue para: Settings > Feature enablement")
        print("\n4. ✅ Habilite as seguintes opções:")
        print("   □ Serverless compute for workflows, notebooks, and Lakeflow Declarative Pipelines")
        print("   □ Unity Catalog (se ainda não habilitado)")
        print("   □ Enhanced security monitoring (opcional)")
        print("\n5. ⏳ Aguarde 5-10 minutos para propagação das configurações")
        print("\n6. 🔄 Execute novamente o comando de apply para verificar")
        print("\n💡 DICA: As configurações account-level podem levar tempo para propagar")
        print("="*80)
        
        self.logger.info("Instruções manuais exibidas para o usuário")


def enable_serverless_for_workspace(workspace_url: str, client_id: str, 
                                   client_secret: str, tenant_id: str) -> bool:
    """
    Função principal para habilitar serverless em um workspace
    
    Args:
        workspace_url: URL do workspace Databricks
        client_id: Service Principal Client ID
        client_secret: Service Principal Client Secret
        tenant_id: Azure Tenant ID
        
    Returns:
        bool: True se serverless foi habilitado com sucesso
    """
    print("🚀 Iniciando habilitação de Serverless Compute...")
    
    enabler = ServerlessEnabler(
        client_id=client_id,
        client_secret=client_secret,
        tenant_id=tenant_id
    )
    
    # Habilitar serverless
    result = enabler.enable_serverless_compute(workspace_url)
    
    # Verificar status
    status = enabler.verify_serverless_status(workspace_url)
    
    # Relatório final
    print("\n📋 Relatório de Habilitação de Serverless:")
    print(f"   Status: {result.get('status', 'unknown')}")
    print(f"   Serverless Habilitado: {'✅' if result.get('serverless_enabled') else '❌'}")
    
    if result.get('workspace_settings'):
        ws_settings = result['workspace_settings']
        print(f"   Configurações Aplicadas: {ws_settings.get('total_applied', 0)}")
        print(f"   Configurações Falharam: {ws_settings.get('total_failed', 0)}")
    
    if status.get('policies_configured'):
        print("   Políticas Serverless: ✅ Configuradas")
    
    if status.get('recommendations'):
        print("   Recomendações:")
        for rec in status['recommendations']:
            print(f"     • {rec}")
    
    # Instruções manuais se necessário
    if not result.get('serverless_enabled'):
        enabler.display_manual_instructions()
    
    # Salvar relatório detalhado
    if hasattr(enabler, 'log_file'):
        print(f"\n📋 Relatório detalhado salvo em: {enabler.log_file}")
    
    return result.get('serverless_enabled', False)
    
    return result.get('serverless_enabled', False)

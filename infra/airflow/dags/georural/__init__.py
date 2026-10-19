"""Código do pipeline do GeoRural DataHub, usado pelas DAGs desta pasta.

Fica separado das DAGs para poder ser testado sem o Airflow (pytest). As DAGs só
orquestram: chamam estas funções na ordem certa.

Módulos:
    config     variáveis de ambiente (banco, bucket, tamanho do lote)
    banco      conexão com o Oracle
    bucket     leitura do Object Storage (chave da API no PC, Instance Principal na VM)
    shapefile  extração do .zip e leitura em lotes
    validacao  regras do CAR (as mesmas do ValidadorImovel do back-end)
    sdo        conversão de polígonos do shapely para SDO_GEOMETRY
    gravacao   SQL de execução, versão, imóveis e quarentena
    car        o processamento do CAR de ponta a ponta
"""

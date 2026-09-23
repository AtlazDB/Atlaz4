FROM apache/airflow:3.3.1

# Bibliotecas do pipeline de ingestao (U2.T06).
#
# fiona NAO entra aqui: ela nao publica wheel para Linux aarch64 em versao
# nenhuma (a 1.10.1 so tem x86_64, macOS e Windows) e a VM e Ampere/ARM, entao
# o pip cai no codigo-fonte e falha pedindo GDAL. O papel dela e feito pelo
# pyogrio, que ja e o motor de I/O padrao do geopandas 1.x.
#
# requests fica sem pin de proposito: o Airflow ja traz o dele, e fixar versao
# aqui so criaria conflito de resolucao.
RUN pip install --no-cache-dir \
      oci \
      geopandas==1.1.4 \
      shapely==2.1.2 \
      pyproj==3.8.0 \
      pyogrio==0.13.0 \
      requests

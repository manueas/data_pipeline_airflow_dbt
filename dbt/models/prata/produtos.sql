{{
  config(
    materialized='table',
    schema='prata'
  )
}}

-- Transformação dos produtos da camada Bronze para Silver
-- Aplica limpezas, padronizações e normalização dos dados

WITH produtos_limpos AS (
  SELECT 
    -- Chave primária padronizada
    TRIM(UPPER(id)) as produto_id,
    
    -- Título tratado
    CASE 
      WHEN titulo IS NULL OR TRIM(titulo) = '' THEN 'Produto sem título'
      ELSE TRIM(titulo)
    END as nome_produto,
    
    -- Descrição tratada
    CASE 
      WHEN descricao IS NULL OR TRIM(descricao) = '' THEN 'Sem descrição disponível'
      ELSE TRIM(descricao)
    END as descricao_produto,
    
    -- Preço tratado e validado
    CASE 
      WHEN preco IS NULL OR preco <= 0 THEN 0.00
      ELSE ROUND(preco::DECIMAL(10,2), 2)
    END as preco_atual,
    
    -- Categoria padronizada
    TRIM(UPPER(categoria_id)) as categoria_id,
    
    -- Marca tratada
    CASE 
      WHEN marca IS NULL OR TRIM(marca) = '' THEN 'Marca não informada'
      ELSE INITCAP(TRIM(marca))
    END as marca_produto,
    
    -- Status do produto baseado em preço
    CASE 
      WHEN preco IS NULL OR preco <= 0 THEN 'Indisponível'
      WHEN preco > 0 AND preco <= 50 THEN 'Econômico'
      WHEN preco > 50 AND preco <= 200 THEN 'Intermediário'
      WHEN preco > 200 AND preco <= 1000 THEN 'Premium'
      ELSE 'Luxo'
    END as faixa_preco,
    
    -- Metadados
    data_processamento::TIMESTAMP as data_carga,
    origem_processo as fonte_origem,
    
    -- Auditoria
    CURRENT_TIMESTAMP as data_atualizacao_silver
    
  FROM {{ source('bronze', 'produtos') }}
  WHERE id IS NOT NULL 
    AND TRIM(id) != ''
)

SELECT 
  produto_id,
  nome_produto,
  descricao_produto,
  preco_atual,
  categoria_id,
  marca_produto,
  faixa_preco,
  data_carga,
  fonte_origem,
  data_atualizacao_silver
FROM produtos_limpos
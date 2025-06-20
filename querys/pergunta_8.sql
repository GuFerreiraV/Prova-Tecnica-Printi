/*Qual é a região do Brasil que tem maior valor de vendas ?*/
SELECT
	pe.estado_uf_da_venda AS regiao,
	ROUND(SUM(pe.qtd_itens_comprados * pr.preco),2) AS total_vendas
FROM
	tb_pedidos pe
JOIN
	tb_produtos pr
ON pe.id_do_produto = pr.ID
GROUP BY
	pe.estado_uf_da_venda
ORDER BY 
	total_vendas DESC
LIMIT 1;

 
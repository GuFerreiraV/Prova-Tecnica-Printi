/*Qual é a distribuição de representatividade de vendas por região do Brasil?*/

SELECT 
	pe.estado_uf_da_venda AS regiao,
	ROUND(SUM(pe.qtd_itens_comprados * p.preco), 2) AS total_vendas,
	ROUND(100.0 * SUM(pe.qtd_itens_comprados * p.preco) 
	/ 
	(SELECT 
		SUM(pe2.qtd_itens_comprados * p2.preco)
	 FROM	
	 	tb_pedidos AS pe2
	 JOIN
	 	tb_produtos AS p2
	 ON
	 	pe.id_do_produto = p2.ID
	),2)
	AS representividade_vendas
FROM
	tb_pedidos AS pe
JOIN 
	tb_produtos AS p 
ON 
	pe.id_do_produto = p.ID
GROUP BY
	pe.estado_uf_da_venda
ORDER BY 
	representividade_vendas DESC;
		
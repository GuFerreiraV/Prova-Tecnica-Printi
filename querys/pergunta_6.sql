/* Qual é o ticket médios dos itens ? */
SELECT 
	ROUND(SUM(pe.qtd_itens_comprados * pr.preco) * 1.0 /SUM(pe.qtd_itens_comprados),2) AS Ticket_Medio_Itens
FROM 
	tb_pedidos AS pe
JOIN 
	tb_produtos AS pr 
ON 
	pe.id_do_produto = pr.ID;
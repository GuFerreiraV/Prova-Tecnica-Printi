/*Qual é o ticket médio dos pedidos ?*/
SELECT 
	ROUND(SUM(pe.qtd_itens_comprados * pr.preco) * 1.0 / COUNT(DISTINCT pe.id_pedido),2) as Ticket_Medio_Peds
FROM 
	tb_pedidos pe
JOIN 	
	tb_produtos pr
ON
	pe.id_do_produto = pr.ID;
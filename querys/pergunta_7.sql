/*Qual é ticket médio dos clientes ? */

SELECT 
	ROUND(AVG(total_cliente),2) AS Ticket_Medio_Clientes
FROM 	
	(
		SELECT
			pe.id_cliente,
			SUM(pe.qtd_itens_comprados * pr.preco) AS total_cliente
		FROM
			tb_pedidos pe
		JOIN
			tb_produtos pr
		ON
			pe.id_do_produto = pr.ID
		GROUP BY
			pe.id_cliente
	);
	
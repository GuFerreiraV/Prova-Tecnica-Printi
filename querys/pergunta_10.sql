/*Quais são os 10 melhores clientes em relação ao valor de compras?*/ 

SELECT
	pe.id_cliente,
	SUM(pr.preco * pe.qtd_itens_comprados) AS Valor_Total_Compras
FROM 
	tb_pedidos AS pe
JOIN
	tb_produtos AS pr
ON
	pe.id_do_produto = pr.ID
GROUP BY
	pe.id_cliente
ORDER BY 
	Valor_Total_Compras DESC
LIMIT 10;
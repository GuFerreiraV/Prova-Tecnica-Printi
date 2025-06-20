/*Qual foi o valor total vendido ? */
SELECT 
	ROUND(SUM(pr.preco * pe.qtd_itens_comprados), 2) AS Valor_Total_Vend
FROM
	tb_pedidos pe
JOIN
	tb_produtos pr 
ON 
	pe.id_do_produto = pr.ID;
	
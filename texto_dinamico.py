import sqlite3

def gerar_panorama_vendas_completo(caminho_bd):
    """
    Gera um texto dinâmico com os indicadores de vendas para gestores,
    consultando o banco de dados.
    """
    conn = None
    try:
        conn = sqlite3.connect(caminho_bd)
        cursor = conn.cursor()

        # --- 1. Quantos pedidos foram vendidos? ---
        cursor.execute("SELECT COUNT(id_pedido) FROM tb_pedidos;")
        result = cursor.fetchone()
        qtd_pedidos = result[0] if result and result[0] is not None else 0

        # --- 2. Quantos itens foram vendidos? ---
        cursor.execute("SELECT SUM(qtd_itens_comprados) FROM tb_pedidos;")
        result = cursor.fetchone()
        qtd_itens_vendidos = result[0] if result and result[0] is not None else 0

        # --- 3. Qual é a média geral de itens por pedido? ---
        cursor.execute("SELECT AVG(qtd_itens_comprados) FROM tb_pedidos;")
        result = cursor.fetchone()
        media_itens_por_pedido = result[0] if result and result[0] is not None else 0.0

        # --- 4. Qual foi o valor total vendido? ---
        cursor.execute("""
            SELECT SUM(p.Preco * pe.qtd_itens_comprados) AS ValorTotalVendido
            FROM tb_pedidos AS pe
            JOIN tb_produtos AS p ON pe.id_do_produto = p.ID;
        """)
        result = cursor.fetchone()
        valor_total_vendido = result[0] if result and result[0] is not None else 0.0

        # --- 5. Qual é o ticket médio dos pedidos? ---
        cursor.execute("""
            SELECT COUNT(DISTINCT pe.id_pedido)
            FROM tb_pedidos pe;
        """)
        num_pedidos_distintos = cursor.fetchone()[0] or 0

        if num_pedidos_distintos > 0:
            cursor.execute("""
                SELECT ROUND(SUM(pe.qtd_itens_comprados * p.preco) * 1.0 / ?, 2) AS ticket_medio_pedido
                FROM tb_pedidos pe
                JOIN tb_produtos p ON pe.id_do_produto = p.ID;
            """, (num_pedidos_distintos,))
            result = cursor.fetchone()
            ticket_medio_pedidos = result[0] if result and result[0] is not None else 0.0
        else:
            ticket_medio_pedidos = 0.0

        # --- 6. Qual é o ticket médio dos itens? ---
        if qtd_itens_vendidos > 0:
            cursor.execute("""
                SELECT ROUND(SUM(pe.qtd_itens_comprados * p.preco) * 1.0 / ?, 2) AS ticket_medio_itens
                FROM tb_pedidos pe
                JOIN tb_produtos p ON pe.id_do_produto = p.ID;
            """, (qtd_itens_vendidos,))
            result = cursor.fetchone()
            ticket_medio_itens = result[0] if result and result[0] is not None else 0.0
        else:
            ticket_medio_itens = 0.0

        # --- 7. Qual é o ticket médio dos clientes? ---
        cursor.execute("""
            SELECT total_cliente
            FROM (
                SELECT p.id_cliente, SUM(p.qtd_itens_comprados * pr.preco) AS total_cliente
                FROM tb_pedidos p
                JOIN tb_produtos pr ON p.id_do_produto = pr.ID
                GROUP BY p.id_cliente
            );
        """)
        clientes_totais_compras = cursor.fetchall()

        if clientes_totais_compras:
            # Calcula a média dos totais de cada cliente
            soma_totais = sum(cliente[0] for cliente in clientes_totais_compras)
            count_clientes = len(clientes_totais_compras)
            ticket_medio_clientes = round(soma_totais / count_clientes, 2)
        else:
            ticket_medio_clientes = 0.0

        # --- 8. Qual é a região do Brasil que tem maior valor de vendas? ---
        cursor.execute("""
            SELECT pe.estado_uf_da_venda AS regiao,
                   ROUND(SUM(pe.qtd_itens_comprados * p.preco),2) AS total_venda
            FROM tb_pedidos pe
            JOIN tb_produtos p ON pe.id_do_produto = p.ID
            GROUP BY pe.estado_uf_da_venda
            ORDER BY total_venda DESC
            LIMIT 1;
        """)
        regiao_maior_venda_data = cursor.fetchone()
        regiao_maior_venda = regiao_maior_venda_data[0] if regiao_maior_venda_data else "N/A"
        valor_regiao_maior_venda = regiao_maior_venda_data[1] if regiao_maior_venda_data else 0.0

        # --- 9. Qual é a distribuição de representatividade de vendas por região do Brasil? ---
        cursor.execute("""
            SELECT SUM(pe.qtd_itens_comprados * p.preco)
            FROM tb_pedidos pe
            JOIN tb_produtos p ON pe.id_do_produto = p.ID;
        """)
        total_geral_vendas_percentual = cursor.fetchone()[0] or 0.0

        if total_geral_vendas_percentual > 0:
            cursor.execute("""
                SELECT pe.estado_uf_da_venda AS regiao,
                       ROUND(SUM(pe.qtd_itens_comprados * p.preco), 2) AS total_vendas
                FROM tb_pedidos pe
                JOIN tb_produtos p ON pe.id_do_produto = p.ID
                GROUP BY pe.estado_uf_da_venda
                ORDER BY total_vendas DESC; -- Ordena por total para pegar os tops facilmente
            """)
            regioes_vendas_raw = cursor.fetchall()

            distribuicao_regiao = []
            for regiao_data in regioes_vendas_raw:
                regiao = regiao_data[0]
                total_vendas_regiao = regiao_data[1]
                percentual = round(100 * total_vendas_regiao / total_geral_vendas_percentual, 2)
                distribuicao_regiao.append((regiao, total_vendas_regiao, percentual))
        else:
            distribuicao_regiao = []


        top_5_regioes = distribuicao_regiao[:5]


        # --- 10. Quais são os 10 melhores clientes em relação ao valor de compras? ---
        cursor.execute("""
            SELECT pe.id_cliente,
                   SUM(p.preco * pe.qtd_itens_comprados) as valorTotalCompras
            FROM tb_pedidos AS pe
            JOIN tb_produtos AS p ON pe.id_do_produto = p.ID
            GROUP BY pe.id_cliente
            ORDER BY valorTotalCompras DESC
            LIMIT 10;
        """)
        top_clientes = cursor.fetchall()

        # --- Texto ---
        texto = "Prezados Gestores,\n\n"
        texto += "Segue o panorama geral de vendas e produtividade (Dados atualizados):\n\n"
        texto += f"**Visão Geral das Vendas:**\n"
        texto += f"  * O total de pedidos vendidos foi de {qtd_pedidos:,.0f}.\n"
        texto += f"  * Um total de {qtd_itens_vendidos:,.0f} itens foram comercializados.\n"
        texto += f"  * O valor total arrecadado com as vendas é de R$ {valor_total_vendido:,.2f}.\n"
        texto += f"  * A média geral de itens por pedido é de {media_itens_por_pedido:,.2f}.\n\n"

        texto += f"**Métricas de Valor:**\n"
        texto += f"  * O ticket médio por pedido está em R$ {ticket_medio_pedidos:,.2f}.\n"
        texto += f"  * O ticket médio por item é de R$ {ticket_medio_itens:,.2f}.\n"
        texto += f"  * O ticket médio por cliente é de R$ {ticket_medio_clientes:,.2f}.\n\n"

        if top_clientes:
            texto += "**Nossos Melhores Clientes (Top 10 em Valor de Compras):**\n"
            for i, cliente in enumerate(top_clientes):
                cliente_id = cliente[0]
                valor_compras = cliente[1]
                texto += f"  * {i+1}. Cliente {cliente_id}: R$ {valor_compras:,.2f}\n"
        else:
            texto += "Não há dados de clientes suficientes para listar os principais compradores.\n\n"

        texto += f"\n**Desempenho Regional:**\n"
        if regiao_maior_venda != "N/A":
             texto += f"  * A região com maior valor de vendas é {regiao_maior_venda}, totalizando R$ {valor_regiao_maior_venda:,.2f}.\n\n"
        else:
            texto += "  * Não há dados de região com maior valor de vendas.\n\n"

        if top_5_regioes:
            texto += "A distribuição de representatividade de vendas por região (Top 5):\n"
            for regiao_data in top_5_regioes:
                texto += f"  * {regiao_data[0]}: {regiao_data[2]:,.2f}% (Total: R$ {regiao_data[1]:,.2f})\n"
            if len(distribuicao_regiao) > 5:
                texto += "(Demais regiões com percentuais similares)\n\n"
        else:
            texto += "Não há dados de vendas por região para análise.\n\n"

        return texto

    except sqlite3.Error as e:
        return f"Erro ao acessar o banco de dados: {e}"
    except Exception as e:
        return f"Erro inesperado ao gerar o panorama: {e}"
    finally:
        if conn:
            conn.close()



panorama_final = gerar_panorama_vendas_completo(caminho_db)
print(panorama_final)
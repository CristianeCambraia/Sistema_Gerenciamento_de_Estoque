import tkinter as tk
from tkinter import ttk
import customtkinter
import sqlite3

# conecta com banco de dados
# create

def criar_banco():
    conexao = sqlite3.connect("banco_dados_estoque.db")
    terminal_sql = conexao.cursor()

    # Tabela de cadastros
    terminal_sql.execute("""CREATE TABLE IF NOT EXISTS cadastros (nome text, quantidade decimal, descricao text, 
    preco decimal)""")

    # Tabela de entradas
    terminal_sql.execute("""CREATE TABLE IF NOT EXISTS entradas (id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto TEXT NOT NULL,quantidade REAL NOT NULL,data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(produto) REFERENCES cadastros(nome))""")

    # Tabela de saídas
    terminal_sql.execute("""CREATE TABLE IF NOT EXISTS saidas (id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto TEXT NOT NULL,quantidade REAL NOT NULL,data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(produto) 
    REFERENCES cadastros(nome))""")

    conexao.commit()
    conexao.close()


# limpa os dados da tela cadastro
def limpar_campos_cadastro():
    nome_cadastro.delete(0, tk.END)  # Limpa o campo de nome
    preco_cadastro.delete(0, tk.END)  # Limpa o campo de preço
    descricao_cadastro.delete('1.0', tk.END)  # Limpa o campo de descrição



# create
def salvar_dados():
    conexao = sqlite3.connect("banco_dados_estoque.db")
    terminal_sql = conexao.cursor()
    terminal_sql.execute(f"INSERT INTO cadastros (nome, quantidade, descricao, preco) VALUES ('{nome_cadastro.get()}', '{0}', '{str(descricao_cadastro.get('1.0', 'end'))}', '{float(preco_cadastro.get())}')")
    conexao.commit()
    conexao.close()

    limpar_campos_cadastro()  # Limpa os campos após salvar

# read
def ler_dados():
    conexao = sqlite3.connect("banco_dados_estoque.db")
    terminal_sql = conexao.cursor()
    terminal_sql.execute("SELECT * FROM cadastros")
    receber_dados = terminal_sql.fetchall()


    for row in tabela_relatorio_estoque.get_children(): #usado para impedir repetir novos dados no relatório
        tabela_relatorio_estoque.delete(row)

    for i in receber_dados:
        nome = str(i[0])
        quantidade = str(i[1])
        descricao = str(i[2])
        preco = "R$ {:.2f}".format(float(i[3]))
        tabela_relatorio_estoque.insert("", tk.END, values=(nome, quantidade, descricao, preco))






# inserir dados e apagar itens  duplicados na caixinha tela entrada
# Variáveis para controle de seleção
selected_entrada = None

def dados_tela_entrada_cadastro():
    global selected_entrada

    # Limpa o frame de seleção
    for widget in scrollable_entrada.winfo_children():
        widget.destroy()

    conexao = sqlite3.connect("banco_dados_estoque.db")
    terminal_sql_entrada = conexao.cursor()
    terminal_sql_entrada.execute("SELECT nome FROM cadastros")
    produtos = terminal_sql_entrada.fetchall()

    for produto in produtos:
        nome = produto[0]

        # Cria um botão/checkbox para cada item
        btn = customtkinter.CTkCheckBox(scrollable_entrada,text=nome,state="normal" if selected_entrada is None or
        selected_entrada == nome else "disabled")

        # Configura o comando
        btn.configure(command=lambda n=nome, b=btn: selecionar_entrada(n, b))

        # Marca como selecionado se for o item atual
        if selected_entrada == nome:
            btn.select()

        btn.pack(anchor='w', pady=2)


def selecionar_entrada(nome, checkbox):
    global selected_entrada

    if checkbox.get() == 1:  # Se está marcando
        selected_entrada = nome
        # Atualiza todos os checkboxes
        for widget in scrollable_entrada.winfo_children():
            if isinstance(widget, customtkinter.CTkCheckBox):
                if widget != checkbox:
                    widget.deselect()
                    widget.configure(state="disabled")
        seleciona_item_entrada(nome)
    else:  # Se está desmarcando
        selected_entrada = None
        # Habilita todos os checkboxes
        for widget in scrollable_entrada.winfo_children():
            if isinstance(widget, customtkinter.CTkCheckBox):
                widget.configure(state="normal")
        limpar_campos_entrada()


def limpar_campos_entrada():
    global selected_entrada
    selected_entrada = None
    produto_nome_tela_entrada.configure(state='normal')
    produto_nome_tela_entrada.delete(0, tk.END)
    produto_nome_tela_entrada.configure(state='readonly')
    produto_qnt_tela_entrada.delete(0, tk.END)

    # Limpa os itens da lista
    for item in itens_adicionados_entrada:
        item.destroy()
itens_adicionados_entrada = []


def seleciona_item_entrada(arg_item):
    conexao = sqlite3.connect("banco_dados_estoque.db")
    terminal_sql_entrada = conexao.cursor()
    terminal_sql_entrada.execute(f"SELECT nome, quantidade FROM cadastros WHERE nome ='{arg_item}'")
    produto_selecionado = terminal_sql_entrada.fetchone()  # Retorna (nome, quantidade)
    conexao.close()

    if produto_selecionado:
        nome = produto_selecionado[0]
        quantidade_ent = produto_selecionado[1]

        # Limpa os campos antes de preencher
        produto_nome_tela_entrada.delete(0, tk.END)

        # Preenche os campos com os dados do produto selecionado
        produto_nome_tela_entrada.insert(0, produto_selecionado[0])  # Nome

        # Habilita edição temporária (se o campo estiver como 'readonly')
        produto_nome_tela_entrada.configure(state='normal')

        # Limpa e insere o texto formatado
        produto_nome_tela_entrada.delete(0, tk.END)
        produto_nome_tela_entrada.insert(0, f"{nome} ({quantidade_ent} un)")  # Formato limpo

        # Volta para 'readonly'
        produto_nome_tela_entrada.configure(state='readonly')

        # Preenche o campo de quantidade separadamente (para edição)
        produto_nome_tela_entrada.delete(0, tk.END)

global nome_produto_tela_editar, preco_produto_tela_editar, descricao_tela_editar


# Variável global para armazenar os itens adicionados
itens_adicionados_entrada = []


def adicionar_item():
    global selected_entrada


    if selected_entrada:
        # Pega a quantidade digitada (ou 1 se vazio)
        quantidade = produto_qnt_tela_entrada.get() or "1"

        # Cria um frame para o item
        item_frame = customtkinter.CTkFrame(line_frame_tela_entrada)
        item_frame.pack(fill='x', pady=2)

        # Label com nome e quantidade
        label = customtkinter.CTkLabel(item_frame,text=f"{selected_entrada} - {quantidade} un",width=200,anchor='w')
        label.pack(side='left', padx=5)

        # Botão de lixeira
        btn_remover = customtkinter.CTkButton(item_frame,text="🗑️",width=30,command=lambda
            frame=item_frame: remover_item(frame))
        btn_remover.pack(side='right')

        # Armazena o item
        itens_adicionados_entrada.append(item_frame)

        # Limpa o campo de quantidade após adicionar
        produto_qnt_tela_entrada.delete(0, tk.END)


def remover_item(frame):
    global itens_adicionados_entrada
    frame.destroy()
    itens_adicionados_entrada.remove(frame)


def limpar_campos_entrada():
    # Limpa os campos de input
    produto_nome_tela_entrada.delete(0, tk.END)
    produto_qnt_tela_entrada.delete(0, tk.END)

    # Remove todos os itens da lista direita
    for item in itens_adicionados:
        item.destroy()
itens_adicionados = []  # Reseta a lista



def salvar_entrada():
    global itens_adicionados_entrada

    if not itens_adicionados_entrada:
        messagebox.showwarning("Aviso", "Nenhum item adicionado para registrar entrada!")
        return

    # Confirmação com usuário
    if not messagebox.askyesno("Confirmar", "Deseja registrar esta entrada?"):
        return

    try:
        conexao = sqlite3.connect("banco_dados_estoque.db")
        cursor = conexao.cursor()

        # Processa cada item da entrada
        for item_frame in itens_adicionados_entrada:
            # Obtém os widgets do frame do item
            for widget in item_frame.winfo_children():
                if isinstance(widget, customtkinter.CTkLabel):
                    texto = widget.cget("text")
                    partes = texto.split(" - ")
                    nome_produto = partes[0]
                    quantidade = float(partes[1].replace(" un", ""))

                    # Atualiza o estoque (aumenta a quantidade)
                    cursor.execute("UPDATE cadastros SET quantidade = quantidade + ? WHERE nome = ?",
                                   (quantidade, nome_produto))

                    # Registra a entrada
                    cursor.execute("INSERT INTO entradas (produto, quantidade) VALUES (?, ?)",
                                   (nome_produto, quantidade))

        conexao.commit()
        messagebox.showinfo("Sucesso", "Entrada registrada com sucesso!")

        # Atualiza o relatório
        ler_entradas()

        # Limpa os campos e os itens do scroll
        limpar_campos_entrada()

        # Limpa os itens adicionados
        for item in itens_adicionados_entrada[:]:  # Usamos [:] para criar uma cópia da lista
            item.destroy()
            itens_adicionados_entrada.remove(item)

    except ValueError:
        messagebox.showerror("Erro", "Quantidade inválida!")
        conexao.rollback()
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao registrar entrada:\n{str(e)}")
        conexao.rollback()
    finally:
        if 'conexao' in locals():
            conexao.close()


def ler_entradas():
    try:
        conexao = sqlite3.connect("banco_dados_estoque.db")
        cursor = conexao.cursor()

        # Limpa a tabela antes de carregar novos dados
        for row in tabela_entrada.get_children():
            tabela_entrada.delete(row)

        # Busca as entradas registradas formatando a data
        cursor.execute("""SELECT produto, quantidade, strftime('%d/%m/%Y %H:%M', data) 
         FROM entradas ORDER BY data DESC""")
        entradas = cursor.fetchall()

        # Adiciona cada entrada na tabela
        for entrada in entradas:
            tabela_entrada.insert("", tk.END, values=(entrada[0],  # Nome do produto
                f"{entrada[1]:.2f} un",  # Quantidade formatada
                entrada[2]))  # Data formatada


    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar entradas:\n{str(e)}")
    finally:
        if 'conexao' in locals():
            conexao.close()


# Adicione esta variável global no início do seu código (junto com as outras)
selected_editar = None


def dados_tela_editar_cadastro():
    global selected_editar

    # Limpa o frame de seleção
    for widget in tabela_produtos_tela_editar.winfo_children():
        widget.destroy()

    conexao = sqlite3.connect("banco_dados_estoque.db")
    terminal_sql_editar = conexao.cursor()
    terminal_sql_editar.execute("SELECT nome FROM cadastros")
    items = terminal_sql_editar.fetchall()

    for item in items:
        nome = item[0]

        # Cria um botão/checkbox para cada item
        btn = customtkinter.CTkCheckBox(tabela_produtos_tela_editar,text=nome, state="normal" if selected_editar
        is None or selected_editar == nome else "disabled")

        # Configura o comando
        btn.configure(command=lambda n=nome, b=btn: selecionar_editar(n, b))

        # Marca como selecionado se for o item atual
        if selected_editar == nome:
            btn.select()

        btn.grid(pady=5)

def seleciona_item(arg_item):
    global selected_editar

    conexao = sqlite3.connect("banco_dados_estoque.db")
    terminal_sql_editar = conexao.cursor()
    terminal_sql_editar.execute(f"SELECT * FROM cadastros WHERE nome ='{arg_item}'")
    produto_selecionado = terminal_sql_editar.fetchone()
    conexao.close()

    if produto_selecionado:
        # Limpa os campos antes de preencher
        nome_produto_tela_editar.delete(0, tk.END)
        preco_produto_tela_editar.delete(0, tk.END)
        descricao_tela_editar.delete('1.0', tk.END)

        # Preenche os campos com os dados do produto selecionado
        nome_produto_tela_editar.insert(0, produto_selecionado[0])  # Nome
        preco_produto_tela_editar.insert(0, produto_selecionado[3])  # Preço
        descricao_tela_editar.insert('1.0', produto_selecionado[2])  # Descrição

        # Atualiza a seleção global
        selected_editar = arg_item


def selecionar_editar(nome, checkbox):
    global selected_editar

    if checkbox.get() == 1:  # Se está marcando
        selected_editar = nome
        # Atualiza todos os checkboxes
        for widget in tabela_produtos_tela_editar.winfo_children():
            if isinstance(widget, customtkinter.CTkCheckBox):
                if widget != checkbox:
                    widget.deselect()
                    widget.configure(state="disabled")
        seleciona_item(nome)
    else:  # Se está desmarcando
        selected_editar = None
        # Habilita todos os checkboxes
        for widget in tabela_produtos_tela_editar.winfo_children():
            if isinstance(widget, customtkinter.CTkCheckBox):
                widget.configure(state="normal")
        limpar_campos_edicao()


def limpar_campos_edicao():
    nome_produto_tela_editar.delete(0, tk.END)
    preco_produto_tela_editar.delete(0, tk.END)
    descricao_tela_editar.delete('1.0', tk.END)



def salvar_edicao():
    global selected_editar

    if selected_editar is None:
        print("Nenhum item selecionado para edição")
        return

    # Obter os novos valores dos campos
    novo_nome = nome_produto_tela_editar.get()
    novo_preco = preco_produto_tela_editar.get()
    nova_descricao = descricao_tela_editar.get("1.0", "end-1c")

    try:
        conexao = sqlite3.connect("banco_dados_estoque.db")
        terminal_sql = conexao.cursor()

        terminal_sql.execute("""UPDATE cadastros SET nome = ?, preco = ?, descricao = ?WHERE nome = ?""",
        (novo_nome, float(novo_preco), nova_descricao, selected_editar))

        conexao.commit()
        conexao.close()

        # Limpa a seleção e os campos após salvar
        selected_editar = None
        limpar_campos_edicao()  # Esta linha foi adicionada

        # Atualiza a lista de produtos
        dados_tela_editar_cadastro()

        # Atualiza o relatório
        ler_dados()

        print("Produto atualizado com sucesso! Campos limpos.")

    except Exception as e:
        print(f"Erro ao atualizar produto: {e}")


def excluir_item():
    global selected_editar

    if selected_editar is None:
        print("Nenhum item selecionado para exclusão")
        return

    try:
        conexao = sqlite3.connect("banco_dados_estoque.db")
        terminal_sql = conexao.cursor()

        # Remove o registro do banco de dados
        terminal_sql.execute("DELETE FROM cadastros WHERE nome = ?", (selected_editar,))

        conexao.commit()
        conexao.close()

        # Limpa a seleção
        selected_editar = None
        limpar_campos_edicao()

        # Atualiza a lista de produtos
        dados_tela_editar_cadastro()

        # Atualiza o relatório
        ler_dados()

        print("Produto excluído com sucesso!")

    except Exception as e:
        print(f"Erro ao excluir produto: {e}")


def cancelar_edicao():
    global selected_editar

    # Desmarca o checkbox selecionado (se houver)
    if selected_editar:
        for widget in tabela_produtos_tela_editar.winfo_children():
            if isinstance(widget, customtkinter.CTkCheckBox) and widget.cget("text") == selected_editar:
                widget.deselect()
                break

    # Limpa os campos
    limpar_campos_edicao()

    # Reativa todos os checkboxes
    for widget in tabela_produtos_tela_editar.winfo_children():
        if isinstance(widget, customtkinter.CTkCheckBox):
            widget.configure(state="normal")

    # Reseta a seleção global
    selected_editar = None
    print("Edição cancelada - Campos limpos e seleção resetada")



# inserir dados e apagar itens  duplicados na caixinha tela saida
# Variáveis para controle de seleção
selected_saida = None
itens_adicionados_saida = []
def dados_tela_saida_cadastro():
    global selected_saida

    for widget in scroll_tabela_saida.winfo_children():
        widget.destroy()

    conexao = sqlite3.connect("banco_dados_estoque.db")
    terminal_sql_saida = conexao.cursor()
    terminal_sql_saida.execute("SELECT nome FROM cadastros")
    produtos = terminal_sql_saida.fetchall()

    for produto in produtos:
        nome = produto[0]

        btn = customtkinter.CTkCheckBox(scroll_tabela_saida,text=nome,state="normal" if selected_saida
        is None or selected_saida == nome else "disabled")
        btn.configure(command=lambda n=nome, b=btn: selecionar_saida(n, b))

        if selected_saida == nome:
            btn.select()

        btn.pack(anchor='w', pady=2)


def seleciona_item_saida(arg_item):
    conexao = sqlite3.connect("banco_dados_estoque.db")
    terminal_sql_saida = conexao.cursor()
    terminal_sql_saida.execute(f"SELECT nome, quantidade FROM cadastros WHERE nome ='{arg_item}'")
    produto_selecionado = terminal_sql_saida.fetchone()
    conexao.close()

    if produto_selecionado:
        nome = produto_selecionado[0]
        quantidade = produto_selecionado[1]

        # Habilita edição temporária (se o campo estiver como 'readonly')
        nome_produto_tela_saida.configure(state='normal')

        # Limpa e insere o texto formatado
        nome_produto_tela_saida.delete(0, tk.END)
        nome_produto_tela_saida.insert(0, f"{nome} ({quantidade} un)")  # Formato limpo

        # Volta para 'readonly' (opcional)
        nome_produto_tela_saida.configure(state='readonly')

        # Preenche o campo de quantidade separadamente (para edição)
        quantidade_tela_saida.delete(0, tk.END)




def limpar_campos_saida():
    global selected_saida
    selected_saida = None
    itens_adicionados_saida = []
    nome_produto_tela_saida.configure(state='normal')
    nome_produto_tela_saida.delete(0, tk.END)
    nome_produto_tela_saida.configure(state='readonly')
    quantidade_tela_saida.delete(0, tk.END)

    # Limpa os itens da lista
    for item in itens_adicionados_saida:
        item.destroy()
    itens_adicionados_saida = []


def selecionar_saida(nome, checkbox):
    global selected_saida

    if checkbox.get() == 1:
        selected_saida = nome
        for widget in scroll_tabela_saida.winfo_children():
            if isinstance(widget, customtkinter.CTkCheckBox):
                if widget != checkbox:
                    widget.deselect()
                    widget.configure(state="disabled")
        seleciona_item_saida(nome)
    else:
        selected_saida = None
        for widget in scroll_tabela_saida.winfo_children():
            if isinstance(widget, customtkinter.CTkCheckBox):
                widget.configure(state="normal")
        limpar_campos_saida()  # Agora usa a função atualizada


def adicionar_item_saida():
    global selected_saida
    global itens_adicionados_saida

    if selected_saida:
        # Pega a quantidade digitada (ou 1 se vazio)
        quantidade = quantidade_tela_saida.get() or "1"

        # Cria um frame para o item
        item_frame = customtkinter.CTkFrame(caixa_saida)
        item_frame.pack(fill='x', pady=2)

        # Label com nome e quantidade
        label = customtkinter.CTkLabel(item_frame,text=f"{selected_saida} - {quantidade} un",width=200,anchor='w')
        label.pack(side='left', padx=5)

        # Botão de lixeira
        btn_remover = customtkinter.CTkButton(item_frame,text="🗑️",width=30,command=lambda
        frame=item_frame: remover_item_saida(frame))
        btn_remover.pack(side='right')

        # Armazena o item
        itens_adicionados_saida.append(item_frame)

        # Limpa o campo de quantidade após adicionar
        quantidade_tela_saida.delete(0, tk.END)


def remover_item_saida(frame):
    global itens_adicionados_saida
    frame.destroy()
    itens_adicionados_saida.remove(frame)


from tkinter import messagebox
from datetime import datetime



def salvar_saida():
    global itens_adicionados_saida

    if not itens_adicionados_saida:
        messagebox.showwarning("Aviso", "Nenhum item adicionado para registrar saída!")
        return

    # Confirmação com usuário
    if not messagebox.askyesno("Confirmar", "Deseja registrar esta saída?"):
        return

    try:
        conexao = sqlite3.connect("banco_dados_estoque.db")
        cursor = conexao.cursor()

        # Processa cada item da saída
        for item_frame in itens_adicionados_saida:
            # Obtém os widgets do frame do item
            for widget in item_frame.winfo_children():
                if isinstance(widget, customtkinter.CTkLabel):
                    texto = widget.cget("text")
                    partes = texto.split(" - ")
                    nome_produto = partes[0]
                    quantidade = float(partes[1].replace(" un", ""))

                    # Verifica se há estoque suficiente
                    cursor.execute("SELECT quantidade FROM cadastros WHERE nome = ?", (nome_produto,))
                    resultado = cursor.fetchone()

                    if resultado is None:
                        messagebox.showerror("Erro", f"Produto '{nome_produto}' não encontrado no estoque!")
                        conexao.rollback()
                        return

                    estoque_atual = resultado[0]

                    if estoque_atual < quantidade:
                        messagebox.showerror("Erro",
                                             f"Estoque insuficiente para {nome_produto}!\nEstoque atual: {estoque_atual}")
                        conexao.rollback()
                        return

                    # Atualiza o estoque (diminui a quantidade)
                    cursor.execute("UPDATE cadastros SET quantidade = quantidade - ? WHERE nome = ?",
                                   (quantidade, nome_produto))

                    # Registra a saída
                    cursor.execute("INSERT INTO saidas (produto, quantidade) VALUES (?, ?)",
                                   (nome_produto, quantidade))

        conexao.commit()
        messagebox.showinfo("Sucesso", "Saída registrada com sucesso!")

        # Atualiza o relatório
        ler_saidas()

        # Limpa os campos e os itens do scroll
        limpar_campos_saida()

        # Limpa os itens adicionados
        for item in itens_adicionados_saida[:]:  # Usamos [:] para criar uma cópia da lista
            item.destroy()
            itens_adicionados_saida.remove(item)

    except ValueError:
        messagebox.showerror("Erro", "Quantidade inválida! Use números.")
        if 'conexao' in locals():
            conexao.rollback()
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao registrar saída:\n{str(e)}")
        if 'conexao' in locals():
            conexao.rollback()
    finally:
        if 'conexao' in locals():
            conexao.close()


def ler_saidas():
    try:
        conexao = sqlite3.connect("banco_dados_estoque.db")
        cursor = conexao.cursor()

        # Limpa a tabela antes de carregar novos dados
        for row in tabela_saida.get_children():
            tabela_saida.delete(row)

        # Busca as saídas registradas formatando a data
        cursor.execute("""SELECT produto, quantidade, 
                         strftime('%d/%m/%Y %H:%M', data) 
                         FROM saidas ORDER BY data DESC""")
        saidas = cursor.fetchall()

        # Adiciona cada saída na tabela
        for saida in saidas:
            tabela_saida.insert("", tk.END, values=(
                saida[0],  # Nome do produto
                f"{saida[1]:.2f} un",  # Quantidade formatada
                saida[2]  # Data formatada
            ))

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar saídas:\n{str(e)}")
    finally:
        if 'conexao' in locals():
            conexao.close()



# chama a função de criar o banco de dados
criar_banco()


def abrir_frame_tela_editar():
    # fechar frames
    frame_cadastro.grid_forget()
    frame_tela_saida.grid_forget()
    frame_tela_entrada.grid_forget()
    frame_tela_relatorio.grid_forget()
    frame_relatorio_entrada.grid_forget()
    frame_relatorio_saida.grid_forget()
    # abrir frames
    frame_tela_editar.grid_propagate(False)
    frame_tela_editar.grid(row=0, column=1, padx=5, pady=5)
    dados_tela_editar_cadastro()


def abrir_frame_cadastro():
    # fechar frames
    frame_tela_editar.grid_forget()
    frame_tela_saida.grid_forget()
    frame_tela_entrada.grid_forget()
    frame_tela_relatorio.grid_forget()
    frame_relatorio_saida.grid_forget()
    frame_relatorio_entrada.grid_forget()

    # abrir frames
    frame_cadastro.grid_propagate(False)
    frame_cadastro.grid(row=0, column=1, padx=5, pady=5)


def abrir_frame_tela_saida():
    # fechar frames
    frame_cadastro.grid_forget()
    frame_tela_editar.grid_forget()
    frame_tela_entrada.grid_forget()
    frame_tela_relatorio.grid_forget()
    frame_relatorio_saida.grid_forget()
    frame_relatorio_entrada.grid_forget()
    # abrir frames
    frame_tela_saida.grid_propagate(False)
    frame_tela_saida.grid(row=0, column=1, padx=5, pady=5)
    dados_tela_saida_cadastro()
    ler_entradas()


def abrir_frame_tela_entrada():
    # fechar frames
    frame_cadastro.grid_forget()
    frame_tela_editar.grid_forget()
    frame_tela_saida.grid_forget()
    frame_tela_relatorio.grid_forget()
    frame_relatorio_saida.grid_forget()
    frame_relatorio_entrada.grid_forget()
    # abrir frames
    frame_tela_entrada.grid_propagate(False)
    frame_tela_entrada.grid(row=0, column=1, padx=5, pady=5)
    dados_tela_entrada_cadastro()



def abrir_frame_tela_relatorio():
    # fechar frames
    frame_cadastro.grid_forget()
    frame_tela_editar.grid_forget()
    frame_tela_saida.grid_forget()
    frame_tela_entrada.grid_forget()
    frame_relatorio_saida.grid_forget()
    frame_relatorio_entrada.grid_forget()
    # abrir frames
    frame_tela_relatorio.grid_propagate(False)
    frame_tela_relatorio.grid(row=0, column=1, padx=5, pady=5)
    ler_dados()


# DEF TELA DE RELATÓRIO
def abrir_frame_relatorio_saida():
    # fechar frames
    frame_tela_relatorio.grid_forget()
    frame_relatorio_entrada.grid_forget()
    # abrir frames
    frame_relatorio_saida.grid_propagate(False)
    frame_relatorio_saida.grid(row=0, column=1, padx=5, pady=5)
    ler_saidas()


def abrir_frame_relatorio_entrada():
    # fechar frames
    frame_tela_relatorio.grid_forget()
    frame_relatorio_saida.grid_forget()
    # abrir frames
    frame_relatorio_entrada.grid_propagate(False)
    frame_relatorio_entrada.grid(row=0, column=1, padx=5, pady=5)


# DEF JANELA POPUP
def abrir_popup():
    janela_pop = customtkinter.CTk()
    janela_pop.title("Popup")
    janela_pop.geometry("325x240")

    # label de janela popup
    label_relatorio_pop = customtkinter.CTkLabel(janela_pop, text="Escolher Relatório(s):")
    label_relatorio_pop.grid(pady=10, padx=10, row=1, column=0, stick="w")

    exportar_estoque_pop = customtkinter.CTkCheckBox(janela_pop, text="Exportar Estoque")
    exportar_estoque_pop.grid(pady=10, padx=10, row=2, column=0, stick="w")

    exportar_saida_pop = customtkinter.CTkCheckBox(janela_pop, text="Exportar Saída")
    exportar_saida_pop.grid(pady=10, padx=10, row=3, column=0, stick="w")

    exportar_entrada_pop = customtkinter.CTkCheckBox(janela_pop, text="Exportar Entrada")
    exportar_entrada_pop.grid(pady=10, padx=10, row=4, column=0, stick="w")

    # titulo de escolher pra onde vai a exportação janela popup
    label_exportacao_pop = customtkinter.CTkLabel(janela_pop, text="Escolher Extenção:")
    label_exportacao_pop.grid(pady=10, padx=10, row=1, column=1, columnspan=2, stick="w")

    # caixas formato dos arquivos janela popup
    exportar_word = customtkinter.CTkCheckBox(janela_pop, text="Formato WORD")
    exportar_word.grid(pady=10, padx=10, row=2, column=1, columnspan=2, stick="w")

    exportar_pdf = customtkinter.CTkCheckBox(janela_pop, text="Formato PDF")
    exportar_pdf.grid(pady=10, padx=10, row=3, column=1, columnspan=2, stick="w")

    exportar_excel = customtkinter.CTkCheckBox(janela_pop, text="Formato EXCEL")
    exportar_excel.grid(pady=10, padx=10, row=4, column=1, columnspan=2, stick="w")

    # botões do popup
    botao_salvar_pop = customtkinter.CTkButton(janela_pop, text="Salvar", width=80, fg_color="black",
                                               hover_color="#2f394a")
    botao_salvar_pop.grid(padx=5, pady=5, row=5, column=2, stick="w")

    botao_cancelar_pop = customtkinter.CTkButton(janela_pop, text="Cancelar", width=80, fg_color="black",
                                                 hover_color="#2f394a")
    botao_cancelar_pop.grid(padx=5, pady=5, row=5, column=1, stick="e")

    janela_pop.mainloop()




# janela principal
janela_principal = customtkinter.CTk()
janela_principal.title("Sistema de Gerenciamento de Estoque")
janela_principal.geometry("800x400")

# aparencia da janela principal
customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")

# janela frame menu
frame_menu = customtkinter.CTkFrame(janela_principal, width=190, height=380, corner_radius=0, fg_color="gray")
frame_menu.grid_propagate(False)
frame_menu.grid(row=0, column=0, padx=5, pady=10)

# janela frame cadastro no menu
frame_cadastro = customtkinter.CTkFrame(janela_principal, width=590, height=380, corner_radius=0, fg_color="gray")
frame_cadastro.grid_propagate(False)
frame_cadastro.grid(row=0, column=1, padx=5, pady=5)

# frame para acessar tela editar no menu
frame_tela_editar = customtkinter.CTkFrame(janela_principal, width=590, height=380, fg_color="gray", corner_radius=0)
frame_tela_editar.grid_propagate(False)

# frame para acessar tela saida no menu
frame_tela_saida = customtkinter.CTkFrame(janela_principal, width=590, height=380, fg_color="gray", corner_radius=0)
frame_tela_saida.grid_propagate(False)

# frame para acessar tela entrada no menu
frame_tela_entrada = customtkinter.CTkFrame(janela_principal, width=590, height=380, fg_color="gray", corner_radius=0)
frame_tela_entrada.grid_propagate(False)

# frame para acessar tela relatório estoque
frame_tela_relatorio = customtkinter.CTkFrame(janela_principal, width=590, height=380, fg_color="gray", corner_radius=0)
frame_tela_relatorio.grid_propagate(False)

# frame para acessar tela relatório de saida
frame_relatorio_saida = customtkinter.CTkFrame(janela_principal, width=590, height=380, fg_color="gray",
                                               corner_radius=0)
frame_relatorio_saida.grid_propagate(False)

# frame para acessar tela relatório de entrada
frame_relatorio_entrada = customtkinter.CTkFrame(janela_principal, width=590, height=380, fg_color="gray",
                                                 corner_radius=0)
frame_relatorio_entrada.grid_propagate(False)

# janela frame menu
botao_cadastrar_tela_cadastro = customtkinter.CTkButton(frame_menu, text="Cadastrar", width=100, fg_color="Black",
                                                        hover_color="#2f394a", command=abrir_frame_cadastro)
botao_cadastrar_tela_cadastro.grid(padx=5, pady=5, column=0, row=1)

botao_editar_tela_cadastro = customtkinter.CTkButton(frame_menu, text="Editar", width=100, fg_color="Black",
                                                     hover_color="#2f394a", command=abrir_frame_tela_editar)
botao_editar_tela_cadastro.grid(padx=5, pady=5, column=0, row=2)

botao_saida_tela_cadastro = customtkinter.CTkButton(frame_menu, text="Saída", width=100, fg_color="Black",
                                                    hover_color="#2f394a", command=abrir_frame_tela_saida)
botao_saida_tela_cadastro.grid(padx=5, pady=5, column=0, row=3)

botao_entrada_tela_cadastro = customtkinter.CTkButton(frame_menu, text="Entrada", width=100, fg_color="Black",
                                                      hover_color="#2f394a", command=abrir_frame_tela_entrada)
botao_entrada_tela_cadastro.grid(padx=5, pady=5, column=0, row=4)

botao_relatorio_tela_cadastro = customtkinter.CTkButton(frame_menu, text="Relatórios", width=100, fg_color="Black",
                                                        hover_color="#2f394a", command=abrir_frame_tela_relatorio)
botao_relatorio_tela_cadastro.grid(padx=5, pady=5, column=0, row=5)

mensagem_tela_cadastro = customtkinter.CTkLabel(frame_menu, text="Nome do Sistema", font=("Couvier", 18, "bold"),
                                                text_color="Black")
mensagem_tela_cadastro.grid(pady=35, padx=22, row=0, column=0)

# janela frame cadastro
botao_salvar_tela_cadastro = customtkinter.CTkButton(frame_cadastro, text="Salvar", width=80, fg_color="black",
                                                     hover_color="#2f394a", command=salvar_dados)
botao_salvar_tela_cadastro.grid(padx=5, pady=5, sticky="e", row=4, column=1)

botao_cancelar_tela_cadastro = customtkinter.CTkButton(frame_cadastro, text="Cancelar", width=80, fg_color="black",
                                                       hover_color="#2f394a", command=limpar_campos_cadastro)
botao_cancelar_tela_cadastro.grid(padx=5, pady=5, row=4, column=1, stick="w")

mensagem_cadastro = customtkinter.CTkLabel(frame_cadastro, text="Cadastro de Produtos", font=("Couvier", 18, "bold"),
                                           text_color="Black")
mensagem_cadastro.grid(pady=30, row=0, column=1)

mensagem_nome_cadastro = customtkinter.CTkLabel(frame_cadastro, text="Nome do Produto", text_color="Black")
mensagem_nome_cadastro.grid(padx=40, row=1, column=0)

mensagem_preco_cadastro = customtkinter.CTkLabel(frame_cadastro, text="Preço (R$):", text_color="Black")
mensagem_preco_cadastro.grid(padx=40, row=2, column=0, sticky="ne")

mensagem_descricao_cadastro = customtkinter.CTkLabel(frame_cadastro, text="Descrição:", text_color="Black")
mensagem_descricao_cadastro.grid(padx=40, row=3, column=0, sticky="ne")

# placeholders na janela tela de saída frame cadastro
nome_cadastro = customtkinter.CTkEntry(frame_cadastro, placeholder_text="Digite o nome do produto:", width=300)
nome_cadastro.grid(padx=5, pady=5, row=1, column=1)

preco_cadastro = customtkinter.CTkEntry(frame_cadastro, placeholder_text="0,00", width=80)
preco_cadastro.grid(padx=5, pady=5, row=2, column=1, sticky="w")

descricao_cadastro = customtkinter.CTkTextbox(frame_cadastro, width=300, height=80)
descricao_cadastro.grid(padx=5, pady=5, row=3, column=1)

# tabela de lista janela de editar
tabela_produtos_tela_editar = customtkinter.CTkScrollableFrame(frame_tela_editar)
tabela_produtos_tela_editar.grid(column=0, rowspan=4, pady=0, padx=20, row=2)

mensagem_tela_editar = customtkinter.CTkLabel(frame_tela_editar, text="Editar Produtos Cadastrados",
                                              font=("Couvier", 18, "bold"), text_color="black")
mensagem_tela_editar.grid(pady=0, padx=0, row=0, column=0, columnspan=4)

buscar_produto_tela_editar = customtkinter.CTkEntry(frame_tela_editar, placeholder_text="Buscar produto:", width=220)
buscar_produto_tela_editar.grid(padx=20, pady=20, row=1, column=0, columnspan=4, stick="w")

nome_produto_tela_editar = customtkinter.CTkEntry(frame_tela_editar, placeholder_text="Nome do produto:", width=230)
nome_produto_tela_editar.grid(padx=5, pady=0, row=2, column=1, stick="w", columnspan=3)

preco_produto_tela_editar = customtkinter.CTkEntry(frame_tela_editar, placeholder_text="0.00:", width=80)
preco_produto_tela_editar.grid(padx=5, pady=0, row=3, column=1, stick="w", columnspan=3)

descricao_tela_editar = customtkinter.CTkTextbox(frame_tela_editar, width=300, height=80)
descricao_tela_editar.grid(padx=5, pady=0, row=4, column=1, stick="w", columnspan=3)

botao_excluir_tela_editar = customtkinter.CTkButton(frame_tela_editar, text="Excluir", width=80, fg_color="Red",
                                                    hover_color="#2f394a", command=excluir_item)

botao_excluir_tela_editar.grid(padx=5, pady=5, row=5, column=1, stick="w")

botao_cancelar_tela_editar = customtkinter.CTkButton(frame_tela_editar, text="Cancelar", width=80, fg_color="black",
                                        hover_color="#2f394a", command=cancelar_edicao)  # Adicionado o comando aqui
botao_cancelar_tela_editar.grid(padx=0, pady=5, row=5, column=2)


botao_salvar_tela_editar = customtkinter.CTkButton(frame_tela_editar, text="Salvar", width=80, fg_color="black",
                                                   hover_color="#2f394a", command=salvar_edicao)
botao_salvar_tela_editar.grid(padx=5, pady=5, row=5, column=3, stick="e")

# janela de saída
scroll_tabela_saida = customtkinter.CTkScrollableFrame(frame_tela_saida)
scroll_tabela_saida.grid(row=2, column=0, rowspan=4, pady=0, padx=20)

buscar_produto_tela_saida = customtkinter.CTkEntry(frame_tela_saida, placeholder_text="Buscar produto:", width=220)
buscar_produto_tela_saida.grid(padx=20, pady=20, row=1, column=0, stick="w")

nome_produto_tela_saida = customtkinter.CTkEntry(frame_tela_saida, placeholder_text="Nome e quantidade do produto:",
                                                 width=300)
nome_produto_tela_saida.grid(padx=0, pady=0, row=1, column=1, stick="we", columnspan=2)

quantidade_tela_saida = customtkinter.CTkEntry(frame_tela_saida, placeholder_text="Quantidade retirada: ", width=190)
quantidade_tela_saida.grid(padx=0, pady=0, row=2, column=1, stick="w")

# caixinha do produto tela saida
caixa_saida = customtkinter.CTkScrollableFrame(frame_tela_saida, height=100, width=300)
caixa_saida.grid(pady=0, row=3, column=1, columnspan=2, stick="we")

mensagem_tela_saida = customtkinter.CTkLabel(frame_tela_saida, text="Saída de produto", font=("Couvier", 18, "bold"),
                                             text_color="black")
mensagem_tela_saida.grid(pady=0, padx=0, row=0, column=1)


botao_cancelar_tela_saida = customtkinter.CTkButton(frame_tela_saida, text="Cancelar", width=80, fg_color="black",
                                                    hover_color="#2f394a", command=limpar_campos_saida)
botao_cancelar_tela_saida.grid(padx=0, pady=5, row=5, column=1, stick="w")


botao_salvar_tela_saida = customtkinter.CTkButton(frame_tela_saida, text="Salvar", width=80, fg_color="black",
                                                  hover_color="#2f394a", command=salvar_saida)
botao_salvar_tela_saida.grid(padx=0, pady=5, row=5, column=2, stick="e")


botao_adicionar_item_tela_saida = customtkinter.CTkButton(frame_tela_saida, text="Adicionar", width=80,
                                                fg_color="black", hover_color="#2f394a",command=adicionar_item_saida)
botao_adicionar_item_tela_saida.grid(padx=0, pady=5, row=2, column=2, stick="e")




# janela de entrada
scrollable_entrada = customtkinter.CTkScrollableFrame(frame_tela_entrada)
scrollable_entrada.grid(row=2, column=0, rowspan=4, pady=0, padx=20)

produto_buscar_tela_entrada = customtkinter.CTkEntry(frame_tela_entrada, placeholder_text="Buscar produto:", width=220)
produto_buscar_tela_entrada.grid(padx=20, pady=20, row=1, column=0, stick="w")

produto_nome_tela_entrada = customtkinter.CTkEntry(frame_tela_entrada, placeholder_text="Nome e quantidade do produto:",
                                                   width=300)
produto_nome_tela_entrada.grid(padx=0, pady=0, row=1, column=1, stick="we", columnspan=2)

produto_qnt_tela_entrada = customtkinter.CTkEntry(frame_tela_entrada, placeholder_text="Quantidade recebida : ",
                                                  width=190)
produto_qnt_tela_entrada.grid(padx=0, pady=0, row=2, column=1, stick="w")

# caixinha do produto tela entrada
line_frame_tela_entrada = customtkinter.CTkScrollableFrame(frame_tela_entrada, height=100, width=300)
line_frame_tela_entrada.grid(pady=0, row=3, column=1, columnspan=2, stick="we")

botao_cancelar_tela_entrada = customtkinter.CTkButton(frame_tela_entrada, text="Cancelar", width=80, fg_color="black",
                                                      hover_color="#2f394a", command=limpar_campos_entrada)
botao_cancelar_tela_entrada.grid(padx=0, pady=5, row=5, column=1, stick="w")

botao_salvar_tela_entrada = customtkinter.CTkButton(frame_tela_entrada, text="Salvar", width=80, fg_color="black",
                                                    hover_color="#2f394a", command=salvar_entrada)
botao_salvar_tela_entrada.grid(padx=0, pady=5, row=5, column=2, stick="e")

botao_adicionar_item_tela_entrada = customtkinter.CTkButton(frame_tela_entrada, text="Adicionar", width=80,
    fg_color="black", hover_color="#2f394a",command=adicionar_item)  # Remove o lambda, usa a função diretamente'''

botao_adicionar_item_tela_entrada.grid(padx=0, pady=5, row=2, column=2, stick="e")

mensagem_tela_entrada = customtkinter.CTkLabel(frame_tela_entrada, text="Entrada", font=("Couvier", 18, "bold"),
                                               text_color="black")
mensagem_tela_entrada.grid(pady=0, padx=0, row=0, column=1)

# pagina frame relatório estoque
produto_buscar_relatorio_estoque = customtkinter.CTkEntry(frame_tela_relatorio, placeholder_text="Buscar produto:",
                                                          width=220)
produto_buscar_relatorio_estoque.grid(padx=20, pady=20, row=1, column=0, stick="w")

mensagem_tela_relatorio = customtkinter.CTkLabel(frame_tela_relatorio, text="Relatório de estoque",
                                                 font=("Couvier", 18, "bold"), text_color="black")
mensagem_tela_relatorio.grid(pady=30, padx=30, row=0, column=0, columnspan=4)

# Define as colunas da tabela de relatorio icone estoque
columns = ("#1", "#2", "#3", "#4")

# Cria o Treeview do estoque FRAME 5
tabela_relatorio_estoque = ttk.Treeview(frame_tela_relatorio, columns=columns, show='headings', height=5)
# Adiciona a tabela à janela principal
tabela_relatorio_estoque.grid(pady=5, padx=10, column=0, columnspan=4, row=2, stick="wsne")

# Define os cabeçalhos das colunas tabela estoque FRAME5
tabela_relatorio_estoque.heading("#1", text="Nome")
tabela_relatorio_estoque.heading("#2", text="Quantidade")
tabela_relatorio_estoque.heading("#3", text="Descrição")
tabela_relatorio_estoque.heading("#4", text="Preço")
tabela_relatorio_estoque.column("#1", width=110)
tabela_relatorio_estoque.column("#2", width=110)
tabela_relatorio_estoque.column("#3", width=110)
tabela_relatorio_estoque.column("#4", width=110)


# scroll da tabela relatório estoque
scroll_tela_relatorio_estoque = tk.Scrollbar(frame_tela_relatorio, orient="vertical",
                                             command=tabela_relatorio_estoque.yview)
scroll_tela_relatorio_estoque.grid(row=2, column=4, stick="ns")

# botões da tela relatório
botao_estoque_tela_relatorio = customtkinter.CTkButton(frame_tela_relatorio, text="Estoque", width=80,
                                                       fg_color="black", hover_color="#2f394a",
                                                       command=abrir_frame_tela_relatorio)
botao_estoque_tela_relatorio.grid(padx=10, pady=5, row=3, column=1, stick="w")

botao_saida_tela_relatorio = customtkinter.CTkButton(frame_tela_relatorio, text="Saída", width=80, fg_color="black",
                                                     hover_color="#2f394a", command=abrir_frame_relatorio_saida)
botao_saida_tela_relatorio.grid(padx=10, pady=5, row=3, column=2, stick="w")

botao_entrada_tela_relatorio = customtkinter.CTkButton(frame_tela_relatorio, text="Entrada", width=80,
                                                       fg_color="black", hover_color="#2f394a",
                                                       command=abrir_frame_relatorio_entrada)
botao_entrada_tela_relatorio.grid(padx=10, pady=5, row=3, column=3, stick="w")

botao_exportar_tela_relatorio = customtkinter.CTkButton(frame_tela_relatorio, text="Exportar", width=80,
                                                        fg_color="black", hover_color="#2f394a", command=abrir_popup)
botao_exportar_tela_relatorio.grid(padx=10, pady=5, row=1, column=3, stick="w")

# Define as colunas da tabela do saida
columns = ("#1", "#2", "#3")

# Cria o Tabela de saida
tabela_saida = ttk.Treeview(frame_relatorio_saida, columns=columns, show='headings', height=5)

# Adiciona a tabela à janela principal
tabela_saida.grid(pady=5, padx=10, column=0, columnspan=4, row=2, stick="wsne")

# Define os cabeçalhos das colunas de saida
tabela_saida.heading("#1", text="Nome")
tabela_saida.heading("#2", text="Quantidade")
tabela_saida.heading("#3", text="Data/hora")
tabela_saida.column("#1", width=178)
tabela_saida.column("#2", width=178)
tabela_saida.column("#3", width=178)

# Insere alguns dados na tabela do frame saida
tabela_saida.insert("", tk.END, values=("Dado 1", "Dado 2", "Dado 3"))
tabela_saida.insert("", tk.END, values=("Dado 5", "Dado 6", "Dado 7"))
tabela_saida.insert("", tk.END, values=("Dado 9", "Dado 10", "Dado 11"))
tabela_saida.insert("", tk.END, values=("Dado 13", "Dado14", "Dado 15"))
tabela_saida.insert("", tk.END, values=("Dado 17", "Dado 18", "Dado 19"))
tabela_saida.insert("", tk.END, values=("Dado 21", "Dado 22", "Dado 23"))
tabela_saida.insert("", tk.END, values=("Dado 25", "Dado 26", "Dado 27"))
tabela_saida.insert("", tk.END, values=("Dado 29", "Dado29", "Dado 30"))

# scroll da tabela do frame saida
scroll_tabela_saida_relatorio = tk.Scrollbar(frame_relatorio_saida, orient="vertical", command=tabela_saida.yview)
scroll_tabela_saida_relatorio.grid(row=2, column=4, stick="ns")

# elementos janela relatorio saida
mensagem_relatorio_saida = customtkinter.CTkLabel(frame_relatorio_saida, text="Relatório de saída",
                                                  font=("Couvier", 18, "bold"), text_color="black")
mensagem_relatorio_saida.grid(pady=30, padx=30, row=0, column=0, columnspan=4)

produto_buscar_relatorio_saida = customtkinter.CTkEntry(frame_relatorio_saida, placeholder_text="Buscar produto:",
                                                        width=220)
produto_buscar_relatorio_saida.grid(padx=20, pady=20, row=1, column=0, stick="w")

botao_estoque_relatorio_saida = customtkinter.CTkButton(frame_relatorio_saida, text="Estoque", width=80,
                                                        fg_color="black", hover_color="#2f394a",
                                                        command=abrir_frame_tela_relatorio)
botao_estoque_relatorio_saida.grid(padx=10, pady=5, row=3, column=1, stick="w")

botao_saida_relatorio_saida = customtkinter.CTkButton(frame_relatorio_saida, text="Saída", width=80, fg_color="black",
                                                      hover_color="#2f394a", command=abrir_frame_relatorio_saida)
botao_saida_relatorio_saida.grid(padx=0, pady=5, row=3, column=2, stick="w")

botao_entrada_relatorio_saida = customtkinter.CTkButton(frame_relatorio_saida, text="Entrada", width=80,
                                                        fg_color="black", hover_color="#2f394a",
                                                        command=abrir_frame_relatorio_entrada)
botao_entrada_relatorio_saida.grid(padx=10, pady=5, row=3, column=3, stick="w")

botao_exportar_relatorio_saida = customtkinter.CTkButton(frame_relatorio_saida, text="Exportar", width=80,
                                                         fg_color="black", hover_color="#2f394a", command=abrir_popup)
botao_exportar_relatorio_saida.grid(padx=10, pady=5, row=1, column=3, stick="w")

# elementos janela relatorio entrada
mensagem_tela_entrada = customtkinter.CTkLabel(frame_relatorio_entrada, text="Relatório de entrada",
                                               font=("Couvier", 18, "bold"), text_color="black")
mensagem_tela_entrada.grid(pady=30, padx=30, row=0, column=0, columnspan=4)

produto_buscar_relatorio_entrada = customtkinter.CTkEntry(frame_relatorio_entrada, placeholder_text="Buscar produto:",
                                                          width=220)
produto_buscar_relatorio_entrada.grid(padx=20, pady=20, row=1, column=0, stick="w")

botao_estoque_relatorio_entrada = customtkinter.CTkButton(frame_relatorio_entrada, text="Estoque", width=80,
                                                          fg_color="black", hover_color="#2f394a",
                                                          command=abrir_frame_tela_relatorio)
botao_estoque_relatorio_entrada.grid(padx=10, pady=5, row=3, column=1, stick="w")

botao_saida_relatorio_entrada = customtkinter.CTkButton(frame_relatorio_entrada, text="Saída", width=80,
                                                        fg_color="black", hover_color="#2f394a",
                                                        command=abrir_frame_relatorio_saida)
botao_saida_relatorio_entrada.grid(padx=0, pady=5, row=3, column=2, stick="w")

botao_entrada_relatorio_entrada = customtkinter.CTkButton(frame_relatorio_entrada, text="Entrada", width=80,
                                                          fg_color="black", hover_color="#2f394a",
                                                          command=abrir_frame_relatorio_entrada)
botao_entrada_relatorio_entrada.grid(padx=10, pady=5, row=3, column=3, stick="w")

botao_exportar_relatorio_entrada = customtkinter.CTkButton(frame_relatorio_entrada, text="Exportar", width=80,
                                                           fg_color="black", hover_color="#2f394a",
                                                           command=abrir_popup)
botao_exportar_relatorio_entrada.grid(padx=10, pady=5, row=1, column=3, stick="w")

# Define as colunas da tabela da tela de entrada
columns = ("#1", "#2", "#3")

# Cria o Treeview do entrada
tabela_entrada = ttk.Treeview(frame_relatorio_entrada, columns=columns, show='headings', height=5)

# Adiciona a tabela à janela principal
tabela_entrada.grid(pady=5, padx=10, column=0, columnspan=4, row=2, stick="wsne")

# Define os cabeçalhos das colunas
tabela_entrada.heading("#1", text="Nome")
tabela_entrada.heading("#2", text="Quantidade")
tabela_entrada.heading("#3", text="Data/hora")
tabela_entrada.column("#1", width=178)
tabela_entrada.column("#2", width=178)
tabela_entrada.column("#3", width=178)

# Insere alguns dados na tabela de entrada
tabela_entrada.insert("", tk.END, values=("Dado 1", "Dado 2", "Dado 3"))
tabela_entrada.insert("", tk.END, values=("Dado 5", "Dado 6", "Dado 7"))
tabela_entrada.insert("", tk.END, values=("Dado 9", "Dado 10", "Dado 11"))
tabela_entrada.insert("", tk.END, values=("Dado 13", "Dado14", "Dado 15"))
tabela_entrada.insert("", tk.END, values=("Dado 17", "Dado 18", "Dado 19"))
tabela_entrada.insert("", tk.END, values=("Dado 21", "Dado 22", "Dado 23"))
tabela_entrada.insert("", tk.END, values=("Dado 25", "Dado 26", "Dado 27"))
tabela_entrada.insert("", tk.END, values=("Dado 29", "Dado29", "Dado 30"))

# scroll da tabela de entrada
scroll_tabela_entrada = tk.Scrollbar(frame_relatorio_entrada, orient="vertical", command=tabela_entrada.yview)
scroll_tabela_entrada.grid(row=2, column=4, stick="ns")

janela_principal.mainloop()

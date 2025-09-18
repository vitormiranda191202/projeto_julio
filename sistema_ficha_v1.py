import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração do banco
DATABASE_URL = "postgresql://neondb_owner:npg_yWMlIa8iB1mH@ep-plain-bonus-adrh7qhm-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Modelos do banco
class FichaProducao(Base):
    __tablename__ = "fichas_producao"
    __table_args__ = {"schema": "eguh_vest"}
    id = Column(Integer, primary_key=True, index=True)
    produto = Column(String(150), nullable=False)
    corte = Column(Integer, nullable=False)
    grade = Column(String(50), nullable=False)
    data = Column(Date, nullable=False)
    itens = relationship("ItemFicha", back_populates="ficha", cascade="all, delete-orphan")

class ItemFicha(Base):
    __tablename__ = "itens_ficha"
    __table_args__ = {"schema": "eguh_vest"}
    id = Column(Integer, primary_key=True, index=True)
    ficha_id = Column(Integer, ForeignKey("eguh_vest.fichas_producao.id", ondelete="CASCADE"))
    cor = Column(String(50), nullable=False)
    g1 = Column(Integer, default=0)
    g2 = Column(Integer, default=0)
    g3 = Column(Integer, default=0)
    ficha = relationship("FichaProducao", back_populates="itens")

Base.metadata.create_all(engine)

# Interface Tkinter
class FichaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📋 Ficha de Produção")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")  # Fundo claro

        # Aplicar tema moderno
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", padding=6, font=("Helvetica", 10))
        self.style.configure("TLabel", background="#f0f0f0", font=("Helvetica", 10))
        self.style.configure("TEntry", padding=5)
        self.style.configure("Treeview", rowheight=25, font=("Helvetica", 10))
        self.style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))

        # Container principal
        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Cabeçalho
        self.create_header_frame()

        # Itens
        self.items = []
        self.create_items_frame()

        # Formulário de itens
        self.create_item_form()

        # Botões de ação
        self.create_action_buttons()

    def create_header_frame(self):
        header_frame = tk.LabelFrame(self.main_frame, text="Cabeçalho", font=("Helvetica", 12, "bold"), bg="#f0f0f0", padx=10, pady=10)
        header_frame.pack(fill="x", pady=10)

        # Campos do cabeçalho
        fields = [
            ("Produto:", 40, "produto_entry"),
            ("Corte:", 10, "corte_entry"),
            ("Grade:", 20, "grade_entry"),
            ("Data (dd/mm/yyyy):", 12, "data_entry")
        ]

        for i, (label, width, attr_name) in enumerate(fields):
            tk.Label(header_frame, text=label, bg="#f0f0f0", font=("Helvetica", 10)).grid(row=0, column=i*2, sticky="w", padx=5)
            entry = ttk.Entry(header_frame, width=width, font=("Helvetica", 10))
            entry.grid(row=0, column=i*2+1, padx=5, pady=5)
            setattr(self, attr_name, entry)

        self.data_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))

    def create_items_frame(self):
        items_frame = tk.LabelFrame(self.main_frame, text="Itens (Cores e Tamanhos)", font=("Helvetica", 12, "bold"), bg="#f0f0f0", padx=10, pady=10)
        items_frame.pack(fill="both", expand=True, pady=10)

        self.tree = ttk.Treeview(items_frame, columns=("Cor", "G1", "G2", "G3", "Total"), show="headings")
        self.tree.heading("Cor", text="Cor")
        self.tree.heading("G1", text="G1")
        self.tree.heading("G2", text="G2")
        self.tree.heading("G3", text="G3")
        self.tree.heading("Total", text="Total")
        self.tree.column("Cor", width=200)
        self.tree.column("G1", width=80, anchor="center")
        self.tree.column("G2", width=80, anchor="center")
        self.tree.column("G3", width=80, anchor="center")
        self.tree.column("Total", width=100, anchor="center")
        self.tree.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(items_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Botão para remover item selecionado
        ttk.Button(items_frame, text="Remover Item", command=self.remover_item).pack(pady=5)

    def create_item_form(self):
        form_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        form_frame.pack(fill="x", pady=10)

        fields = [
            ("Cor:", 20, "cor_entry"),
            ("G1:", 5, "g1_entry"),
            ("G2:", 5, "g2_entry"),
            ("G3:", 5, "g3_entry")
        ]

        for i, (label, width, attr_name) in enumerate(fields):
            tk.Label(form_frame, text=label, bg="#f0f0f0", font=("Helvetica", 10)).grid(row=0, column=i*2, padx=5)
            entry = ttk.Entry(form_frame, width=width, font=("Helvetica", 10))
            entry.grid(row=0, column=i*2+1, padx=5)
            setattr(self, attr_name, entry)

        ttk.Button(form_frame, text="Adicionar Item", command=self.adicionar_item).grid(row=0, column=len(fields)*2, padx=10)

    def create_action_buttons(self):
        btn_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        btn_frame.pack(pady=10)

        buttons = [
            ("Salvar Ficha", self.salvar_ficha, "green"),
            ("Listar Fichas", self.listar_fichas, "blue"),
            ("Limpar Formulário", self.limpar_formulario, "gray")
        ]

        for text, command, bg in buttons:
            ttk.Button(btn_frame, text=text, command=command, style="TButton").pack(side="left", padx=10)
            self.style.configure(f"{text}.TButton", background=bg, foreground="white")

    def validate_date(self, date_str):
        try:
            return datetime.strptime(date_str, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("Data deve estar no formato dd/mm/yyyy")

    def validate_corte(self, corte_str):
        try:
            return int(corte_str)
        except ValueError:
            raise ValueError("Corte deve ser um número inteiro")

    def adicionar_item(self):
        cor = self.cor_entry.get().strip()
        try:
            g1 = int(self.g1_entry.get() or 0)
            g2 = int(self.g2_entry.get() or 0)
            g3 = int(self.g3_entry.get() or 0)
        except ValueError:
            messagebox.showerror("Erro", "G1, G2 e G3 devem ser números inteiros")
            return

        if not cor:
            messagebox.showerror("Erro", "O campo 'Cor' é obrigatório")
            return

        total = g1 + g2 + g3
        self.items.append((cor, g1, g2, g3, total))
        self.tree.insert("", "end", values=(cor, g1, g2, g3, total))

        self.cor_entry.delete(0, tk.END)
        self.g1_entry.delete(0, tk.END)
        self.g2_entry.delete(0, tk.END)
        self.g3_entry.delete(0, tk.END)

    def remover_item(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um item para remover")
            return

        item = self.tree.item(selection[0])["values"]
        self.items.remove(tuple(item))
        self.tree.delete(selection[0])

    def limpar_formulario(self):
        self.produto_entry.delete(0, tk.END)
        self.corte_entry.delete(0, tk.END)
        self.grade_entry.delete(0, tk.END)
        self.data_entry.delete(0, tk.END)
        self.data_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.tree.delete(*self.tree.get_children())
        self.items.clear()

    def salvar_ficha(self):
        produto = self.produto_entry.get().strip()
        corte = self.corte_entry.get().strip()
        grade = self.grade_entry.get().strip()
        data_str = self.data_entry.get().strip()

        if not (produto and corte and grade and data_str):
            messagebox.showwarning("Aviso", "Preencha todos os campos obrigatórios")
            return

        try:
            data = self.validate_date(data_str)
            corte = self.validate_corte(corte)
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
            return

        if not self.items:
            messagebox.showwarning("Aviso", "Adicione pelo menos um item à ficha")
            return

        try:
            with SessionLocal() as db:
                ficha = FichaProducao(produto=produto, corte=corte, grade=grade, data=data)
                db.add(ficha)
                db.commit()

                for cor, g1, g2, g3, _ in self.items:
                    novo_item = ItemFicha(ficha_id=ficha.id, cor=cor, g1=g1, g2=g2, g3=g3)
                    db.add(novo_item)

                db.commit()
                messagebox.showinfo("Sucesso", "Ficha salva com sucesso!")
                self.limpar_formulario()
        except Exception as e:
            logger.error(f"Erro ao salvar ficha: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar ficha: {e}")

    def listar_fichas(self):
        try:
            with SessionLocal() as db:
                fichas = db.query(FichaProducao).all()

                if not fichas:
                    messagebox.showinfo("Aviso", "Nenhuma ficha cadastrada")
                    return

                list_window = tk.Toplevel(self.root)
                list_window.title("📑 Fichas Cadastradas")
                list_window.geometry("900x500")
                list_window.configure(bg="#f0f0f0")

                tree = ttk.Treeview(list_window, columns=("ID", "Produto", "Corte", "Grade", "Data"), show="headings")
                tree.heading("ID", text="ID")
                tree.heading("Produto", text="Produto")
                tree.heading("Corte", text="Corte")
                tree.heading("Grade", text="Grade")
                tree.heading("Data", text="Data")
                tree.column("ID", width=50)
                tree.column("Produto", width=300)
                tree.column("Corte", width=80, anchor="center")
                tree.column("Grade", width=100)
                tree.column("Data", width=100)
                tree.pack(fill="both", expand=True, padx=20, pady=10)

                scrollbar = ttk.Scrollbar(list_window, orient="vertical", command=tree.yview)
                tree.configure(yscroll=scrollbar.set)
                scrollbar.pack(side="right", fill="y")

                for f in fichas:
                    tree.insert("", "end", values=(f.id, f.produto, f.corte, f.grade, f.data.strftime("%d/%m/%Y")))

                def apagar():
                    selection = tree.selection()
                    if not selection:
                        messagebox.showwarning("Aviso", "Selecione uma ficha para apagar")
                        return

                    ficha_id = tree.item(selection[0])["values"][0]
                    with SessionLocal() as db:
                        ficha = db.query(FichaProducao).filter(FichaProducao.id == ficha_id).first()
                        if messagebox.askyesno("Confirmação", f"Deseja apagar a ficha {ficha_id} - {ficha.produto}?"):
                            db.delete(ficha)
                            db.commit()
                            tree.delete(selection[0])
                            messagebox.showinfo("Sucesso", "Ficha apagada com sucesso!")

                def editar():
                    selection = tree.selection()
                    if not selection:
                        messagebox.showwarning("Aviso", "Selecione uma ficha para editar")
                        return

                    ficha_id = tree.item(selection[0])["values"][0]
                    with SessionLocal() as db:
                        ficha = db.query(FichaProducao).filter(FichaProducao.id == ficha_id).first()

                        edit_window = tk.Toplevel(list_window)
                        edit_window.title(f"Editar Ficha {ficha_id}")
                        edit_window.geometry("400x300")
                        edit_window.configure(bg="#f0f0f0")

                        fields = [
                            ("Produto:", 30, ficha.produto, "produto_entry"),
                            ("Corte:", 10, ficha.corte, "corte_entry"),
                            ("Grade:", 20, ficha.grade, "grade_entry"),
                            ("Data (dd/mm/yyyy):", 15, ficha.data.strftime("%d/%m/%Y"), "data_entry")
                        ]

                        for i, (label, width, value, attr_name) in enumerate(fields):
                            tk.Label(edit_window, text=label, bg="#f0f0f0", font=("Helvetica", 10)).grid(row=i, column=0, sticky="w", pady=5)
                            entry = ttk.Entry(edit_window, width=width, font=("Helvetica", 10))
                            entry.insert(0, value)
                            entry.grid(row=i, column=1, padx=5, pady=5)
                            setattr(edit_window, attr_name, entry)

                        def salvar_edicao():
                            try:
                                ficha.produto = edit_window.produto_entry.get().strip()
                                ficha.corte = self.validate_corte(edit_window.corte_entry.get().strip())
                                ficha.grade = edit_window.grade_entry.get().strip()
                                ficha.data = self.validate_date(edit_window.data_entry.get().strip())
                                db.commit()
                                tree.item(selection[0], values=(ficha.id, ficha.produto, ficha.corte, ficha.grade, ficha.data.strftime("%d/%m/%Y")))
                                messagebox.showinfo("Sucesso", "Ficha atualizada com sucesso!")
                                edit_window.destroy()
                            except Exception as e:
                                messagebox.showerror("Erro", f"Erro ao salvar: {e}")

                        ttk.Button(edit_window, text="Salvar", command=salvar_edicao, style="TButton").grid(row=len(fields), column=0, columnspan=2, pady=15)
                        self.style.configure("Salvar.TButton", background="green", foreground="white")

                btn_frame = tk.Frame(list_window, bg="#f0f0f0")
                btn_frame.pack(pady=10)

                buttons = [
                    ("Editar Ficha", editar, "orange"),
                    ("Apagar Ficha", apagar, "red"),
                    ("Fechar", list_window.destroy, "gray")
                ]

                for text, command, bg in buttons:
                    ttk.Button(btn_frame, text=text, command=command, style="TButton").pack(side="left", padx=10)
                    self.style.configure(f"{text}.TButton", background=bg, foreground="white")

        except Exception as e:
            logger.error(f"Erro ao listar fichas: {e}")
            messagebox.showerror("Erro", "Erro ao carregar fichas do banco de dados")

if __name__ == "__main__":
    root = tk.Tk()
    app = FichaApp(root)
    root.mainloop()
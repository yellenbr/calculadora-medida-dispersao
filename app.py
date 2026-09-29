import re
import tkinter as tk
from tkinter import ttk, messagebox

from calculos import (
    DadosInsuficientesError,
    Resultado,
    calcular_dados_brutos,
    calcular_tabela_frequencia_classes,
    calcular_tabela_frequencia_simples,
)

# Paleta e constantes visuais
COR_FUNDO = "#f4f6fb"
COR_FUNDO_CARD = "#ffffff"
COR_BORDA = "#e2e8f0"
COR_PRIMARIA = "#2f6fed"
COR_PRIMARIA_HOVER = "#2558c2"
COR_TEXTO = "#1e2433"
COR_TEXTO_SUAVE = "#5b6472"
COR_ERRO = "#d94f4f"
COR_SUCESSO = "#1f9d55"

FONTE_BASE = ("Segoe UI", 10)
FONTE_TITULO = ("Segoe UI", 17, "bold")
FONTE_SUBTITULO = ("Segoe UI", 10)
FONTE_SECAO = ("Segoe UI", 11, "bold")
FONTE_METRICA_ROTULO = ("Segoe UI", 9)
FONTE_METRICA_VALOR = ("Segoe UI", 16, "bold")


def botao_primario(master, text, command):
    return tk.Button(
        master,
        text=text,
        command=command,
        bg=COR_PRIMARIA,
        fg="white",
        activebackground=COR_PRIMARIA_HOVER,
        activeforeground="white",
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        borderwidth=0,
        padx=16,
        pady=8,
        cursor="hand2",
        highlightthickness=0,
    )


# Widgets reutilizáveis
class CartaoMetrica(ttk.Frame):

    def __init__(self, master, titulo: str, **kwargs):
        super().__init__(master, style="Card.TFrame", padding=(16, 12), **kwargs)
        self.columnconfigure(0, weight=1)

        self._titulo = ttk.Label(self, text=titulo, style="MetricaRotulo.TLabel")
        self._titulo.grid(row=0, column=0, sticky="w")

        self._valor = ttk.Label(self, text="—", style="MetricaValor.TLabel")
        self._valor.grid(row=1, column=0, sticky="w", pady=(4, 0))

    def definir_valor(self, texto: str):
        self._valor.configure(text=texto)

    def limpar(self):
        self._valor.configure(text="—")


class PainelResultados(ttk.Frame):

    def __init__(self, master, **kwargs):
        kwargs.setdefault("padding", 16)
        super().__init__(master, style="Painel.TFrame", **kwargs)
        self.columnconfigure((0, 1), weight=1, uniform="col")

        titulo = ttk.Label(self, text="Resultados", style="Secao.TLabel")
        titulo.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        self.cartao_amplitude = CartaoMetrica(self, "Amplitude total")
        self.cartao_amplitude.grid(row=1, column=0, sticky="nsew", padx=(0, 8), pady=6)

        self.cartao_variancia = CartaoMetrica(self, "Variância")
        self.cartao_variancia.grid(row=1, column=1, sticky="nsew", padx=(8, 0), pady=6)

        self.cartao_desvio = CartaoMetrica(self, "Desvio padrão")
        self.cartao_desvio.grid(row=2, column=0, sticky="nsew", padx=(0, 8), pady=6)

        self.cartao_cv = CartaoMetrica(self, "Coeficiente de variação")
        self.cartao_cv.grid(row=2, column=1, sticky="nsew", padx=(8, 0), pady=6)

        self.rodape = ttk.Label(self, text="", style="Rodape.TLabel")
        self.rodape.grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 0))

    def atualizar(self, resultado: Resultado, amostral: bool):
        self.cartao_amplitude.definir_valor(f"{resultado.amplitude_total:.4f}")
        self.cartao_variancia.definir_valor(f"{resultado.variancia:.4f}")
        self.cartao_desvio.definir_valor(f"{resultado.desvio_padrao:.4f}")
        cv_texto = "indefinido" if resultado.coeficiente_variacao != resultado.coeficiente_variacao else f"{resultado.coeficiente_variacao:.2f}%"
        self.cartao_cv.definir_valor(cv_texto)
        tipo = "amostral" if amostral else "populacional"
        self.rodape.configure(
            text=f"n = {resultado.n}   •   média = {resultado.media:.4f}   •   variância {tipo}"
        )

    def limpar(self):
        for cartao in (self.cartao_amplitude, self.cartao_variancia, self.cartao_desvio, self.cartao_cv):
            cartao.limpar()
        self.rodape.configure(text="")


class TabelaEditavel(ttk.Frame):

    def __init__(self, master, colunas, linhas_iniciais=3, **kwargs):
        super().__init__(master, **kwargs)
        self.colunas = colunas
        self.linhas = []

        self.columnconfigure(len(colunas), weight=0)

        self._cabecalho = ttk.Frame(self)
        self._cabecalho.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        for idx, (_, rotulo, largura) in enumerate(colunas):
            lbl = ttk.Label(self._cabecalho, text=rotulo, style="CabecalhoTabela.TLabel", width=largura, anchor="w")
            lbl.grid(row=0, column=idx, padx=(0, 8))

        self._corpo = ttk.Frame(self)
        self._corpo.grid(row=1, column=0, sticky="ew")

        botoes = ttk.Frame(self)
        botoes.grid(row=2, column=0, sticky="w", pady=(8, 0))
        ttk.Button(botoes, text="+ Adicionar linha", style="Secundario.TButton", command=self.adicionar_linha).grid(row=0, column=0, padx=(0, 6))
        ttk.Button(botoes, text="Remover última", style="Secundario.TButton", command=self.remover_linha).grid(row=0, column=1)

        for _ in range(linhas_iniciais):
            self.adicionar_linha()

    def adicionar_linha(self):
        idx = len(self.linhas)
        entradas = []
        for c, (_, _, largura) in enumerate(self.colunas):
            var = tk.StringVar()
            ent = ttk.Entry(self._corpo, textvariable=var, width=largura, font=FONTE_BASE)
            ent.grid(row=idx, column=c, padx=(0, 8), pady=3)
            entradas.append(var)
        self.linhas.append(entradas)

    def remover_linha(self):
        if len(self.linhas) <= 1:
            return
        entradas = self.linhas.pop()
        for widget in self._corpo.grid_slaves(row=len(self.linhas)):
            widget.destroy()

    def limpar(self):
        for entradas in self.linhas:
            for var in entradas:
                var.set("")

    def valores(self):
    
        resultado = []
        for entradas in self.linhas:
            textos = [var.get().strip() for var in entradas]
            if all(t == "" for t in textos):
                continue
            if any(t == "" for t in textos):
                raise ValueError("Preencha todas as colunas da linha ou deixe a linha totalmente vazia.")
            resultado.append(tuple(float(t.replace(",", ".")) for t in textos))
        return resultado

# Abas

class AbaDadosBrutos(ttk.Frame):
    def __init__(self, master, on_status, on_resultado, on_limpar):
        super().__init__(master, style="Fundo.TFrame", padding=20)
        self.on_status = on_status
        self.on_resultado = on_resultado
        self.on_limpar = on_limpar
        self.columnconfigure(0, weight=1)

        instrucao = ttk.Label(
            self,
            text="Digite os valores separados por espaço, vírgula ou quebra de linha. Use ponto (.) para casas decimais.",
            style="Instrucao.TLabel",
            wraplength=560,
        )
        instrucao.grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.texto = tk.Text(self, height=6, font=FONTE_BASE, wrap="word", relief="solid", borderwidth=1,
                              highlightthickness=1, highlightbackground=COR_BORDA, highlightcolor=COR_PRIMARIA)
        self.texto.grid(row=1, column=0, sticky="ew")
        self.texto.insert("1.0", "2, 4, 4, 4, 5, 5, 7, 9")

        exemplo = ttk.Label(self, text="Exemplo acima — substitua pelos seus próprios dados.", style="Dica.TLabel")
        exemplo.grid(row=2, column=0, sticky="w", pady=(4, 16))

        opcoes = ttk.Frame(self, style="Fundo.TFrame")
        opcoes.grid(row=3, column=0, sticky="w", pady=(0, 16))
        ttk.Label(opcoes, text="Tipo de variância:", style="Instrucao.TLabel").grid(row=0, column=0, padx=(0, 10))
        self.var_amostral = tk.BooleanVar(value=False)
        ttk.Radiobutton(opcoes, text="Populacional (÷ n)", value=False, variable=self.var_amostral, style="TRadiobutton").grid(row=0, column=1, padx=(0, 10))
        ttk.Radiobutton(opcoes, text="Amostral (÷ n-1)", value=True, variable=self.var_amostral, style="TRadiobutton").grid(row=0, column=2)

        acoes = ttk.Frame(self, style="Fundo.TFrame")
        acoes.grid(row=4, column=0, sticky="w")
        botao_primario(acoes, "Calcular", self.calcular).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(acoes, text="Limpar", style="Secundario.TButton", command=self.limpar).grid(row=0, column=1)

    def calcular(self):
        bruto = self.texto.get("1.0", "end").strip()
        if not bruto:
            self.on_status("Informe ao menos um valor.", erro=True)
            return
        try:
            tokens = [t for t in re.split(r"[\s,;]+", bruto.strip()) if t]
            valores = [float(t) for t in tokens]
            resultado = calcular_dados_brutos(valores, self.var_amostral.get())
        except (ValueError, DadosInsuficientesError) as exc:
            self.on_status(f"Erro: {exc}", erro=True)
            return
        self.on_status("Cálculo realizado com sucesso.", erro=False)
        self.on_resultado(resultado, self.var_amostral.get())

    def limpar(self):
        self.texto.delete("1.0", "end")
        self.on_status("", erro=False)
        self.on_limpar()


class AbaTabelaFrequencia(ttk.Frame):
    def __init__(self, master, on_status, on_resultado, on_limpar):
        super().__init__(master, style="Fundo.TFrame", padding=20)
        self.on_status = on_status
        self.on_resultado = on_resultado
        self.on_limpar = on_limpar
        self.columnconfigure(0, weight=1)

        self.modo = tk.StringVar(value="simples")
        seletor = ttk.Frame(self, style="Fundo.TFrame")
        seletor.grid(row=0, column=0, sticky="w", pady=(0, 12))
        ttk.Label(seletor, text="Tipo de tabela:", style="Instrucao.TLabel").grid(row=0, column=0, padx=(0, 10))
        ttk.Radiobutton(seletor, text="Frequência simples (valor / f)", value="simples", variable=self.modo,
                         style="TRadiobutton", command=self._alternar_modo).grid(row=0, column=1, padx=(0, 10))
        ttk.Radiobutton(seletor, text="Frequência em classes (Li / Ls / f)", value="classes", variable=self.modo,
                         style="TRadiobutton", command=self._alternar_modo).grid(row=0, column=2)

        self.container_tabelas = ttk.Frame(self, style="Fundo.TFrame")
        self.container_tabelas.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        self.tabela_simples = TabelaEditavel(
            self.container_tabelas,
            colunas=[("x", "Valor (x)", 12), ("f", "Frequência (f)", 12)],
        )
        self.tabela_classes = TabelaEditavel(
            self.container_tabelas,
            colunas=[("li", "Limite inferior", 12), ("ls", "Limite superior", 12), ("f", "Frequência (f)", 12)],
        )
        self.tabela_simples.grid(row=0, column=0, sticky="ew")
        self.tabela_classes.grid(row=0, column=0, sticky="ew")
        self._alternar_modo()

        opcoes = ttk.Frame(self, style="Fundo.TFrame")
        opcoes.grid(row=2, column=0, sticky="w", pady=(4, 16))
        ttk.Label(opcoes, text="Tipo de variância:", style="Instrucao.TLabel").grid(row=0, column=0, padx=(0, 10))
        self.var_amostral = tk.BooleanVar(value=False)
        ttk.Radiobutton(opcoes, text="Populacional (÷ n)", value=False, variable=self.var_amostral, style="TRadiobutton").grid(row=0, column=1, padx=(0, 10))
        ttk.Radiobutton(opcoes, text="Amostral (÷ n-1)", value=True, variable=self.var_amostral, style="TRadiobutton").grid(row=0, column=2)

        acoes = ttk.Frame(self, style="Fundo.TFrame")
        acoes.grid(row=3, column=0, sticky="w")
        botao_primario(acoes, "Calcular", self.calcular).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(acoes, text="Limpar", style="Secundario.TButton", command=self.limpar).grid(row=0, column=1)

    def _alternar_modo(self):
        if self.modo.get() == "simples":
            self.tabela_classes.grid_remove()
            self.tabela_simples.grid()
        else:
            self.tabela_simples.grid_remove()
            self.tabela_classes.grid()

    def calcular(self):
        try:
            if self.modo.get() == "simples":
                linhas = self.tabela_simples.valores()
                if not linhas:
                    raise ValueError("Preencha ao menos uma linha da tabela.")
                valores = [l[0] for l in linhas]
                frequencias = [l[1] for l in linhas]
                resultado = calcular_tabela_frequencia_simples(valores, frequencias, self.var_amostral.get())
            else:
                linhas = self.tabela_classes.valores()
                if not linhas:
                    raise ValueError("Preencha ao menos uma linha da tabela.")
                lis = [l[0] for l in linhas]
                lss = [l[1] for l in linhas]
                frequencias = [l[2] for l in linhas]
                for li, ls in zip(lis, lss):
                    if ls <= li:
                        raise ValueError("O limite superior deve ser maior que o limite inferior em cada classe.")
                resultado = calcular_tabela_frequencia_classes(lis, lss, frequencias, self.var_amostral.get())
        except (ValueError, DadosInsuficientesError) as exc:
            self.on_status(f"Erro: {exc}", erro=True)
            return
        self.on_status("Cálculo realizado com sucesso.", erro=False)
        self.on_resultado(resultado, self.var_amostral.get())

    def limpar(self):
        self.tabela_simples.limpar()
        self.tabela_classes.limpar()
        self.on_status("", erro=False)
        self.on_limpar()



# Aplicação principal
class Aplicativo(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculadora de Medidas de Dispersão")
        self.geometry("760x760")
        self.minsize(680, 640)
        self.configure(bg=COR_FUNDO)

        self._configurar_estilos()
        self._montar_layout()

    # -- estilos ------------------------------------------------------
    def _configurar_estilos(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Fundo.TFrame", background=COR_FUNDO)
        style.configure("Painel.TFrame", background=COR_FUNDO)
        style.configure("Card.TFrame", background=COR_FUNDO_CARD, relief="flat", borderwidth=1)
        style.configure("TFrame", background=COR_FUNDO)

        style.configure("Titulo.TLabel", background=COR_FUNDO, foreground=COR_TEXTO, font=FONTE_TITULO)
        style.configure("Subtitulo.TLabel", background=COR_FUNDO, foreground=COR_TEXTO_SUAVE, font=FONTE_SUBTITULO)
        style.configure("Secao.TLabel", background=COR_FUNDO, foreground=COR_TEXTO, font=FONTE_SECAO)
        style.configure("Instrucao.TLabel", background=COR_FUNDO, foreground=COR_TEXTO, font=FONTE_BASE)
        style.configure("Dica.TLabel", background=COR_FUNDO, foreground=COR_TEXTO_SUAVE, font=("Segoe UI", 8, "italic"))
        style.configure("CabecalhoTabela.TLabel", background=COR_FUNDO, foreground=COR_TEXTO_SUAVE, font=("Segoe UI", 9, "bold"))
        style.configure("MetricaRotulo.TLabel", background=COR_FUNDO_CARD, foreground=COR_TEXTO_SUAVE, font=FONTE_METRICA_ROTULO)
        style.configure("MetricaValor.TLabel", background=COR_FUNDO_CARD, foreground=COR_PRIMARIA, font=FONTE_METRICA_VALOR)
        style.configure("Rodape.TLabel", background=COR_FUNDO, foreground=COR_TEXTO_SUAVE, font=("Segoe UI", 9))
        style.configure("StatusOk.TLabel", background=COR_FUNDO, foreground=COR_SUCESSO, font=("Segoe UI", 9, "bold"))
        style.configure("StatusErro.TLabel", background=COR_FUNDO, foreground=COR_ERRO, font=("Segoe UI", 9, "bold"))

        style.configure("TRadiobutton", background=COR_FUNDO, foreground=COR_TEXTO, font=FONTE_BASE)
        style.map("TRadiobutton", background=[("active", COR_FUNDO)])

        style.configure("TNotebook", background=COR_FUNDO, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(16, 8), font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", COR_FUNDO_CARD)], foreground=[("selected", COR_PRIMARIA)])

        style.configure("Secundario.TButton", background=COR_FUNDO_CARD, foreground=COR_TEXTO, font=FONTE_BASE,
                        padding=(12, 6), borderwidth=1, relief="solid")
        style.map("Secundario.TButton", background=[("active", "#eef2f9")])

    # -- layout ---------------------------------------------------------
    def _montar_layout(self):
        cabecalho = ttk.Frame(self, style="Fundo.TFrame", padding=(24, 20, 24, 8))
        cabecalho.pack(fill="x")
        ttk.Label(cabecalho, text="Medidas de Dispersão", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(
            cabecalho,
            text="Calcule amplitude total, variância, desvio padrão e coeficiente de variação.",
            style="Subtitulo.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        corpo = ttk.Frame(self, style="Fundo.TFrame", padding=(24, 0, 24, 0))
        corpo.pack(fill="both", expand=True)
        corpo.columnconfigure(0, weight=1)
        corpo.rowconfigure(0, weight=0)
        corpo.rowconfigure(1, weight=1)

        self.notebook = ttk.Notebook(corpo)
        self.notebook.grid(row=0, column=0, sticky="nsew", pady=(0, 16))

        self.aba_brutos = AbaDadosBrutos(
            self.notebook, self._definir_status, self.exibir_resultado, self.limpar_resultado
        )
        self.aba_tabela = AbaTabelaFrequencia(
            self.notebook, self._definir_status, self.exibir_resultado, self.limpar_resultado
        )
        self.notebook.add(self.aba_brutos, text="  Dados Brutos  ")
        self.notebook.add(self.aba_tabela, text="  Tabela de Frequência  ")

        self.status_label = ttk.Label(corpo, text="", style="StatusOk.TLabel")
        self.status_label.grid(row=1, column=0, sticky="w")

        self.painel_resultados = PainelResultados(self, padding=(24, 8, 24, 20))
        self.painel_resultados.pack(fill="x", side="bottom")

    # -- callbacks --------------------------------------------------------
    def _definir_status(self, texto: str, erro: bool):
        self.status_label.configure(text=texto, style="StatusErro.TLabel" if erro else "StatusOk.TLabel")

    def exibir_resultado(self, resultado: Resultado, amostral: bool):
        self.painel_resultados.atualizar(resultado, amostral)

    def limpar_resultado(self):
        self.painel_resultados.limpar()


def main():
    app = Aplicativo()
    app.mainloop()


if __name__ == "__main__":
    main()

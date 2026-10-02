# Calculadora de Medidas de Dispersão

Aplicativo de desktop em Python que calcula as principais medidas de dispersão
estatística, tanto para dados brutos quanto para dados organizados em tabela
de frequência.

## Medidas calculadas

- Amplitude total
- Variância (populacional ou amostral)
- Desvio padrão
- Coeficiente de variação

## Modos de entrada

- **Dados brutos**: lista de valores digitados separados por espaço, vírgula,
  ponto e vírgula ou quebra de linha.
- **Tabela de frequência simples**: pares valor (x) / frequência (f).
- **Tabela de frequência em classes**: limite inferior, limite superior e
  frequência de cada classe (o cálculo usa o ponto médio de cada classe).

## Requisitos

- Python 3.8+
- Tkinter (já vem com o Python na maioria dos sistemas; no Ubuntu/Debian,
  instale com `sudo apt-get install python3-tk` caso não esteja disponível)

## Como executar localmente

```bash
python3 app.py
```

O comando acima abre a versão desktop em Tkinter. Para executar a versão web
localmente, instale as dependências e inicie o servidor Flask:

```bash
python3 -m pip install -r requirements.txt
flask --app api.index run --debug
```

Depois, acesse `http://127.0.0.1:5000` no navegador.

## Publicar na Vercel

A Vercel não executa janelas Tkinter. A versão web usa `api/index.py`, que já
está configurada em `vercel.json`. Na Vercel, importe este repositório como um
novo projeto e mantenha o diretório raiz na pasta do projeto. O build instalará
automaticamente `requirements.txt`; não é necessário configurar um comando de
build ou iniciar `app.py`.

## Estrutura do projeto

- `calculos.py` — funções puras de cálculo estatístico (sem dependência de UI).
- `app.py` — interface gráfica em Tkinter/ttk.
- `api/index.py` — interface web Flask compatível com Vercel.
- `vercel.json` — roteamento da aplicação web para a função Python.

## Observações sobre a variância

- **Populacional** (÷ n): use quando os dados representam a população completa.
- **Amostral** (÷ n-1): use quando os dados são uma amostra de uma população maior.

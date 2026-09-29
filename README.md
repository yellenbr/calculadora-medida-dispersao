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

## Como executar

```bash
python3 app.py
```

## Estrutura do projeto

- `calculos.py` — funções puras de cálculo estatístico (sem dependência de UI).
- `app.py` — interface gráfica em Tkinter/ttk.

## Observações sobre a variância

- **Populacional** (÷ n): use quando os dados representam a população completa.
- **Amostral** (÷ n-1): use quando os dados são uma amostra de uma população maior.

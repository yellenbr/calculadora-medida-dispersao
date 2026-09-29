from dataclasses import dataclass
from typing import Sequence


class DadosInsuficientesError(ValueError):
    pass


@dataclass
class Resultado:
    n: int
    media: float
    amplitude_total: float
    variancia: float
    desvio_padrao: float
    coeficiente_variacao: float


def _validar_nao_vazio(valores: Sequence[float]) -> None:
    if not valores:
        raise DadosInsuficientesError("Informe ao menos um valor.")


def calcular_dados_brutos(dados: Sequence[float], amostral: bool) -> Resultado:
    _validar_nao_vazio(dados)
    n = len(dados)
    media = sum(dados) / n
    amplitude = max(dados) - min(dados)
    soma_quadrados = sum((x - media) ** 2 for x in dados)
    divisor = (n - 1) if amostral and n > 1 else n
    variancia = soma_quadrados / divisor
    desvio = variancia ** 0.5
    cv = (desvio / media * 100) if media != 0 else float("nan")
    return Resultado(n, media, amplitude, variancia, desvio, cv)


def calcular_tabela_frequencia_simples(
    valores: Sequence[float], frequencias: Sequence[float], amostral: bool
) -> Resultado:
    _validar_nao_vazio(valores)
    if len(valores) != len(frequencias):
        raise ValueError("Valores e frequências devem ter a mesma quantidade de linhas.")
    n = sum(frequencias)
    if n <= 0:
        raise DadosInsuficientesError("A soma das frequências deve ser maior que zero.")
    media = sum(x * f for x, f in zip(valores, frequencias)) / n
    amplitude = max(valores) - min(valores)
    soma_quadrados = sum(f * (x - media) ** 2 for x, f in zip(valores, frequencias))
    divisor = (n - 1) if amostral and n > 1 else n
    variancia = soma_quadrados / divisor
    desvio = variancia ** 0.5
    cv = (desvio / media * 100) if media != 0 else float("nan")
    return Resultado(int(n), media, amplitude, variancia, desvio, cv)


def calcular_tabela_frequencia_classes(
    limites_inferiores: Sequence[float],
    limites_superiores: Sequence[float],
    frequencias: Sequence[float],
    amostral: bool,
) -> Resultado:
    _validar_nao_vazio(limites_inferiores)
    if not (len(limites_inferiores) == len(limites_superiores) == len(frequencias)):
        raise ValueError("Limites inferiores, superiores e frequências devem ter a mesma quantidade de linhas.")
    pontos_medios = [(li + ls) / 2 for li, ls in zip(limites_inferiores, limites_superiores)]
    resultado = calcular_tabela_frequencia_simples(pontos_medios, frequencias, amostral)
    amplitude = max(limites_superiores) - min(limites_inferiores)
    resultado.amplitude_total = amplitude
    return resultado

"""Tests para ObservationsExtractor."""

import logging

import pytest

from purchase_toolkit.extract.observations import ObservationsExtractor


def test_extract_basic_example() -> None:
    text = """
| TIPO_OC=ABONO | FECHA_ABONO=2026-07 |
| PRESUPUESTO=1234 |
"""
    extractor = ObservationsExtractor()
    result = extractor.extract(text)

    assert result == {
        "TIPO_OC": "ABONO",
        "FECHA_ABONO": "2026-07",
        "PRESUPUESTO": "1234",
    }


def test_extract_dynamic_currency_key() -> None:
    text = "| TC_USD_ARS=1250,50 | TC_FECHA=2026-08-01 | TC_FUENTE=BNA |"

    extractor = ObservationsExtractor()
    result = extractor.extract(text)

    assert result == {
        "TC_USD_ARS": "1250,50",
        "TC_FECHA": "2026-08-01",
        "TC_FUENTE": "BNA",
    }


def test_extract_with_custom_separators() -> None:
    text = "; TIPO_OC:ABONO ; FECHA_ABONO:2026-07 ;"

    extractor = ObservationsExtractor(field_separator=";", key_value_separator=":")
    result = extractor.extract(text)

    assert result == {"TIPO_OC": "ABONO", "FECHA_ABONO": "2026-07"}


def test_extract_ignores_fragment_without_separator(
    caplog: pytest.LogCaptureFixture,
) -> None:
    text = "| TIPO_OC=ABONO | texto_sin_formato |"

    extractor = ObservationsExtractor()
    with caplog.at_level(logging.WARNING):
        result = extractor.extract(text)

    assert result == {"TIPO_OC": "ABONO"}
    assert "texto_sin_formato" in caplog.text


def test_extract_keeps_last_value_on_duplicate_key(
    caplog: pytest.LogCaptureFixture,
) -> None:
    text = """
| PRESUPUESTO=1111 |
| PRESUPUESTO=2222 |
"""
    extractor = ObservationsExtractor()
    with caplog.at_level(logging.WARNING):
        result = extractor.extract(text)

    assert result == {"PRESUPUESTO": "2222"}
    assert "PRESUPUESTO" in caplog.text


def test_extract_empty_text_returns_empty_dict() -> None:
    extractor = ObservationsExtractor()
    result = extractor.extract("\n\n")

    assert result == {}


def test_extract_strips_surrounding_whitespace() -> None:
    text = "|   TIPO_OC   =   ABONO   |"

    extractor = ObservationsExtractor()
    result = extractor.extract(text)

    assert result == {"TIPO_OC": "ABONO"}

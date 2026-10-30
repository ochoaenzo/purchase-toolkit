"""Tests para PurchaseOrderObservationsExtractor."""

from pathlib import Path

import pytest
from pypdf import PdfWriter

from purchase_toolkit.extract import purchase_order_pdf
from purchase_toolkit.extract.purchase_order_pdf import (
    PurchaseOrderObservationsExtractor,
)


def _make_pdf(path: Path) -> None:
    """Genera un PDF sintético de una página en blanco."""
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    with path.open("wb") as f:
        writer.write(f)


def test_get_order_number_matches_base_order_file() -> None:
    extractor = PurchaseOrderObservationsExtractor()
    assert extractor.get_order_number("10001.pdf") == "10001"
    assert extractor.get_order_number("10001.PDF") == "10001"


@pytest.mark.parametrize(
    "filename",
    ["10001_auth.pdf", "10001_ppto.pdf", "100011.pdf", "notas.pdf"],
)
def test_get_order_number_ignores_non_order_files(filename: str) -> None:
    extractor = PurchaseOrderObservationsExtractor()
    assert extractor.get_order_number(filename) is None


def test_get_order_number_with_custom_pattern() -> None:
    extractor = PurchaseOrderObservationsExtractor(
        order_number_pattern=r"^OC_(\d{5})\.pdf$"
    )
    assert extractor.get_order_number("OC_10001.pdf") == "10001"
    assert extractor.get_order_number("10001.pdf") is None


def test_extract_from_folder_only_processes_order_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for name in ["10001.pdf", "10001_auth.pdf", "10002.pdf", "notas.pdf"]:
        _make_pdf(tmp_path / name)

    read_files: list[str] = []

    def fake_read_pdf_text(pdf_path: Path) -> str:
        read_files.append(pdf_path.name)
        return f"Razón social\n| ARCHIVO={pdf_path.stem} |\nTotal"

    monkeypatch.setattr(purchase_order_pdf, "read_pdf_text", fake_read_pdf_text)

    extractor = PurchaseOrderObservationsExtractor()
    result = extractor.extract_from_folder(tmp_path)

    assert result == {
        "10001": {"ARCHIVO": "10001"},
        "10002": {"ARCHIVO": "10002"},
    }
    assert sorted(read_files) == ["10001.pdf", "10002.pdf"]


def test_extract_from_folder_raises_when_folder_missing(tmp_path: Path) -> None:
    extractor = PurchaseOrderObservationsExtractor()
    with pytest.raises(FileNotFoundError):
        extractor.extract_from_folder(tmp_path / "no_existe")


def test_find_observations_text_keeps_only_observation_lines() -> None:
    pdf_text = "Razón social\n| TIPO_OC=ABONO | PRESUPUESTO=1234 |\nTotal: 1.000"

    extractor = PurchaseOrderObservationsExtractor()

    assert extractor.find_observations_text(pdf_text) == (
        "| TIPO_OC=ABONO | PRESUPUESTO=1234 |"
    )


def test_find_observations_text_with_custom_field_separator() -> None:
    pdf_text = "Razón social\n; TIPO_OC:ABONO ; FECHA_ABONO:2026-07 ;\nTotal"

    extractor = PurchaseOrderObservationsExtractor(
        field_separator=";", key_value_separator=":"
    )

    assert extractor.find_observations_text(pdf_text) == (
        "; TIPO_OC:ABONO ; FECHA_ABONO:2026-07 ;"
    )


def test_find_observations_text_ignores_default_separator_when_customized() -> None:
    pdf_text = "| TIPO_OC=ABONO |"

    extractor = PurchaseOrderObservationsExtractor(field_separator=";")

    assert extractor.find_observations_text(pdf_text) == ""

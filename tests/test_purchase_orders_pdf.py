"""Tests para PurchaseOrderPdfMerger."""

import logging
from pathlib import Path

import pytest
from pypdf import PdfReader, PdfWriter

from purchase_toolkit.merge.purchase_orders_pdf import PurchaseOrderPdfMerger


def _make_pdf(path: Path, num_pages: int = 1, page_size: tuple[int, int] = (200, 200)) -> None:
    """Genera un PDF sintético con la cantidad de páginas y tamaño indicados."""
    writer = PdfWriter()
    width, height = page_size
    for _ in range(num_pages):
        writer.add_blank_page(width=width, height=height)
    with path.open("wb") as f:
        writer.write(f)


def test_get_order_number_matches_default_pattern() -> None:
    merger = PurchaseOrderPdfMerger()
    assert merger.get_order_number("10001_auth.pdf") == "10001"


def test_get_order_number_returns_none_when_no_match() -> None:
    merger = PurchaseOrderPdfMerger()
    assert merger.get_order_number("sin_numero.pdf") is None


def test_get_order_number_with_custom_pattern() -> None:
    merger = PurchaseOrderPdfMerger(order_number_pattern=r"^([A-Z]{2}\d{3})")
    assert merger.get_order_number("AT502_ppto.pdf") == "AT502"


def test_merge_raises_when_source_folder_missing(tmp_path: Path) -> None:
    merger = PurchaseOrderPdfMerger()
    missing_source = tmp_path / "no_existe"
    destination = tmp_path / "salida"

    with pytest.raises(FileNotFoundError):
        merger.merge(missing_source, destination)


def test_merge_creates_destination_folder(tmp_path: Path) -> None:
    source = tmp_path / "entrada"
    source.mkdir()
    destination = tmp_path / "salida" / "anidada"

    merger = PurchaseOrderPdfMerger()
    merger.merge(source, destination)

    assert destination.exists()


def test_merge_groups_files_by_order_number(tmp_path: Path) -> None:
    source = tmp_path / "entrada"
    source.mkdir()
    destination = tmp_path / "salida"

    _make_pdf(source / "10001.pdf")
    _make_pdf(source / "10001_auth.pdf")
    _make_pdf(source / "10002.pdf")

    merger = PurchaseOrderPdfMerger()
    merger.merge(source, destination)

    assert (destination / "10001.pdf").exists()
    assert (destination / "10002.pdf").exists()

    merged_10001 = PdfReader(destination / "10001.pdf")
    assert len(merged_10001.pages) == 2

    merged_10002 = PdfReader(destination / "10002.pdf")
    assert len(merged_10002.pages) == 1


def test_merge_orders_base_file_first(tmp_path: Path) -> None:
    source = tmp_path / "entrada"
    source.mkdir()
    destination = tmp_path / "salida"

    # Archivo base con un tamaño de página distinto al de respaldo,
    # para poder verificar cuál quedó primero en el PDF combinado.
    _make_pdf(source / "10001.pdf", page_size=(100, 100))
    _make_pdf(source / "10001_auth.pdf", page_size=(300, 300))

    merger = PurchaseOrderPdfMerger()
    merger.merge(source, destination)

    merged = PdfReader(destination / "10001.pdf")
    first_page_width = merged.pages[0].mediabox.width
    second_page_width = merged.pages[1].mediabox.width

    assert first_page_width == 100
    assert second_page_width == 300


def test_merge_ignores_files_not_matching_pattern(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    source = tmp_path / "entrada"
    source.mkdir()
    destination = tmp_path / "salida"

    _make_pdf(source / "10001.pdf")
    _make_pdf(source / "sin_numero_de_orden.pdf")

    merger = PurchaseOrderPdfMerger()
    with caplog.at_level(logging.DEBUG):
        merger.merge(source, destination)

    assert (destination / "10001.pdf").exists()
    assert not (destination / "sin_numero_de_orden.pdf").exists()
    assert "sin_numero_de_orden.pdf" in caplog.text
    assert "1 archivo(s) ignorados" in caplog.text
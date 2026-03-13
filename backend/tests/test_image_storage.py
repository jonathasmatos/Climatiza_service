import io

from PIL import Image
from starlette.datastructures import Headers, UploadFile

from app.services.image_storage import processar_upload_foto


def _upload_png(filename: str = "foto.png") -> UploadFile:
    buf = io.BytesIO()
    img = Image.new("RGB", (800, 600), color=(20, 140, 220))
    img.save(buf, format="PNG")
    buf.seek(0)
    headers = Headers({"content-type": "image/png"})
    return UploadFile(file=buf, filename=filename, headers=headers)


def test_processar_upload_gera_original_e_thumb(monkeypatch, tmp_path, db_session, ordem_basica, admin_user):
    monkeypatch.setenv("IMAGE_STORAGE_ROOT", str(tmp_path / "storage"))

    foto = processar_upload_foto(
        db=db_session,
        ordem_servico_id=ordem_basica.id,
        upload=_upload_png(),
        categoria="ANTES",
        descricao="foto de teste",
        foto_principal=False,
        criado_por_usuario=admin_user.id,
    )

    assert foto.url_arquivo.endswith(".webp")
    assert foto.url_thumb.endswith("_thumb.webp")
    assert foto.mime_type == "image/webp"
    assert foto.tamanho_bytes > 0
    assert foto.hash_sha256


def test_processar_upload_marca_duplicidade(monkeypatch, tmp_path, db_session, ordem_basica, admin_user):
    monkeypatch.setenv("IMAGE_STORAGE_ROOT", str(tmp_path / "storage"))

    primeira = processar_upload_foto(
        db=db_session,
        ordem_servico_id=ordem_basica.id,
        upload=_upload_png("primeira.png"),
        categoria="ANTES",
        descricao=None,
        foto_principal=False,
        criado_por_usuario=admin_user.id,
    )

    segunda = processar_upload_foto(
        db=db_session,
        ordem_servico_id=ordem_basica.id,
        upload=_upload_png("segunda.png"),
        categoria="ANTES",
        descricao=None,
        foto_principal=False,
        criado_por_usuario=admin_user.id,
    )

    assert segunda.duplicada_de_foto_id == primeira.id

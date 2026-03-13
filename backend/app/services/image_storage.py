import hashlib
import uuid
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

from fastapi import HTTPException, UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import OSFoto, OrdemServico

_ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}


def _normalize_categoria(categoria: str) -> str:
    return categoria.strip().lower()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _resize_to_width(img: Image.Image, width: int) -> Image.Image:
    if img.width <= width:
        return img
    ratio = width / float(img.width)
    height = int(img.height * ratio)
    return img.resize((width, height), Image.Resampling.LANCZOS)


def _save_webp_atomic(img: Image.Image, final_path: Path, quality: int = 80) -> None:
    final_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = final_path.with_suffix(final_path.suffix + f".{uuid.uuid4().hex}.tmp")
    img.save(temp_path, format="WEBP", quality=quality, method=6)
    temp_path.replace(final_path)


def processar_upload_foto(
    *,
    db: Session,
    ordem_servico_id,
    upload: UploadFile,
    categoria: str,
    descricao: str | None,
    foto_principal: bool,
    criado_por_usuario: int | None,
) -> OSFoto:
    settings = get_settings()

    os = db.get(OrdemServico, ordem_servico_id)
    if not os:
        raise HTTPException(404, "OS não encontrada")

    total_fotos = db.query(OSFoto).filter(OSFoto.ordem_servico_id == ordem_servico_id).count()
    if total_fotos >= settings.IMAGE_MAX_PER_OS:
        raise HTTPException(422, f"A OS já atingiu o limite de {settings.IMAGE_MAX_PER_OS} fotos")

    content_type = (upload.content_type or "").lower().strip()
    if content_type not in _ALLOWED_MIME_TYPES:
        raise HTTPException(422, "Tipo de arquivo inválido. Use jpeg, png ou webp")

    data = upload.file.read(settings.IMAGE_MAX_BYTES + 1)
    if not data:
        raise HTTPException(422, "Arquivo vazio")
    if len(data) > settings.IMAGE_MAX_BYTES:
        raise HTTPException(413, f"Arquivo excede o limite de {settings.IMAGE_MAX_BYTES} bytes")

    try:
        img = Image.open(BytesIO(data))
        img = ImageOps.exif_transpose(img)
        img.load()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(422, "Arquivo de imagem inválido ou corrompido")

    if img.width > settings.IMAGE_MAX_INPUT_DIMENSION or img.height > settings.IMAGE_MAX_INPUT_DIMENSION:
        raise HTTPException(422, "Dimensão da imagem excede o limite permitido")

    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    elif img.mode == "RGBA":
        img = img.convert("RGB")

    original = _resize_to_width(img.copy(), settings.IMAGE_MAX_WIDTH)
    thumb = _resize_to_width(img.copy(), settings.IMAGE_THUMB_WIDTH)

    now_utc = datetime.now(timezone.utc)
    ano = now_utc.strftime("%Y")
    mes = now_utc.strftime("%m")
    categoria_nome = _normalize_categoria(categoria)
    token = uuid.uuid4().hex[:8]
    base_name = f"{categoria_nome}_{token}"

    storage_root = Path(settings.IMAGE_STORAGE_ROOT)
    relative_dir = Path("os") / ano / mes / str(ordem_servico_id)
    absolute_dir = storage_root / relative_dir

    original_path = absolute_dir / f"{base_name}.webp"
    thumb_path = absolute_dir / f"{base_name}_thumb.webp"

    _save_webp_atomic(original, original_path)
    _save_webp_atomic(thumb, thumb_path)

    url_arquivo = f"/files/{(relative_dir / (base_name + '.webp')).as_posix()}"
    url_thumb = f"/files/{(relative_dir / (base_name + '_thumb.webp')).as_posix()}"

    file_hash = _sha256(data)
    duplicada = (
        db.query(OSFoto)
        .filter(
            OSFoto.ordem_servico_id == ordem_servico_id,
            OSFoto.hash_sha256 == file_hash,
        )
        .order_by(OSFoto.criado_em.asc())
        .first()
    )

    if foto_principal:
        db.query(OSFoto).filter(OSFoto.ordem_servico_id == ordem_servico_id).update({"foto_principal": False})
    elif total_fotos == 0:
        foto_principal = True

    foto = OSFoto(
        ordem_servico_id=ordem_servico_id,
        url_arquivo=url_arquivo,
        url_thumb=url_thumb,
        categoria=categoria.upper(),
        descricao=descricao,
        mime_type="image/webp",
        tamanho_bytes=original_path.stat().st_size,
        largura_px=original.width,
        altura_px=original.height,
        hash_sha256=file_hash,
        duplicada_de_foto_id=duplicada.id if duplicada else None,
        foto_principal=foto_principal,
        status_arquivo="ATIVO",
        criado_por_usuario=criado_por_usuario,
    )
    db.add(foto)
    db.commit()
    db.refresh(foto)
    return foto

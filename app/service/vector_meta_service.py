import os, json, tempfile

VECTOR_DIR = (os.getenv("VECTOR_DIR") or "/data/vectorstores").strip()

# 강의별 메타 데이터(오디오 저장 여부 담김) 경로 반환
def meta_path(lecture_id: str) -> str:

    return os.path.join(VECTOR_DIR, lecture_id, "meta.json")

# 메타 데이터 파일 반환
def read_meta(lecture_id: str) -> dict:

    try:
        with open(meta_path(lecture_id), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _atomic_write(path: str, data: str):

    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".meta-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
        os.replace(tmp, path)
    finally:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except Exception:
            pass

# 메타 데이터 작성
def write_meta(lecture_id: str, meta: dict):

    _atomic_write(meta_path(lecture_id), json.dumps(meta, ensure_ascii=False, indent=2))

# has_audio 값 반환
def get_has_audio(lecture_id: str) -> bool:

    return bool(read_meta(lecture_id).get("has_audio", False))

# has_audio 값 갱신
def set_has_audio(lecture_id: str, has_audio: bool):

    meta = read_meta(lecture_id)
    meta["has_audio"] = bool(has_audio)
    write_meta(lecture_id, meta)
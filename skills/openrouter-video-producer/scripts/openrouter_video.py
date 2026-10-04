"""OpenRouter 影片工作工具；只使用 Python 標準函式庫，不自動重送提交。"""

import argparse
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

BASE = "https://openrouter.ai/api/v1"
TERMINAL_FAILURES = {"failed", "cancelled", "expired"}
REFERENCE_LIMITS = {"image": 9, "video": 3, "audio": 3}
H3_MODELS = {"minimax/hailuo-3", "minimax/hailuo-3-max"}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("API 回傳重新導向；停止以避免認證外洩，請查證官方端點。")


def request(path, payload=None, authenticated=True):
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if authenticated and not key:
        raise ValueError("請先在本機設定 OPENROUTER_API_KEY 環境變數。")
    headers = {"Accept": "application/json"}
    if key:
        headers["Authorization"] = "Bearer " + key
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(BASE + path, data=data, headers=headers)
    return urllib.request.build_opener(NoRedirect()).open(req, timeout=60)


def api_json(path, payload=None, authenticated=True):
    with request(path, payload, authenticated) as response:
        return json.load(response)


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def save_json(path, value):
    target = Path(path)
    temporary = target.with_name(target.name + ".tmp")
    with temporary.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, target)


def report_error(args, exc):
    """保存錯誤而不重試，也不改寫已存在的工作紀錄。"""
    details = {"operation": args.command, "requires_user_input": True,
               "exception_type": type(exc).__name__, "message": str(exc)}
    if isinstance(exc, urllib.error.HTTPError):
        details["http_status"] = exc.code
        details["request_id"] = (exc.headers or {}).get("x-request-id")
        try:
            body = exc.read().decode("utf-8", errors="replace")
            details["response_body"] = body
            try:
                details["response_json"] = json.loads(body)
            except ValueError:
                pass
        except OSError as read_error:
            details["body_read_error"] = str(read_error)
    job_path = getattr(args, "job", None)
    if job_path:
        details["job_file"] = str(Path(job_path).resolve())
        try:
            job = read_json(job_path)
            details["job_id"] = job.get("id")
            details["job_status"] = job.get("status")
        except (OSError, ValueError, AttributeError):
            pass
    # 只保存错误與必要工作資訊，不複製請求中的素材或認證標頭。
    encoded = json.dumps(details, ensure_ascii=False)
    key = os.environ.get("OPENROUTER_API_KEY")
    if key:
        encoded = encoded.replace(json.dumps(key, ensure_ascii=False)[1:-1], "[REDACTED]")
    details = json.loads(encoded)
    anchor = Path(job_path or args.out)
    error_path = anchor.with_name(anchor.stem + ".error-" + uuid.uuid4().hex + ".json")
    try:
        error_path.parent.mkdir(parents=True, exist_ok=True)
        save_json(error_path, details)
        details["error_file"] = str(error_path.resolve())
    except OSError as save_error:
        message = str(save_error)
        details["error_save_failure"] = message.replace(key, "[REDACTED]") if key else message
    details["next_action"] = "停止操作，說明錯誤並詢問使用者如何處理；不要自行修改或重試。"
    print(json.dumps(details, ensure_ascii=False, indent=2), file=sys.stderr)
    return 1


def model_list():
    result = api_json("/videos/models", authenticated=False)
    if not isinstance(result.get("data"), list):
        raise ValueError("模型 API 未回傳 data 陣列。")
    return result


def validate_references(payload, reference_limits=None):
    """Count actual API entries; local limits never relax the production caps."""
    limits = dict(REFERENCE_LIMITS)
    model_id = payload.get("model")
    if isinstance(model_id, str) and model_id in H3_MODELS:
        limits["total"] = 12
    if reference_limits is not None:
        if not isinstance(reference_limits, dict):
            raise ValueError("reference_limits 必須為數量上限物件。")
        for kind, cap in reference_limits.items():
            if kind not in {*REFERENCE_LIMITS, "total"} or type(cap) is not int or cap < 0:
                raise ValueError("素材上限須為 image/video/audio/total 的非負整數。")
            limits[kind] = min(limits.get(kind, cap), cap)
    counts = dict.fromkeys(REFERENCE_LIMITS, 0)
    for field in ("frame_images", "input_references"):
        entries = payload.get(field, [])
        if not isinstance(entries, list):
            raise ValueError(f"{field} 必須為陣列。")
        for entry in entries:
            if not isinstance(entry, dict):
                raise ValueError(f"{field} 的項目必須為物件。")
            source_type = entry.get("type")
            kind = ({"image_url": "image", "video_url": "video", "audio_url": "audio"}.get(source_type)
                    if isinstance(source_type, str) else None)
            if kind is None or (field == "frame_images" and kind != "image"):
                raise ValueError(f"{field} 的素材類型無效。")
            content = entry.get(source_type)
            if not isinstance(content, dict) or not isinstance(content.get("url"), str) or not content["url"].strip():
                raise ValueError(f"{field} 需要非空的素材 URL。")
            counts[kind] += 1
    counts["total"] = sum(counts.values())
    for kind, cap in limits.items():
        if counts[kind] > cap:
            raise ValueError(f"參考素材超額：{kind}={counts[kind]}，上限 {cap}。")
    if payload.get("frame_images") and payload.get("input_references"):
        raise ValueError("frame_images 會優先於 input_references；請先選定保留必要素材的參考模式。")
    return counts


def validate(payload, model, reference_limits=None):
    validate_references(payload, reference_limits)
    if not isinstance(payload.get("prompt"), str) or not payload["prompt"].strip():
        raise ValueError("需要非空的 prompt。")
    for field, capability in (
        ("duration", "supported_durations"),
        ("resolution", "supported_resolutions"),
        ("aspect_ratio", "supported_aspect_ratios"),
        ("size", "supported_sizes"),
    ):
        if field in payload and payload[field] not in (model.get(capability) or []):
            raise ValueError(f"模型未列出支援 {field}={payload[field]!r}。")
    if "duration" in payload and type(payload["duration"]) is not int:
        raise ValueError("duration 必須為整數。")
    if "size" in payload and ("resolution" in payload or "aspect_ratio" in payload):
        raise ValueError("size 與 resolution/aspect_ratio 請選一種表示方式。")
    if type(payload.get("generate_audio")) is not bool:
        raise ValueError("請明確設定 generate_audio 為 true 或 false。")
    if payload["generate_audio"] and model.get("generate_audio") is not True:
        raise ValueError("模型未列出音訊生成能力。")
    if "seed" in payload:
        if type(payload["seed"]) is not int or model.get("seed") is not True:
            raise ValueError("seed 需要整數且模型須列出 seed 能力。")
    for frame in payload.get("frame_images", []):
        if frame.get("frame_type") not in (model.get("supported_frame_images") or []):
            raise ValueError("模型未列出此首尾幀類型。")
        if frame.get("type") != "image_url" or not frame.get("image_url", {}).get("url"):
            raise ValueError("首尾幀需要 image_url 輸入。")
    if payload.get("callback_url"):
        parsed = urllib.parse.urlsplit(payload["callback_url"])
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError("callback_url 必須為 HTTPS 網址。")


def job_id(job):
    identifier = job.get("id")
    if not isinstance(identifier, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", identifier):
        raise ValueError("缺少有效工作 ID；提交結果可能未知，請先查帳號活動，勿直接重送。")
    return identifier


def submit(request_path, job_path, reference_limits=None):
    target = Path(job_path)
    if target.exists():
        raise ValueError("工作紀錄已存在；請查詢或使用另一次已授權嘗試的目錄。")
    if not os.environ.get("OPENROUTER_API_KEY"):
        raise ValueError("請先在本機設定 OPENROUTER_API_KEY 環境變數。")
    payload = read_json(request_path)
    model = next((m for m in model_list()["data"] if m["id"] == payload.get("model")), None)
    if model is None:
        raise ValueError("模型不在即時影片模型清單內。")
    validate(payload, model, reference_limits)
    target.parent.mkdir(parents=True, exist_ok=True)
    # 先獨占建立意圖紀錄；即使 POST 逾時，也阻止盲目重送。
    with target.open("x", encoding="utf-8") as handle:
        json.dump({"status": "submission_unknown", "request_file": str(Path(request_path).resolve())}, handle)
        handle.flush()
        os.fsync(handle.fileno())
    result = api_json("/videos", payload)
    save_json(target, result)
    job_id(result)
    return result


def status(job_path):
    previous = read_json(job_path)
    identifier = job_id(previous)
    result = api_json("/videos/" + identifier)
    if result.get("id") != identifier:
        raise ValueError("查詢結果的工作 ID 不一致。")
    save_json(job_path, result)
    return result


def download(job_path, output, index=0):
    if index < 0:
        raise ValueError("index 不得為負數。")
    result = status(job_path)
    if result.get("status") != "completed":
        raise ValueError("工作尚未完成：" + str(result.get("status")))
    target = Path(output)
    partial = target.with_name(target.name + ".part")
    if target.exists() or partial.exists():
        raise ValueError("輸出或 .part 已存在；請先檢查既有成果，勿覆蓋。")
    target.parent.mkdir(parents=True, exist_ok=True)
    with request(f"/videos/{job_id(result)}/content?index={index}") as response:
        media_type = response.headers.get("Content-Type", "").split(";")[0].lower()
        if not media_type.startswith("video/"):
            raise ValueError("下載回應不是影片 Content-Type。")
        expected_length = response.headers.get("Content-Length")
        size = 0
        with partial.open("xb") as handle:
            while chunk := response.read(1024 * 1024):
                handle.write(chunk)
                size += len(chunk)
            handle.flush()
            os.fsync(handle.fileno())
    if not size or (expected_length is not None and size != int(expected_length)):
        raise ValueError("影片為空或下載長度不符；保留 .part 供檢查。")
    # 不覆寫既有檔案，成功建立最終檔案後才移除暫存名稱。
    os.link(partial, target)
    partial.unlink()
    return {"id": result["id"], "video_saved": str(target.resolve()), "bytes": size,
            "index": index, "usage": result.get("usage"), "media_verified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    models_parser = commands.add_parser("models")
    models_parser.add_argument("--out", required=True)
    submit_parser = commands.add_parser("submit")
    submit_parser.add_argument("--request", required=True)
    submit_parser.add_argument("--job", required=True)
    submit_parser.add_argument("--reference-limits", help="已查證的較嚴格素材數量上限 JSON，不傳入 API")
    status_parser = commands.add_parser("status")
    status_parser.add_argument("--job", required=True)
    download_parser = commands.add_parser("download")
    download_parser.add_argument("--job", required=True)
    download_parser.add_argument("--out", required=True)
    download_parser.add_argument("--index", type=int, default=0)
    args = parser.parse_args()
    try:
        if args.command == "models":
            result = model_list()
            Path(args.out).parent.mkdir(parents=True, exist_ok=True)
            save_json(args.out, result)
        elif args.command == "submit":
            limits = read_json(args.reference_limits) if args.reference_limits else None
            result = submit(args.request, args.job, limits)
        elif args.command == "status":
            result = status(args.job)
        else:
            result = download(args.job, args.out, args.index)
        if result.get("status") in TERMINAL_FAILURES:
            return report_error(args, RuntimeError(json.dumps(result, ensure_ascii=False)))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except urllib.error.HTTPError as exc:
        return report_error(args, exc)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        return report_error(args, exc)


if __name__ == "__main__":
    sys.exit(main())

"""離線驗證付費提交與下載的可觀察行為；不呼叫外部 API。"""

import io
import json
from pathlib import Path
import tempfile
import unittest
import urllib.error
from unittest.mock import patch

import openrouter_video as video


MODEL = {"id": "test/video", "supported_durations": [4, 8],
         "supported_resolutions": ["720p"], "supported_aspect_ratios": ["16:9"],
         "generate_audio": False, "seed": False, "supported_frame_images": ["first_frame"]}
PAYLOAD = {"model": "test/video", "prompt": "雨夜", "duration": 8, "generate_audio": False}


class Response(io.BytesIO):
    def __init__(self, content, media_type="video/mp4", length=None):
        super().__init__(content)
        self.headers = {"Content-Type": media_type}
        if length is not None:
            self.headers["Content-Length"] = str(length)


class WorkflowTests(unittest.TestCase):
    def test_heygen_modes_audio_seed_and_2k_combination(self):
        model = {**MODEL, "id": video.HEYGEN_VIDEO_MODEL, "seed": True,
                 "supported_durations": list(range(5, 16)),
                 "supported_resolutions": ["480p", "768p", "2K"],
                 "supported_aspect_ratios": ["21:9", "16:9", "4:3", "1:1", "3:4", "9:16"]}
        payload = {"model": video.HEYGEN_VIDEO_MODEL, "prompt": "咖啡店", "duration": 5,
                   "resolution": "768p", "aspect_ratio": "16:9"}
        frame = {"type": "image_url", "image_url": {"url": "https://example.com/start.png"},
                 "frame_type": "first_frame"}
        reference = {"type": "image_url", "image_url": {"url": "https://example.com/character.png"}}
        for changes in ({}, {"frame_images": [frame]}, {"input_references": [reference]},
                        {"resolution": "2K", "aspect_ratio": "9:16"}, {"seed": 0}, {"seed": 4294967295}):
            video.validate({**payload, **changes}, model)
        for changes in ({"generate_audio": False}, {"generate_audio": True}, {"seed": -1},
                        {"seed": 4294967296}, {"seed": True}, {"resolution": "720p"},
                        {"resolution": "2K", "aspect_ratio": "1:1"},
                        {"duration": 4}, {"duration": 16}, {"prompt": "x" * 32001},
                        {"frame_images": [frame, frame]},
                        {"frame_images": [{**frame, "frame_type": "last_frame"}]}):
            with self.subTest(changes=changes.keys()), self.assertRaises(ValueError):
                video.validate({**payload, **changes}, model)

    def test_heygen_reference_total_and_audio_only(self):
        def ref(kind):
            key = kind + "_url"
            return {"type": key, key: {"url": "https://example.com/media"}}
        refs = [ref("image")] * 9 + [ref("video")] * 2 + [ref("audio")]
        payload = {"model": video.HEYGEN_VIDEO_MODEL, "input_references": refs}
        self.assertEqual(video.validate_references(payload)["total"], 12)
        with self.assertRaises(ValueError):
            video.validate_references({**payload, "input_references": refs + [ref("audio")]}, {"total": 99})
        with self.assertRaises(ValueError):
            video.validate_references({**payload, "input_references": [ref("audio")]})
        video.validate_references({**payload, "input_references": [ref("video"), ref("audio")]})

    def test_unknown_audio_switch_is_omitted_without_promising_silence(self):
        payload = {key: value for key, value in PAYLOAD.items() if key != "generate_audio"}
        for capability in ({**MODEL, "generate_audio": None},
                           {key: value for key, value in MODEL.items() if key != "generate_audio"}):
            video.validate(payload, capability)
            for audio in (True, False, None):
                with self.subTest(audio=audio), self.assertRaises(ValueError):
                    video.validate({**payload, "generate_audio": audio}, capability)
        for audio in (True, False):
            video.validate({**payload, "generate_audio": audio}, {**MODEL, "generate_audio": True})
        with self.assertRaises(ValueError):
            video.validate(payload, {**MODEL, "generate_audio": True})

    def test_grok_lite_accepts_text_and_single_first_frame(self):
        model = {**MODEL, "id": video.GROK_LITE_MODEL, "generate_audio": None,
                 "seed": None, "supported_durations": list(range(1, 16)),
                 "supported_resolutions": ["480p", "720p", "1080p"],
                 "supported_aspect_ratios": ["16:9", "9:16", "1:1", "4:3", "3:4", "3:2", "2:3"]}
        payload = {"model": video.GROK_LITE_MODEL, "prompt": "雨夜", "duration": 5,
                   "resolution": "720p", "aspect_ratio": "16:9"}
        frame = {"type": "image_url", "image_url": {"url": "https://example.com/start.png"},
                 "frame_type": "first_frame"}
        video.validate(payload, model)
        video.validate({**payload, "frame_images": [frame]}, model)
        for changes in ({"duration": 16}, {"duration": 0}, {"duration": 5.5},
                        {"resolution": "4K"}, {"aspect_ratio": "21:9"},
                        {"size": "1280x720"}, {"seed": 42},
                        {"frame_images": [{**frame, "frame_type": "last_frame"}]},
                        {"frame_images": [frame, frame]},
                        {"input_references": [frame]}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                video.validate({**payload, **changes}, model)

    def test_cli_http_error_preserves_body_and_job_redacts_key_without_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            job_path = Path(directory) / "job.json"
            original = {"id": "job-1", "status": "pending"}
            video.save_json(job_path, original)
            body = b'{"error":{"code":"PrivacyInformation","message":"test-key"}}'
            error = urllib.error.HTTPError("https://openrouter.ai/api/v1/videos/job-1", 400,
                                           "Bad Request", {"x-request-id": "request-1"}, io.BytesIO(body))
            output = io.StringIO()
            with patch.dict(video.os.environ, {"OPENROUTER_API_KEY": "test-key"}), \
                 patch.object(video.sys, "argv", ["video", "status", "--job", str(job_path)]), \
                 patch.object(video, "api_json", side_effect=error) as api, \
                 patch.object(video.sys, "stderr", output):
                self.assertEqual(video.main(), 1)
            api.assert_called_once_with("/videos/job-1")
            self.assertEqual(video.read_json(job_path), original)
            saved = video.read_json(next(Path(directory).glob("job.error-*.json")))
            self.assertEqual(saved["http_status"], 400)
            self.assertEqual(saved["request_id"], "request-1")
            self.assertEqual(saved["response_json"]["error"]["code"], "PrivacyInformation")
            self.assertTrue(saved["requires_user_input"])
            self.assertNotIn("test-key", json.dumps(saved) + output.getvalue())
            self.assertIn("[REDACTED]", saved["response_body"])

    def test_cli_non_json_error_retains_response(self):
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "models.json"
            error = urllib.error.HTTPError("https://openrouter.ai", 502, "Bad Gateway", {},
                                           io.BytesIO(b"upstream unavailable"))
            with patch.object(video.sys, "argv", ["video", "models", "--out", str(output_path)]), \
                 patch.object(video, "model_list", side_effect=error), \
                 patch.object(video.sys, "stderr", io.StringIO()):
                self.assertEqual(video.main(), 1)
            saved = video.read_json(next(Path(directory).glob("models.error-*.json")))
            self.assertEqual(saved["response_body"], "upstream unavailable")
            self.assertFalse(output_path.exists())

    def test_cli_timeout_keeps_unknown_submission_and_requires_input(self):
        with tempfile.TemporaryDirectory() as directory:
            request_path = Path(directory) / "request.json"
            job_path = Path(directory) / "job.json"
            request_path.write_text(json.dumps(PAYLOAD), encoding="utf-8")
            with patch.dict(video.os.environ, {"OPENROUTER_API_KEY": "test-key"}), \
                 patch.object(video.sys, "argv", ["video", "submit", "--request", str(request_path),
                                                 "--job", str(job_path)]), \
                 patch.object(video, "model_list", return_value={"data": [MODEL]}), \
                 patch.object(video, "api_json", side_effect=TimeoutError("timed out")) as api, \
                 patch.object(video.sys, "stderr", io.StringIO()):
                self.assertEqual(video.main(), 1)
                api.assert_called_once()
            self.assertEqual(video.read_json(job_path)["status"], "submission_unknown")
            saved = video.read_json(next(Path(directory).glob("job.error-*.json")))
            self.assertTrue(saved["requires_user_input"])
            self.assertNotIn("http_status", saved)

    def test_cli_terminal_failure_requires_input_but_pending_does_not(self):
        with tempfile.TemporaryDirectory() as directory:
            job_path = Path(directory) / "job.json"
            video.save_json(job_path, {"id": "job-1", "status": "pending"})
            with patch.object(video.sys, "argv", ["video", "status", "--job", str(job_path)]), \
                 patch.object(video.sys, "stderr", io.StringIO()), \
                 patch.object(video.sys, "stdout", io.StringIO()):
                with patch.object(video, "api_json", return_value={"id": "job-1", "status": "pending"}):
                    self.assertEqual(video.main(), 0)
                    self.assertEqual(list(Path(directory).glob("*.error-*.json")), [])
                with patch.object(video, "api_json", return_value={"id": "job-1", "status": "failed",
                                                                  "error": {"code": "Rejected"}}):
                    self.assertEqual(video.main(), 1)
            self.assertEqual(video.read_json(job_path)["status"], "failed")
            self.assertTrue(video.read_json(next(Path(directory).glob("*.error-*.json")))["requires_user_input"])

    def test_discrete_duration_and_audio(self):
        video.validate(PAYLOAD, MODEL)
        for changes in ({"duration": 6}, {"generate_audio": True}, {"seed": 42},
                        {"frame_images": [{"frame_type": "last_frame"}]}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                video.validate({**PAYLOAD, **changes}, MODEL)

    def test_submit_timeout_blocks_second_post(self):
        with tempfile.TemporaryDirectory() as directory:
            request_path = Path(directory) / "request.json"
            job_path = Path(directory) / "job.json"
            request_path.write_text(json.dumps(PAYLOAD), encoding="utf-8")
            with patch.dict(video.os.environ, {"OPENROUTER_API_KEY": "test-key"}), \
                 patch.object(video, "model_list", return_value={"data": [MODEL]}), \
                 patch.object(video, "api_json", side_effect=TimeoutError) as post:
                with self.assertRaises(TimeoutError):
                    video.submit(request_path, job_path)
                self.assertEqual(video.read_json(job_path)["status"], "submission_unknown")
                with self.assertRaises(ValueError):
                    video.submit(request_path, job_path)
                self.assertEqual(post.call_count, 1)

    def test_resume_uses_original_job_without_post(self):
        with tempfile.TemporaryDirectory() as directory:
            job_path = Path(directory) / "job.json"
            video.save_json(job_path, {"id": "job-1", "status": "pending"})
            completed = {"id": "job-1", "status": "completed", "usage": {"cost": 0.5}}
            with patch.object(video, "api_json", return_value=completed) as api:
                self.assertEqual(video.status(job_path), completed)
                api.assert_called_once_with("/videos/job-1")
            self.assertEqual(video.read_json(job_path), completed)

    def test_download_uses_authenticated_content_not_external_url(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "video.mp4"
            completed = {"id": "job-1", "status": "completed",
                         "unsigned_urls": ["https://external.example/movie.mp4"]}
            with patch.object(video, "status", return_value=completed), \
                 patch.object(video, "request", return_value=Response(b"test-video")) as request:
                result = video.download("job.json", output)
                request.assert_called_once_with("/videos/job-1/content?index=0")
            self.assertEqual(output.read_bytes(), b"test-video")
            self.assertFalse(result["media_verified"])
            self.assertFalse(output.with_name("video.mp4.part").exists())

    def test_truncated_download_does_not_publish_final_file(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "video.mp4"
            with patch.object(video, "status", return_value={"id": "job-1", "status": "completed"}), \
                 patch.object(video, "request", return_value=Response(b"short", length=100)):
                with self.assertRaises(ValueError):
                    video.download("job.json", output)
            self.assertFalse(output.exists())
            self.assertTrue(output.with_name("video.mp4.part").exists())

    def test_pending_or_nonvideo_response_cannot_be_saved_as_video(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "video.mp4"
            with patch.object(video, "status", return_value={"id": "job-1", "status": "pending"}), \
                 patch.object(video, "request") as request:
                with self.assertRaises(ValueError):
                    video.download("job.json", output)
                request.assert_not_called()
            with patch.object(video, "status", return_value={"id": "job-1", "status": "completed"}), \
                 patch.object(video, "request", return_value=Response(b"{}", "application/json")):
                with self.assertRaises(ValueError):
                    video.download("job.json", output)
            self.assertFalse(output.exists())

    def test_redirect_refuses_forwarding_auth(self):
        with self.assertRaises(ValueError):
            video.NoRedirect().redirect_request(None, None, 302, "", {}, "https://external.example")


class ReferenceValidationTests(unittest.TestCase):
    def payload(self, counts, model="test/video"):
        refs = [{"type": kind + "_url", kind + "_url": {"url": f"https://example.com/{kind}-{n}"}}
                for kind, count in counts.items() for n in range(count)]
        return {**PAYLOAD, "model": model, "input_references": refs}

    def test_each_type_boundary_and_excess(self):
        for kind, limit in (("image", 9), ("video", 3), ("audio", 3)):
            with self.subTest(kind=kind):
                self.assertEqual(video.validate_references(self.payload({kind: limit}))[kind], limit)
                with self.assertRaisesRegex(ValueError, "超額"):
                    video.validate_references(self.payload({kind: limit + 1}))

    def test_full_board_and_start_image_are_files_not_panel_counts(self):
        payload = self.payload({"image": 3})
        self.assertEqual(video.validate_references(payload), {"image": 3, "video": 0, "audio": 0, "total": 3})

    def test_repeated_url_entries_still_count(self):
        payload = self.payload({"image": 9})
        payload["input_references"].append(payload["input_references"][0])
        with self.assertRaisesRegex(ValueError, "image=10"):
            video.validate_references(payload)

    def test_generated_audio_is_not_an_audio_reference(self):
        payload = {**PAYLOAD, "generate_audio": True}
        video.validate(payload, {**MODEL, "generate_audio": True})
        self.assertEqual(video.validate_references(payload)["audio"], 0)

    def test_native_frames_count_as_images_and_mixed_modes_are_rejected(self):
        payload = {**PAYLOAD, "frame_images": [
            {"type": "image_url", "image_url": {"url": "https://example.com/start.png"}, "frame_type": "first_frame"}]}
        self.assertEqual(video.validate_references(payload)["image"], 1)
        video.validate(payload, MODEL)
        payload["input_references"] = self.payload({"image": 1})["input_references"]
        with self.assertRaisesRegex(ValueError, "frame_images"):
            video.validate(payload, MODEL)

    def test_stricter_limits_and_zero_support_cannot_be_relaxed(self):
        with self.assertRaisesRegex(ValueError, "上限 6"):
            video.validate_references(self.payload({"image": 7}), {"image": 6})
        with self.assertRaisesRegex(ValueError, "上限 9"):
            video.validate_references(self.payload({"image": 10}), {"image": 99})
        with self.assertRaisesRegex(ValueError, "上限 0"):
            video.validate_references(self.payload({"audio": 1}), {"audio": 0})

    def test_h3_total_twelve_boundary_for_both_models(self):
        for model_id in video.H3_MODELS:
            with self.subTest(model=model_id):
                self.assertEqual(video.validate_references(self.payload({"image": 8, "video": 2, "audio": 2}, model_id))["total"], 12)
                with self.assertRaisesRegex(ValueError, "total=13"):
                    video.validate_references(self.payload({"image": 9, "video": 2, "audio": 2}, model_id), {"total": 99})

    def test_unknown_malformed_and_empty_inputs_are_rejected(self):
        for refs in (None, {}, [None], [{"type": []}], [{"type": "unknown"}], [{"type": "image_url", "image_url": {"url": ""}}],
                     [{"type": "audio_url", "audio_url": "https://example.com/a.wav"}]):
            with self.subTest(refs=refs), self.assertRaises(ValueError):
                video.validate_references({**PAYLOAD, "input_references": refs})
        for limits in ([], {"image": True}, {"image": -1}, {"image": 1.5}, {"typo": 1}):
            with self.subTest(limits=limits), self.assertRaises(ValueError):
                video.validate_references(PAYLOAD, limits)

    def test_excess_is_blocked_before_paid_post_or_job_intent(self):
        with tempfile.TemporaryDirectory() as directory:
            request_path = Path(directory) / "request.json"
            job_path = Path(directory) / "job.json"
            request_path.write_text(json.dumps(self.payload({"image": 10})), encoding="utf-8")
            with patch.dict(video.os.environ, {"OPENROUTER_API_KEY": "test-key"}), \
                 patch.object(video, "model_list", return_value={"data": [MODEL]}), \
                 patch.object(video, "api_json") as api, self.assertRaisesRegex(ValueError, "超額"):
                video.submit(request_path, job_path)
            api.assert_not_called()
            self.assertFalse(job_path.exists())

    def test_cli_uses_local_limit_file_without_sending_it_to_api(self):
        with tempfile.TemporaryDirectory() as directory:
            task_root = Path(directory)
            request_path, job_path, limits_path = (task_root / name for name in ("request.json", "job.json", "limits.json"))
            payload = self.payload({"image": 1})
            request_path.write_text(json.dumps(payload), encoding="utf-8")
            limits_path.write_text(json.dumps({"image": 1}), encoding="utf-8")
            with patch.dict(video.os.environ, {"OPENROUTER_API_KEY": "test-key"}), \
                 patch.object(video.sys, "argv", ["video", "submit", "--request", str(request_path),
                                                 "--job", str(job_path), "--reference-limits", str(limits_path)]), \
                 patch.object(video, "model_list", return_value={"data": [MODEL]}), \
                 patch.object(video, "api_json", return_value={"id": "job-1", "status": "pending"}) as api, \
                 patch.object(video.sys, "stdout", io.StringIO()):
                self.assertEqual(video.main(), 0)
            api.assert_called_once_with("/videos", payload)
            self.assertNotIn("reference_limits", video.read_json(request_path))


if __name__ == "__main__":
    unittest.main()

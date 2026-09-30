"""離線驗證付費提交與下載的可觀察行為；不呼叫外部 API。"""

import io
import json
from pathlib import Path
import tempfile
import unittest
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


if __name__ == "__main__":
    unittest.main()

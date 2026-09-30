# API 與素材對應

基底為 `https://openrouter.ai/api/v1`。認證為 `Authorization: Bearer <OPENROUTER_API_KEY>`；JSON 請求使用 `Content-Type: application/json`。

| 操作 | 方法與路徑 | 結果 |
|---|---|---|
| 模型能力 | `GET /videos/models` | `data[]` 的模型 ID、支援參數、價格 |
| 提交 | `POST /videos` | `202`，`id`、`polling_url`、`status` |
| 查詢 | `GET /videos/{jobId}` | 狀態、錯誤、`generation_id`、`usage`、輸出 URL |
| 下載 | `GET /videos/{jobId}/content?index=0` | 影片位元組，通常為 `video/mp4` |

`polling_url` 可能是相對或絕對路徑。使用工作 ID 建立官方 endpoint 可避免混用；不要把 Bearer Key 傳到任意回傳 URL。content endpoint 下載也需要認證。

## 提交內容

解析度與比例的官方欄位、Seedance 2.5 參考規格，以及未指定時先查再問的流程見 [官方解析度與畫面比例設定](output-settings.md)。

此例只示範形狀；模型及參數須先依即時能力查證。

```json
{
  "model": "google/veo-3.1",
  "prompt": "雨夜咖啡店窗外，鏡頭緩緩推近霓虹燈，雨水沿玻璃流下。臉部身分一致性：本鏡無人物，不新增人物。",
  "duration": 8,
  "aspect_ratio": "16:9",
  "resolution": "720p",
  "generate_audio": false
}
```

- `duration`、`resolution`、`aspect_ratio`、`size`、首尾幀分別對應 `supported_durations`、`supported_resolutions`、`supported_aspect_ratios`、`supported_sizes`、`supported_frame_images`。
- `size` 與解析度加比例是替代表示；避免同時提供矛盾值。
- `seed` 僅在模型支援時使用，不能承諾完全可重現。
- `usage.cost` 是完成後回報的實際成本；估價來自 `pricing_skus` 與其計價單位，不把所有 SKU 都當成每秒費用。

## 圖片、影片與聲音

首尾幀使用 `frame_images`，例如：

```json
{
  "frame_images": [
    {
      "type": "image_url",
      "image_url": {"url": "https://example.com/first-frame.png"},
      "frame_type": "first_frame"
    }
  ]
}
```

風格或人物參考使用 `input_references`，圖片項目形狀同上，但不含 `frame_type`。兩者同時提供時 `frame_images` 優先，不假設參考圖仍全部生效。先確認所選模型對混合參考的行為。

圖片 URL 可使用可讀取的 HTTPS 網址或 `data:image/png;base64,...` 等實際 MIME 的 data URL。本機磁碟路徑不是 API 可存取的 URL；由本機檔案編碼或使用已授權的既有網址，不為傳圖而擅自公開上傳。送出的 `request.json` 含素材資料時，也應留在影片專案。

音訊／影片參考由 `input_references` 承載，但只有特定供應商會使用，其他供應商可能忽略。官方 create API 與所選供應商文件確認支援、項目 schema、格式、大小及數量限制後再建立；本參考不臆造跨模型通用 schema。

使用 Seedance 的混合素材時，另依 [Seedance 素材綁定與提示詞](seedance-reference-prompts.md) 建立素材、API 欄位與提示詞指代的對照。以實際提交規則更新範例，不將其他平台的 `@` 標籤直接視為已完成綁定。

## 供應商選項與 webhook

進階參數位於 `provider.options.<provider-slug>.parameters`。先查 `allowed_passthrough_parameters`，再查該供應商官方文件的值域及組合限制。一般情況省略，不複製另一模型的負面提示詞參數。

本機 Skill 預設輪詢。已有 HTTPS 接收端且使用者要求 webhook 時才使用 `callback_url`；不因生成影片而另部署服務。終止事件包含 `completed`、`failed`、`cancelled`、`expired`，以 `X-OpenRouter-Idempotency-Key` 去重。設定 signing secret 時，驗證 `X-OpenRouter-Signature`：HMAC-SHA256 的訊息為 `<timestamp>,<raw_request_body>`；使用原始位元組、固定時間比較及時間窗（包含未來時間容差）。詳見[官方指南](https://openrouter.ai/docs/guides/overview/multimodal/video-generation)。

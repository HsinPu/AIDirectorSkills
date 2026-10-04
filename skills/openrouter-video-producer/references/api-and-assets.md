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

使用 MiniMax H3／H3 Max 時，另依 [H3 素材引用與提示詞](minimax-h3-reference-prompts.md) 區分首尾幀與一般參考，核對所選供應商的指代與映射。fal 的 `reference_image_urls`、`reference_video_urls`、`reference_audio_urls` 是 fal 欄位，不直接填入 OpenRouter 請求；提示詞標籤也不能代替素材輸入。

## 素材配額與提交檢查

製作上限是每鏡／每次提交圖片 9 張、影片參考 3 段、聲音參考 3 段；選定模型、供應商、模式若更嚴格就取較小值。起始圖、人物原照、完整六格運鏡頁與原生首／尾幀均計入圖片，一張完整頁算 1 張；`generate_audio` 及文字對白不算上傳聲音。多鏡合併要按單次請求全部輸入重算，共用圖只送一次算一次，重複輸入仍占數量。H3／H3 Max 另保守套用所有參考合計 12 個，仍須查實際路由的素材類型、時長、格式及模式限制，不能把配額當成能力保證。[MiniMax H3 官方規格](https://github.com/MiniMax-AI/cli/blob/main/skill/h3-video/references/h3-video.md)，查證日期：2026-10-04。

新導演包宣告 `asset_contract: "start_frame_v1"`，提交前核對 `start_frame_reference_id` 的圖檔、版本、SHA-256 與 `reference_ids`。起始圖是局部 0 秒的成片構圖／風格來源，不是漫畫頁拆格；完整運鏡頁／預演提供後續動作，人物原照提供身分。保留所要求的遊戲介面，不把「排除草圖標示」寫成一律排除 HUD。缺圖或漏列來源不能聲稱整包已準備好；已核准舊包不自動補畫。

`source-map.json` 或等效紀錄逐項保存本機資產 ID、來源角色、檔名、版本、雜湊、實際 API 欄位與順序、提示詞指代及本次計數。一般參考模式將起始圖與必要運鏡／人物來源共同送入 `input_references`；原生首幀模式才放 `frame_images`，記為 `first_frame`。兩欄同時非空時，CLI 會在 POST 前拒絕；先依查證結果與已確認參考策略選模式，不自行刪掉運鏡或身分來源。

助理先核對 manifest 與實際 `request.json` 沒有缺漏，再執行提交。CLI 計算 `input_references` 與 `frame_images` 的實際項目，不把同一 URL 的重複輸入去重；超額或無法辨識的素材項目會在付費 POST 前拒絕。已查證的更嚴格上限放本機 `reference-limits.json`，例如：

2026-10-04 核對的 [OpenRouter 官方 OpenAPI](https://github.com/OpenRouterTeam/docs/blob/main/openapi/openapi.yaml) 將一般參考分為 `image_url`、`video_url`、`audio_url`：`type` 指定類型，同名物件的 `url` 提供素材網址。CLI 按此 schema 計數，型別或欄位變更時先查證再調整，不以未知類型繞過配額。

```json
{"image": 6, "video": 2, "audio": 0, "total": 8}
```

```text
python scripts/openrouter_video.py submit --request <unit>/request.json --job <unit>/job.json --reference-limits <unit>/reference-limits.json
```

值須為非負整數，0 表示不允許此類型；較大值不能放寬製作上限。此檔只供本機檢查，不送入 OpenRouter。通過數量檢查不證明所有素材會生效，也不證明圖中的風格、臉部或精確首幀已遵照。

## 供應商選項與 webhook

進階參數位於 `provider.options.<provider-slug>.parameters`。先查 `allowed_passthrough_parameters`，再查該供應商官方文件的值域及組合限制。一般情況省略，不複製另一模型的負面提示詞參數。

本機 Skill 預設輪詢。已有 HTTPS 接收端且使用者要求 webhook 時才使用 `callback_url`；不因生成影片而另部署服務。終止事件包含 `completed`、`failed`、`cancelled`、`expired`，以 `X-OpenRouter-Idempotency-Key` 去重。設定 signing secret 時，驗證 `X-OpenRouter-Signature`：HMAC-SHA256 的訊息為 `<timestamp>,<raw_request_body>`；使用原始位元組、固定時間比較及時間窗（包含未來時間容差）。詳見[官方指南](https://openrouter.ai/docs/guides/overview/multimodal/video-generation)。

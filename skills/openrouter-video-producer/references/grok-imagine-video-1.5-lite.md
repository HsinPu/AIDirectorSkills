# Grok Imagine Video 1.5 Lite

查證日期：2026-10-07。依 OpenRouter 模型頁、當日直接讀取的 `GET /api/v1/videos/models` 與 xAI 模型頁整理；生成前仍查即時模型資料。這是規格查證，未提交付費生成，未驗證實際音軌、生成速度或畫面品質。

## 模型與輸出

模型 ID：`x-ai/grok-imagine-video-1.5-lite`。OpenRouter 顯示發布日期為 2026-10-06，定位為 Grok Imagine Video 1.5 的蒸餾版本，以部分品質換取速度及價格。請求使用上述 ID，不從 canonical slug 的日期推斷發布時間。

| 項目 | 2026-10-07 查證結果 |
|---|---|
| 模式 | 文字生成、起始圖片生成 |
| `supported_durations` | 整數 1、2、3、4、5、6、7、8、9、10、11、12、13、14、15 秒 |
| `supported_resolutions` | `480p`、`720p`、`1080p` |
| `supported_aspect_ratios` | `16:9`、`9:16`、`1:1`、`4:3`、`3:4`、`3:2`、`2:3` |
| `supported_frame_images` | 僅 `first_frame` |
| `supported_sizes` | `null`，使用 `resolution` 加 `aspect_ratio`，不推導精確 `size` |
| `generate_audio`、`seed` | 均為 `null`，未公開可用開關／種子能力 |
| `allowed_passthrough_parameters` | 空陣列，不添加未列出的供應商參數 |

**1080p 由 720p 渲染後放大，不能稱為原生 1080p。** 使用者要求原生 Full HD 時說明差異，再解決模型選擇。未指定解析度與比例時依 [輸出設定](output-settings.md) 先查再問；已指定就沿用。

## 素材與提示詞

- 文字模式省略 `frame_images` 與 `input_references`。
- 圖片模式使用一張 `frame_images`，`frame_type: "first_frame"`，並按 [API 與素材對應](api-and-assets.md) 提供 HTTPS 或實際 MIME 的 data URL。單一首幀是目前 Skill 採用的提交策略，不把全 Skill 的 9 張圖片配額當成此模式支援多圖的證據。
- 不送 `last_frame`。目前未查證 Lite 在 OpenRouter 支援 `input_references`、多圖身分參考、影片編輯／延長、影片或聲音參考；不能沿用舊版 Grok 的七張參考圖、1.5 的聲音功能或 xAI 原生 API 欄位。
- 必要人物設定圖、起始圖與運鏡頁需要共同輸入時，先解決單一首幀的限制；不擅自刪除必要來源或拼成多格頁當作精確首幀。人物已在採用的首幀中也不能宣稱已另傳身分參考。
- 提示詞描述首幀之後的主體動作、方向、鏡頭、時間節奏與最後狀態；不用 `@ImageN`、`@VideoN` 或原生 `<AUDIO_N>` 標籤虛構素材綁定。這些是製作建議，不是 Lite 專用語法。
- xAI 生成指南說圖片模式指定不同 `aspect_ratio` 會拉伸輸入圖；素材比例與目標不一致時先檢查構圖並解決，不能保證維持原始比例。此為上游行為提示，OpenRouter 實際輸出仍須驗證。

## 聲音與未公開能力

本次 OpenRouter 的 `generate_audio` 為 `null`。省略此欄位，不自行送 `true`／`false`，也不宣稱成片必定有聲或無聲。xAI 通用指南描述原生 API 的音訊預設與開關，但未確認 Lite 的 OpenRouter 映射；不能把這當成本模型開關已支援的證據。

使用者要求對白、同步聲音或靜音時，先查必要能力；若仍無法確認，與使用者解決模型或已授權後製策略再提交。下載後檢查實際音軌。`seed: null` 時不送種子、不保證可重現；passthrough 清單為空時不添加 `negative_prompt`、`voice_id` 等未列出參數。

## 價格快照（美元）

| 解析度 | 每秒影片輸出 | 5 秒文字生成估價 | 5 秒＋一張首幀估價 |
|---|---:|---:|---:|
| `480p` | $0.02 | $0.10 | $0.11 |
| `720p` | $0.03 | $0.15 | $0.16 |
| `1080p` | $0.14 | $0.70 | $0.71 |

`pricing_skus` 列出 `cents_per_video_output_second_480p: "2"`、`..._720p: "3"`、`..._1080p: "14"`，以及 `cents_per_image_input: "1"`。單位是美分：先除以 100。估價為片長 × 所選解析度每秒單價 ＋ 實際輸入圖片數 × $0.01；以即時 SKU 重算，實際費用讀完成工作的 `usage.cost`。

## 請求範例

以下示範已確認 5 秒、720p、16:9 的單一首幀請求；範例網址須換成可讀取的實際素材。文字生成只需移除 `frame_images`。不自動採用範例規格。

```json
{
  "model": "x-ai/grok-imagine-video-1.5-lite",
  "prompt": "延續起始圖中的雨夜街景，鏡頭在五秒內緩緩向前移動，路面倒影隨視角自然改變，結尾停在咖啡店門前。本鏡無人物，不新增人物。",
  "duration": 5,
  "resolution": "720p",
  "aspect_ratio": "16:9",
  "frame_images": [
    {
      "type": "image_url",
      "image_url": {"url": "https://example.com/first-frame.png"},
      "frame_type": "first_frame"
    }
  ]
}
```

沿用 `POST /api/v1/videos` → 保存工作 ID → 輪詢 → 下載的流程。xAI 原生 `/v1/videos/generations`、`image` 或 `reference_audios` 不直接填入 OpenRouter 請求。新增模型規則不授權付費測試。

## 官方來源

- [OpenRouter 模型頁](https://openrouter.ai/x-ai/grok-imagine-video-1.5-lite)：發布日期、定位、放大說明、模式與輸出。
- [OpenRouter 即時模型 API](https://openrouter.ai/api/v1/videos/models)：本次直接取得的規格與 SKU。
- [OpenRouter 模型 API schema](https://openrouter.ai/docs/api/api-reference/video-generation/list-videos-models)：能力欄位。
- [OpenRouter 影片生成指南](https://openrouter.ai/docs/guides/overview/multimodal/video-generation)：非同步流程與素材格式。
- [xAI Lite 模型頁](https://docs.x.ai/developers/models/grok-imagine-video-1.5-lite)：核對分解析度單價與輸入模態。
- [xAI 影片生成指南](https://docs.x.ai/developers/model-capabilities/video/generation)：上游圖片比例行為與原生功能；不能自動視為 OpenRouter Lite 支援。

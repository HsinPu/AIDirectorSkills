# HeyGen Video 素材、提示詞與計費

查證日期：2026-10-07。使用 OpenRouter 模型頁、當日直接取得的影片模型 API／供應商 endpoint，及 HeyGen 原生模型文件。未提交付費生成；實際引用效果、聲音、尺寸與費用須在成片核對。

## 選模型與輸出

OpenRouter ID：`heygen/heygen-video-1`；canonical slug：`heygen/heygen-video-1-20260930`。這是生成完整場景的模型；不套用 Avatar IV／Video Agent 的 `avatar_id`、`voice_id`、script 或 lip-sync 流程。

| 能力 | 即時 API 快照 |
|---|---|
| 片長 | 整數 5–15 秒；即時陣列列出每個整數 |
| 解析度 | `480p`、`768p`、`2K`（OpenRouter 大寫 K，原生為 `2k`） |
| 比例 | `21:9`、`16:9`、`4:3`、`1:1`、`3:4`、`9:16` |
| 精確尺寸 | `supported_sizes: null`，不自行送 `size` |
| 原生幀 | 僅 `first_frame`，不送尾幀 |
| 聲音開關 | `generate_audio: false`，但模型官方明確說會生成對白、環境音與效果音 |
| 隨機種子 | `seed: true`；原生上限為 uint32，0–4294967295 |
| Passthrough | 空陣列，不送未公開的供應商控制 |

原生文件限定 2K 的文字／參考模式為 `16:9` 或 `9:16`；Skill 保守要求所有 2K 請求明確採用這兩種比例。首幀模式實際跟隨圖片比例與 EXIF 方向，先核對首幀構圖，不能承諾 `aspect_ratio` 會替你裁切。不要把原生 `adaptive`／其他平台 `auto` 填入 OpenRouter 比例欄位。需要裁切時依已授權素材策略處理。

原生名義 `16:9` 的 768p 為 1344×768、480p 為 832×480、2K 為 2688×1536，並非精確 16:9；只作驗收參考，不視為 OpenRouter 支援的 `size`。下載後讀取實際寬高、時長與音軌。原生輸出 MP4/H.264、24 fps、AAC 32 kHz stereo；影格取整可能使實際片長略長於請求。

## 三種模式與素材上限

| 模式 | OpenRouter 輸入 | 用途 |
|---|---|---|
| 文字 | 省略兩種素材欄位 | 建立新場景 |
| 首幀圖片 | 單一 `frame_images`，`frame_type: "first_frame"` | 起始構圖採用該圖片 |
| 參考 | `input_references` | 人物、商品、場景、運動或聲音引導；不保證精確首幀 |

兩欄不能同時非空，避免首幀優先而漏掉必要人物／運鏡參考。原生 `mode`、`image`、`reference_images`、`reference_videos`、`reference_audio` 不能直接放入 OpenRouter。

參考最多 **9 張圖、3 段影片、3 段聲音，合計最多 12 個**。至少有一張圖片或一段影片，不能只有聲音。保留使用者已採用的人物版本、起始圖與完整運鏡來源；數量超額不自行省略。

HeyGen 原生只讀每段影片的前 5 秒。提交前檢查必要動作是否在這段；要截取其他區間時記錄裁切範圍與來源，依已授權剪輯範圍處理。多段影片仍分別計入上限。

| 原生素材規則 | 上限 |
|---|---:|
| HTTPS 圖片 | 16 MB |
| HTTPS 影片／聲音 | 32 MB |
| inline base64 圖片 | 5 MB |
| inline base64 影片／聲音 | 16 MB |

這些是上游的保守檢查值，不證明每種 OpenRouter data URL 映射均已驗證。圖片沿用 [API 素材格式](api-and-assets.md)；影片／聲音先採直接可下載的 HTTPS URL。原生 fetcher 不跟隨重新導向；避免登入頁、HTML 分享頁與需 cookie 的連結。HeyGen 原生 asset ID 不能當成 OpenRouter URL，也不為傳素材而自行公開上傳。

## 參考標籤與提示詞

HeyGen 原生文件的標籤是 `<Picture 1>`、`<Video 1>`、`<Audio 1>`，每種類型依輸入順序**獨立從 1 編號**。不是全部素材共用一個流水號。其他平台的 `@Image1` 不直接沿用。

OpenRouter 用 `input_references` 的 `image_url`／`video_url`／`audio_url` 項目；保留每類的相對順序，在 `source-map.json` 保存檔案、SHA-256、角色、陣列位置及原生標籤。標籤本身不會上傳檔案。OpenRouter 未提供 HeyGen 標籤重寫的公開實測，這裡依原生規則編寫；首次成片需驗證每項來源的遵循效果，不能只看到標籤就宣稱角色已鎖定。

提示詞可用原生範例的段落：`subject_definitions`、`summary`、`retention_analysis`、`detailed_description`、`overall_soundscape`、`non_diegetic_music`。這是可選製作結構，不是必填 JSON schema。明寫哪張圖保留身分／服裝，哪張圖只提供背景或風格，以及動作起訖、方向、鏡頭和秒數節奏。設定圖為同一人，不複製四視圖版面。

官方建議用具體鏡頭、材質、製作媒介、光線及音效描述，而不只寫「高品質」；文字標示短句逐字列出，長文依授權後製。現在原生文件 prompt 上限為 32,000 字元，舊版 changelog 的 5,000 是歷史快照。OpenRouter 若回報更嚴格限制，先保存錯誤再依 Skill 錯誤流程處理。

原生有 `prompt_enhancement: turbo/quality/disabled`，但 OpenRouter 的 passthrough 清單為空，不能自行送它，也不能保證提示詞未經上游增強。Seed 可用，但不承諾跨部署或跨路由永遠輸出相同檔案。

## 聲音

本模型的官方描述是生成帶音軌的整段影片；`generate_audio: false` 能力旗標不能證明靜音，也不能作為需要對白就拒絕選模的理由。HeyGen 原生沒有公開這個開關，因此 OpenRouter 請求**省略 `generate_audio`**，提示詞寫所需對白、音效及音樂。必要靜音需求先解決已授權後製或模型選擇；「不加音樂」不等於移除所有音軌。實際音軌及對白準確度要驗收。

## 價格與優惠

模型 API 的 SKU 是**美元／秒原價**，不是美分。供應商 endpoint 目前 `pricing.discount: 0.5`，模型頁顯示五折；HeyGen 公告說優惠至 2026 年 10 月底。不能永遠硬編碼五折，提交前核對兩個來源。

| 解析度 | 文字／首幀原價 | 文字／首幀五折 | 參考模式原價 | 參考模式五折 |
|---|---:|---:|---:|---:|
| 480p | $0.02/s | $0.01/s | $0.04/s | $0.02/s |
| 768p | $0.03/s | $0.015/s | $0.06/s | $0.03/s |
| 2K | $0.09/s | $0.045/s | $0.18/s | $0.09/s |

SKU 分別為 `duration_seconds_<解析度>` 與 `reference_duration_seconds_<解析度>`，2K 後綴為 `2k`。文字／首幀估價為輸出秒數 × 對應單價 × 當前折扣。5 秒 768p 五折約 $0.075；只有圖片參考的 5 秒 768p 按參考 SKU 約 $0.15。

有參考影片時，HeyGen 原生公告說輸入影片秒數加輸出秒數都計費，圖片和聲音不另加費。OpenRouter 沒有在公開 SKU 中分列輸入秒數及截短後的計費細節；估價須把來源／有效影片時長與這項不確定性列明，保守預留輸入成本，不能只報輸出秒數。完成後以 OpenRouter `usage.cost` 為實際費用。

## OpenRouter 圖片參考範例

假設已確認 5 秒、768p、16:9，採用人物設定圖和場景圖；網址須換成實際可讀素材。

```json
{
  "model": "heygen/heygen-video-1",
  "duration": 5,
  "resolution": "768p",
  "aspect_ratio": "16:9",
  "prompt": "subject_definitions: <Picture 1> 是已採用的人物設定圖，所有視圖為同一人；保留臉部、體態與服裝，不複製設定圖版面。<Picture 2> 提供咖啡店場景與照明。summary: 同一人物在店內看向窗外。detailed_description: 0–2 秒保持站姿，2–4 秒緩緩轉頭，4–5 秒停在面向窗外的姿勢。鏡頭固定中景，不新增人物。overall_soundscape: 輕微室內環境音，無對白。non_diegetic_music: 無音樂。",
  "input_references": [
    {"type": "image_url", "image_url": {"url": "https://example.com/character.png"}},
    {"type": "image_url", "image_url": {"url": "https://example.com/cafe.png"}}
  ]
}
```

影片與聲音項目使用 `{"type":"video_url","video_url":{"url":"https://example.com/motion.mp4"}}`、`{"type":"audio_url","audio_url":{"url":"https://example.com/sound.wav"}}`；有必要且已查證可讀時才加入，不為湊參考數量而新增素材。沿用 Skill 的提交、輪詢、下載及錯誤保存流程，建立 Skill 不涵蓋付費試片。

## 官方來源

- [OpenRouter 模型頁](https://openrouter.ai/heygen/heygen-video-1)
- [影片模型 API](https://openrouter.ai/api/v1/videos/models)：規格、SKU、seed 與 passthrough。
- [供應商 endpoint](https://openrouter.ai/api/v1/models/heygen/heygen-video-1/endpoints)：當前折扣；通用 `supports_image_reference` 欄位不替代影片專用模型描述。
- [OpenRouter 參考圖 cookbook](https://openrouter.ai/docs/cookbook/video-generation/reference-to-video)：素材欄位與需查模型描述的規則。
- [HeyGen 模型文件](https://developers.heygen.com/docs/models/heygen-video)：標籤、上限、素材規則、模式、輸出與提示詞建議。
- [HeyGen 官方發布與優惠](https://help.heygen.com/en/articles/17272995-introducing-heygen-video-generate-cinematic-clips-from-a-prompt)：10 月五折與參考影片輸入計費。

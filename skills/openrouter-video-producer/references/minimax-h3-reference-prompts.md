# MiniMax H3／H3 Max 素材引用與提示詞

查證日期：2026-10-01。此處整理官方提示詞寫作方式，供 OpenRouter 製作流程使用；不是固定 API schema。模型 ID 範例為 `minimax/hailuo-3`、`minimax/hailuo-3-max`，執行前仍查即時模型、供應商與能力。

## 先確認模式與實際介面

MiniMax 官方將 H3 分成文字生成 T2VA、首幀 I2VA、首尾幀 FL2VA、尾幀 L2VA，以及多素材參考 Ref2VA。官方的三段／六段格式是提示詞整理格式，放入 `prompt` 字串，不是新增的 JSON 請求欄位。[官方提示詞 Skill](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/SKILL.md)

H3 Max 的能力須按介面判斷：fal 的 reference-to-video 已列出圖片、影片與音訊參考，另有專門的 3d-to-video 介面供 Blender 預演使用。不能由此推定 OpenRouter 路由已提供所有能力，也不能將 H3 Max 一概記為只支援圖片。[fal 參考生成](https://fal.ai/models/minimax/h3-max/reference-to-video/api)、[fal 預演轉影片](https://fal.ai/models/minimax/h3-max/3d-to-video)

執行時查 OpenRouter 的 `input_modalities`、`generate_audio` 與供應商資料，按所需素材與聲音能力選模；不按 Max 名稱推定功能，也不將音訊輸入視為音色複製保證。[影片模型清單](https://openrouter.ai/api/v1/videos/models)、[H3 供應商資料](https://openrouter.ai/api/v1/models/minimax/hailuo-3/endpoints)、[H3 Max 供應商資料](https://openrouter.ai/api/v1/models/minimax/hailuo-3-max/endpoints)。

提交前一起建立素材對照表、`request.json` 與提示詞。對照表記錄本機檔案、素材類型、API 欄位、各類素材的提交順序、模型指代、採用／排除資訊及查證狀態。

- OpenRouter 的首尾幀使用 `frame_images`，一般內容／風格參考使用 `input_references`；兩者同時提供時，官方文件指出首尾幀模式優先。不把人物設定圖當首幀，也不承諾混合模式下所有素材仍生效。
- OpenRouter 只有支援的供應商才採用影片／音訊參考，其他供應商可能忽略。核對素材 schema、限制及指代映射；未核對時標示未驗證，不能只因欄位被接受就宣稱採用成功。
- fal 的素材 URL 欄位與提示詞擴寫設定不能直接當成 OpenRouter 欄位；供應商選項須先查 `allowed_passthrough_parameters`。
- 素材必須實際提交。寫上 `<Picture 1>`、`Video 1` 或本機檔名不等於上傳／綁定；不要把 Seedance 的 `@Image1` 指代照搬到 H3。
- 必要映射無法確認或發生錯誤時，依 Skill 的錯誤規則先說明並詢問使用者，不自行省略素材、換平台或付費試錯。

依據：[OpenRouter 影片指南](https://openrouter.ai/docs/guides/overview/multimodal/video-generation)、[提交 API](https://openrouter.ai/docs/api/api-reference/video-generation/submit-a-video-generation-request)。

## H3 多素材參考：數量與時長上限

MiniMax 官方 H3 Ref2VA 規則如下；這是上游模式的限制，不代表 OpenRouter 各供應商已完整支援。提交前核對當前路由，若有更嚴格限制，以該介面為準。

| 素材 | 最多數量 | 每個片段時長 | 同類片段總時長 |
|---|---|---|---|
| 圖片 | 9 張 | 不適用 | 不適用 |
| 影片 | 3 個 | 2–15 秒 | 最多 15 秒 |
| 音訊 | 3 個 | 2–15 秒 | 最多 15 秒 |

三類合計最多 **12 個素材**，不能同時用滿 9＋3＋3。音訊參考須搭配至少一張圖片或一個影片，不能只有音訊。首尾幀模式各最多一張首幀、一張尾幀，不能與多素材參考模式混用。

來源：[MiniMax 官方 H3 輸入限制](https://github.com/MiniMax-AI/cli/blob/main/skill/h3-video/references/h3-video.md)、[H3 官方說明](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/README.md)。不要將 CLI 自身的上傳大小限制直接視為 OpenRouter 的限制；規格不明時查證或詢問，不以付費試錯推測上限。

## 文字／首尾幀：三段格式

依序寫 `integrated_multimodal_description`、`overall_soundscape`、`non_diegetic_music`。純文字直接開始；首幀／尾幀模式先在首行交代圖片對齊的時間和鏡頭，再空一行接正文。描述首幀之後的發展、首尾幀之間的合理過程，或逐漸收束到尾幀；不要只有「照圖片生成」。

正文按播放順序寫構圖、人物、環境、動作、運鏡與對白。`[Shot 1]` 不加切鏡時間；後續鏡頭使用 `[Shot 2] At 00:03.500, ...`，時間遞增且在本次片長內。單一鏡頭的動作節拍不另編成切鏡。運鏡寫入事件中，必要時交代幅度與速度。

描述用英文；對白、歌詞和畫面文字保留使用者原文。說話者採穩定 `(S1)`、`(S2)`，對白使用 `<d>[Chinese] ...</d>`；語氣、動作與說話者身分寫在標籤外。旁白須明說畫外音，避免畫面人物跟著說話。環境聲放 `overall_soundscape`，觀眾才聽得到的配樂放 `non_diegetic_music`；沒有配樂寫 `N/A`，不要因此消除環境聲。

來源：[官方文字／關鍵幀指南](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/references/base-en.txt)。複雜的跨鏡對白、截斷及關鍵幀對齊，執行時讀原指南的完整規則。

## H3 多素材參考：六段格式

MiniMax 原生 Ref2VA 依序使用下列六段；英文描述，對白保持原語言。這是格式骨架，正式正文要展開本次畫面與聲音，不能只交付素材關係清單。

```text
subject_definitions:
Define each subject, its source and reference role.

summary:
[reference generation + audio reference] Describe the target and reference relationships.

retention_analysis:
Explain which characteristics are retained, changed or transferred.

detailed_description:
[Shot 1] Describe composition, action, camera, dialogue and reference use.

overall_soundscape:
Describe ambience and physical sounds.

non_diegetic_music:
N/A
```

原生標籤的用途：`<Subject N>` 是可沿用的人物、道具或場景；人物外觀來源可在此引用 `<Picture N>`。圖片自身作首幀、尾幀或構圖錨點時才另定義；`<Video N>` 指影片的結構、修改來源或接續來源；`<Audio N>` 指實際提供且啟用的音訊。各類獨立編號，全篇保持同一含義。影片內含聲音不代表自動建立音訊引用。

`retention_analysis` 區分視覺的 `fully_preserved`、`partially_preserved`、`attribute_transfer`、`weak_reference`，以及音訊的 `fully_copy`、`partially_copy`、`reference`、`weak_reference`。只借運鏡的影片屬參考生成，不誤寫成修改原片；借音色也不誤寫成複製原錄音。

來源：[官方 Ref2VA 指南](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/references/ref-en.txt)。提交前依原指南補齊時序、素材生效位置與聲音關係；不能把原生標籤未經核對就宣稱為 OpenRouter 的綁定規則。

## H3 Max：fal 的寫法與限制

fal reference-to-video 的提示詞以 `Image 1`、`Image 2`、`Video 1`、`Audio 1` 等指代各類清單的順序；不是混合清單的總索引。它接受自然語言，再依 `prompt_expansion_mode` 決定是否擴寫：`disabled`、`balanced`、`quality`。這是 fal 的介面規則，不強制當作所有 H3 Max 路由的規則。

截至查證日，該介面列出參考素材合計最多 12 檔；影片與音訊片段各為 2–15 秒，各自合計最多 15 秒。首尾幀另有 `image_url`、`end_image_url`。這些限制只適用該介面，執行時重查，不直接用作 OpenRouter 的通用限制。

可用下列自編寫法表達責任；素材順序須對應實際輸入：

```text
Image 1 defines the woman's face and clothing.
Video 1 guides blocking and camera movement, not the proxy appearance.
Audio 1 guides her voice timbre; generate the new dialogue below.
She enters, stops beside the counter, and says in Mandarin: "你終於回來了。"
Keep her facial identity consistent. Quiet room ambience, no background music.
```

來源：[fal H3 Max reference-to-video API](https://fal.ai/models/minimax/h3-max/reference-to-video/api)。不要未經查證就停用擴寫或填入供應商參數。

## 導演素材的責任與驗證

已選定人物圖決定該角色的臉部、髮型與服裝，依[人物來源選擇與一致性](api-and-assets.md#人物來源選擇與一致性)沿用素材包的檔案及版本，不換回原照。採用四視圖設定圖時，頭部特寫提供主要臉部身分，三個全身視角提供體態與服裝；所有視角只代表同一人，多視角版面不搬入成片。Blender 預演提供走位、運鏡、事件順序與空間關係，排除代理模型外觀與預演原音。場景／道具圖片提供其外觀；音訊需明說借音色並生成新台詞、沿用節奏或保留原音。逐字、逐樣本保留原音的需求須另核對能力或安排已授權的後製，不能只憑提示詞承諾。

人物的臉部身分要求寫進相應定義、保留分析與畫面描述；不改壞官方段落順序。無人物時明說不新增人物；缺人物圖時依文字設定，不虛構人臉參考。

## 提交與驗證

素材 URL 須符合當前 API schema，遠端影片須可直接讀取媒體內容，不能將分享預覽頁當成影片檔。核對實際提交來源與已確認素材一致；提示詞標籤須對應素材類型及順序。

在影片專案保存請求、工作 ID、實際費用、媒體資訊與檢視結果，分清提交成功、素材採用及成片品質。個案工作紀錄與使用者回饋留在專案，不寫入公用 Skill。

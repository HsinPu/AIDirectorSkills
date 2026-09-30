---
name: openrouter-video-producer
description: 透過 OpenRouter API 生成影片，支援文字、首尾幀與參考素材輸入，以及既有工作的查詢、恢復和下載。使用者指定 OpenRouter 製作影片或接續其生成工作時使用。
---

# OpenRouter 影片製作

將提示詞與素材轉為 OpenRouter 影片生成工作，保存工作 ID，完成後下載實際影片。可獨立使用，也可接續導演交付的逐鏡或生成單元素材包；不要求先完成 Blender 預演。使用臺灣繁體中文溝通，保留 API 欄位與模型 ID。

## 工作方式

1. **先讀既有資料。** 確認本次提示詞、素材、輸出位置，以及有無既有 `job.json`。使用者要求查進度、恢復或下載時，沿用工作 ID，不提交新工作。
2. **查模型再選參數。** 使用 `GET /api/v1/videos/models` 取得即時能力與價格。尊重使用者指定模型；委託選擇時依片長、比例、聲音、參考素材及成本選擇並記錄理由。`supported_durations` 是離散秒數集合，不當作範圍。缺少能力資訊時查官方文件，不把缺欄位解讀為支援。
3. **準備可檢視的提交內容。** 在生成單元內保存 `request.json`，填入 `model`、`prompt` 與已驗證的參數。明確設定 `generate_audio`，不要依賴預設值；需要音訊但模型不支援時先解決需求。圖片輸入及供應商參數見 [API 與素材對應](references/api-and-assets.md)。
4. **依已授權範圍提交。** 要求生成影片即可涵蓋該次提交；只查 API、規劃、估價或建立 Skill 不涵蓋付費生成。若模型／預算尚未確定且會影響執行，補齊必要資訊。API Key 只從 `OPENROUTER_API_KEY` 環境變數讀取，缺少時請使用者在本機設定，不請使用者貼入對話。
5. **保存與接續工作。** 提交得到 `202` 和工作 ID 後立即保存 `job.json`，告知已提交。每約 30 秒查詢一次並更新紀錄。`completed` 才能下載；`failed`、`cancelled`、`expired` 停止並報告錯誤。未知狀態或超過本次等待時間時保留工作供接續，不宣稱失敗或自動重送。查詢／下載的暫時性失敗可有界重試；提交逾時的結果可能已接受，先查帳號活動或既有紀錄，不能直接重送。
6. **下載並交付。** 對 OpenRouter 的 content endpoint 使用同一認證，按輸出索引下載。確認本機檔案非空；有媒體工具時確認可解碼、時長、解析度與音軌，未完成的檢查明列。API 成功不代表角色一致性或畫面品質已通過；能播放或查看實際結果時再評估。交付影片連結、工作 ID、實際 `usage` 費用及未驗證項目。

## 解析度與畫面比例：先查，再問

生成前讀 [官方解析度與畫面比例設定](references/output-settings.md)，並查所選模型的即時 `supported_resolutions`、`supported_aspect_ratios`、`supported_sizes`。使用者沒指定時，先找官方支援選項，再主動詢問缺少的解析度與比例；不要要求使用者自行查規格，也不要自行套用範例中的 `720p` 或 `16:9`。

已在目前製作範圍確認的設定直接沿用，不重問；使用者提供支援的精確 `size` 時，可由尺寸取得所需輸出規格。只缺一項就只問該項。詢問時列出模型可用選項與簡短建議，例如橫式 `16:9`、直式 `9:16`，以及較清晰或較省成本的解析度。未回答前可準備素材與提示詞，但不提交付費生成；只有使用者已明確委託選擇時，才代選並記錄理由。要求的規格不受支援時，說明可用替代選項，不靜默降級、裁切或更換模型。

## 接續導演素材包

使用 Seedance，尤其圖片、影片與聲音混合參考時，先讀 [Seedance 素材綁定與提示詞](references/seedance-reference-prompts.md)。其中 Seedance 2.5 的範例是參考，不是固定 API 規格；當下 API／供應商規則不同時，依查證結果重寫素材綁定與提交規則，保留使用者的創作意圖。

- 先讀使用者指定的 `prompt.md`、`shot-manifest.json` 或生成單元紀錄。多鏡單元仍是一次提交；逐鏡資料夾不自動各付費生成。
- 保留已確認的故事、角色、臉部身分、運鏡、聲音及接點要求。沒有角色的影片明寫臉部身分要求不適用；沒有參考圖時使用文字設定，不虛構身分綁定。
- 原平台的 `@imageN`／`@videoN` 不等於 OpenRouter API 綁定。建立檔案到 API 輸入欄位的對照，將提示詞改為實際可解析的來源描述；不把 Blender 結構預演誤作最終美術。
- 模型不能使用某種影片／聲音參考時，不靜默省略。調整模型或與使用者解決需求，再提交。
- 輸出與紀錄存放在該影片專案，保留逐鏡素材包的獨立性；不要存入 Skill 原始碼資料夾。每個生成單元或每次授權的新嘗試使用不同目錄，避免覆蓋舊成果。

## 輔助程式

Python 3，無額外套件。以下路徑相對於本 Skill 根目錄；實際執行時使用程式與專案檔案的完整路徑。

```text
python scripts/openrouter_video.py models --out <project>/models.json
python scripts/openrouter_video.py submit --request <unit>/request.json --job <unit>/job.json
python scripts/openrouter_video.py status --job <unit>/job.json
python scripts/openrouter_video.py download --job <unit>/job.json --out <unit>/video.mp4
```

程式每次只查詢一次，由助理安排輪詢與進度更新；不建立常駐服務。提交前自動驗證模型公開列出的基本能力，不代替供應商參數或參考素材能力的查證。已有工作紀錄時拒絕重新提交；下載先寫 `.part` 再改名。程式不會自動重送 POST，也不會自動把帳號認證傳到外部影片 URL。

## 來源與限制

依 [OpenRouter 官方 Skill](https://github.com/OpenRouterTeam/skills/blob/main/skills/openrouter-video/SKILL.md) 的提交、輪詢、下載流程自行編寫，查證日期為 2026-09-30；不是官方 Skill 的逐字副本。模型、價格、供應商能力以執行時資料為準。

- [影片生成指南](https://openrouter.ai/docs/guides/overview/multimodal/video-generation)
- [生成 API](https://openrouter.ai/docs/api/api-reference/video-generation/submit-a-video-generation-request)
- [模型 API](https://openrouter.ai/docs/api/api-reference/video-generation/list-all-video-generation-models)

影片生成不支援 ZDR；若帳號強制 ZDR，官方不會路由影片請求。保留既有隱私設定，告知限制，不自行停用。

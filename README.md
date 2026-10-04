# AIDirectorSkills

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**從故事、漫畫式分鏡圖或 Blender 預演，到透過 OpenRouter 生成影片的 AI 導演 Skills。**

以臺灣繁體中文記錄創作決策、整理角色與場景素材，讓 AI 助理能接續同一個影片專案。適合製作獨立短片、連續故事中的指定場景，以及需要參考素材的 AI 影片。

## 提供的 Skills

| Skill | 用途 | 主要交付 |
|---|---|---|
| [film-director](skills/film-director/SKILL.md) | 故事開發、劇本、分鏡、資產，以及圖片或 Blender 預演參考 | 劇本、鏡頭表、角色／場景素材、分鏡參考圖片或影片、生成提示詞 |
| [openrouter-video-producer](skills/openrouter-video-producer/SKILL.md) | 透過 OpenRouter API 生成影片，查詢、恢復與下載工作 | 提交內容、工作紀錄、生成影片、API 回報費用 |

兩個 Skill 可各自使用，也可接續：先由導演 Skill 完成鏡頭設計與素材包，再交給 OpenRouter Skill 生成影片。

## 安裝到 Codex

在 Codex 對話中使用內建的 `$skill-installer`：

```text
$skill-installer 請從 https://github.com/HsinPu/AIDirectorSkills 安裝
skills/film-director 和 skills/openrouter-video-producer 這兩個 Skill。
```

也可以下載本儲存庫，將需要的完整 Skill 資料夾複製到 Codex 的技能目錄。依[官方文件](https://learn.chatgpt.com/docs/build-skills)，個人技能目錄為 `~/.agents/skills/`，專案技能目錄為 `<project>/.agents/skills/`；每個 Skill 的 `SKILL.md`、`references/`、`scripts/` 等檔案應一起保留。安裝器採用的路徑以實際環境為準。

Codex 會自動偵測技能；若未出現，重新啟動 Codex。其他支援 Skills 的 AI 用戶端，依該用戶端的安裝規則放置完整資料夾。

## 快速開始

### 創作或接續影片

```text
$film-director
幫我製作一段發生在客廳的短片。先討論故事，再一起呈現劇本與分鏡表。
```

既有專案沿用原本的位置；新專案預設建立在目前可寫入工作區的 `director-projects/`。創作設定與回饋保存在影片專案，方便後續修訂與接續。

### 使用 OpenRouter 生成影片

```text
$openrouter-video-producer
使用 Seedance 2.5，依照這個生成單元的 prompt.md 與素材製作影片。
先查支援的解析度、比例與參考素材規則；未指定的輸出設定請問我。
```

OpenRouter Skill 會查模型能力，整理素材與提示詞對照，保存 `request.json` 與 `job.json`，再查詢進度並下載成果。中斷後可沿用原工作 ID 接續。模型、價格及規格以執行時的官方資料為準。

## 功能特色

- **創作決策可接續**：記錄故事範圍、角色、攝影、色彩、聲音與使用者回饋。
- **劇本與鏡頭一起檢視**：讓敘事、表演、分鏡與運鏡意圖一起審閱。
- **三種參考路線**：A 漫畫式分鏡圖、B Blender 預演、C Hyper3D 素材＋Blender 預演；劇本與鏡頭表確認後選擇，已有答案就沿用。
- **漫畫式分鏡圖片**：預設每鏡一張、每張六格，逐格呈現那幾秒內的景別、動作與運鏡；全片整批審閱後交付乾淨單格與提示詞。六鏡即六張、共36格，格線不增加切鏡；圖片路線無須 Blender，亦可採用使用者指定版型。
- **Blender 結構預演**：以簡化角色與場景表達空間、走位、接觸與攝影機路線。
- **逐鏡素材包**：每鏡保留所需素材副本；多鏡生成另外提供可獨立提交的生成單元。
- **混合參考素材**：為 Seedance 等支援模型整理圖片、影片與聲音的用途及提示詞指代，依當下供應商規則更新。
- **先查規格再詢問**：使用者未指定解析度與比例時，先取得模型可用選項，再詢問；已確認的設定不重問。
- **生成工作可恢復**：保存工作 ID；提交結果未知時不盲目重送，避免重複生成。

## 執行需求

| 工作 | 需求 |
|---|---|
| 訪談、劇本、分鏡與提示詞 | 支援 Skills 的 AI 用戶端 |
| 漫畫式分鏡圖 | 可用的影像生成／編輯工具，或使用者提供圖片；實際影片模型須支援所選圖片參考方式 |
| Blender 預演 | Blender；透過 MCP 操作時需可用的 Blender MCP 連線 |
| OpenRouter 輔助程式 | Python 3.8+，僅使用標準函式庫；本專案於 Python 3.12 驗證 |
| OpenRouter 影片生成 | 網路、`OPENROUTER_API_KEY` 與足夠帳號額度 |

Blender MCP 的設定方式見[連線與安裝指引](skills/film-director/references/blender-mcp-setup.md)。只有實際使用相關製作階段時才需要其工具。

OpenRouter API Key 由環境變數讀取。請在本機設定，勿寫入儲存庫或貼進對話；影片生成可能消耗帳號額度。建立計畫、查規格與估價不會自動提交生成。

## OpenRouter 工具與參考

在儲存庫根目錄執行：

```shell
python skills/openrouter-video-producer/scripts/openrouter_video.py --help
```

程式提供 `models`、`submit`、`status`、`download` 四個命令。模型能力、提交內容、工作紀錄與影片存放在使用者的影片專案中；詳細操作見 [Skill 入口](skills/openrouter-video-producer/SKILL.md)。

- [API 與素材對應](skills/openrouter-video-producer/references/api-and-assets.md)
- [Seedance 素材綁定與提示詞](skills/openrouter-video-producer/references/seedance-reference-prompts.md)
- [解析度與畫面比例](skills/openrouter-video-producer/references/output-settings.md)

## 專案結構

```text
AIDirectorSkills/
├── skills/
│   ├── film-director/
│   │   ├── SKILL.md
│   │   ├── agents/
│   │   ├── references/
│   │   └── scripts/
│   └── openrouter-video-producer/
│       ├── SKILL.md
│       ├── agents/
│       ├── references/
│       └── scripts/
├── README.md
└── LICENSE
```

影片工程與生成成果保存在獨立的影片專案中，不放進 Skill 原始碼資料夾。

## 驗證與貢獻

OpenRouter 輔助程式的離線測試不需要 API Key，也不會提交生成工作：

```shell
python -B -m unittest discover -s skills/openrouter-video-producer/scripts -p test_openrouter_video.py -v
```

目前七項離線測試涵蓋參數能力、提交逾時後避免重送、工作接續，以及下載內容與完整性檢查。這些測試不代表實際生成畫面品質或混合素材綁定已驗證；Seedance 經 OpenRouter 的素材指代效果仍需實際生成查證。

歡迎提出 Issue 或 Pull Request。修訂 API 或模型規則時，請附官方來源與查證日期，區分文件規格和實測結果。可閱讀文字使用臺灣繁體中文，API 欄位、模型 ID 與檔名保留原文。

## 授權與致謝

本專案以 [MIT License](LICENSE) 開源，授權全文見 `LICENSE`。第三方平台、模型與工具仍依各自條款使用。

OpenRouter Skill 參考 [OpenRouter 官方 openrouter-video Skill](https://github.com/OpenRouterTeam/skills/tree/main/skills/openrouter-video) 的非同步生成流程自行編寫，並針對 Windows、工作恢復與導演素材交接調整。

# AI 導演 Skills

這個儲存庫收錄 AI 導演 Skills。目前提供 [film-director](skills/film-director/SKILL.md)，協助製作獨立短片，或連續故事中指定的場景與章節。工作流程涵蓋創作訪談、劇本、分鏡表、角色與場景資產、Blender 結構預演、參考影片，以及可用於製作的 AI 影片提示詞。

請在支援 Skills 的環境中呼叫 `$film-director`。既有專案沿用原本的位置；新專案會在目前可寫入工作區的 `director-projects/` 底下建立獨立資料夾，不必先指定目錄。Skill 本身位於 `skills/film-director/`，製作檔案則存放在專案資料夾。

技能入口是 `SKILL.md`；[openai.yaml](skills/film-director/agents/openai.yaml) 提供介面中繼資料。各流程的詳細規範由入口連到 `references/`，需要執行的輔助工具則由相關規範連到 `scripts/`。

另提供 [openrouter-video-producer](skills/openrouter-video-producer/SKILL.md)（OpenRouter 影片製作），參考官方 Skill 自行編寫。使用 `$openrouter-video-producer` 可透過 OpenRouter API 生成影片，或查詢、恢復與下載既有工作；可直接使用，也可銜接導演的逐鏡與生成單元素材包。需要 Python 3 與本機 `OPENROUTER_API_KEY` 環境變數，輔助程式不需額外套件。影片與工作紀錄存放在影片專案內。

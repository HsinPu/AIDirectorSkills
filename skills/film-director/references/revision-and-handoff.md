# 修訂、專案狀態與交接（1.1）

製作資料存放在依[專案文件](project-documentation.md)選定的專案根目錄。已安裝的技能只保存規則與工具。根目錄包含 PROJECT.md 和 project-state.json；可視需要設 canon/、story/、revisions/、assets/、blender/、exports/ 等職責資料夾。不要保存完整對話紀錄、金鑰或無關的本機資料。

專案的來源、輸出、影像及 blend 路徑，都以專案根目錄為基準，使用 / 分隔。絕對路徑只在執行時暫時解析，不寫進 SceneSpec、狀態、提示詞或交接檔。共享素材庫可放在其他位置，但專案應使用穩定素材 ID、確切版本與已登錄的素材庫參照，不記錄使用者名稱或電腦路徑。

## 狀態與標記

project-state.json 是機器可讀的單一現況入口；PROJECT.md 提供人員摘要。接續工作時，先讀狀態、目前場景、相關已確認設定、前後連續性及未決問題，再提問或製作。追蹤 project_kind、current work_scope、單集進度、last_checkpoint 及 resume_context。區分已寫但尚未製作的章節，與尚未撰寫的故事。creative_documents 索引訪談、具名角色、攝影／色彩、劇本及完整分鏡；stage_reviews 分別記錄靜態與動畫的展示及意見。不要捏造缺失的舊訪談。

專案狀態可包含 project_id、root、title、approved_revision、working_revision、parent_revision、active_scene_id、development_stage、approval_status、帶有 path／scope／status 的 source_of_truth 紀錄、accepted_decisions、delegated_choices、open_questions、帶相依與狀態的 artifacts，以及 drift 項目。若出現舊版 revision_id，必須等於 working_revision。舊版純字串的 source_of_truth 清單可依根目錄讀取，但重寫時應加入路徑、範圍與事實狀態。已確認或明確委託的選擇，可在指定範圍內成為授權來源；提案與推測不可冒充既定設定。

成果狀態：planned（未製作）、working（工作修訂中的草稿）、approved（已核准修訂中的成果）、superseded（歷史版本）、stale（特定相依項已變更）、drifted（實際 Blender／輸出與登錄約定不同）、unverified（存在但未就所述事項查證）、missing（登錄檔案不存在）。下次寫入時，將舊版 current 正規化為 working 或 approved。

## 變更傳遞

不要混用 approved_revision 和 working_revision。新想法、變更或分支建立工作修訂；首份草稿可用 r0001。修訂資料夾只存本次使用或更新的計畫、鏡頭、SceneSpec、素材參照、提示詞、變更紀錄與交接資訊；未變動資料可明確引用來源。只有真正執行檢查，才儲存驗證報告。模型／動畫核准時，指出採納的修訂並升為 approved，進入 prompt_export 並交付；不要額外遞增創作修訂或編造技術審閱。

故事、目標、拓樸、重要道具、場景節奏、鏡頭、路徑、動畫或參考資料變更時：

1. 在 working_revision/change-log.md 記錄請求、原因、變動欄位、影響範圍及保留的證據。
2. 同步使用這些欄位的專案摘要、設定／連續性、場景計畫、分鏡、SceneSpec 與提示詞。已採納快照保留作歷史，現況入口須說明何者取代何者。
3. 只將實際相依的成果標為 stale，並具體標記範圍。文字、標籤或非結構性外觀變動，不會使未變動的 Blender 幾何、動作或攝影機失效。
4. 更新目前需要的過期成果；選用的軌跡、審閱影像或技術證據可維持 stale／unverified。修訂後的模型／動畫核准，不以選用項目重新稽核為前提。

精確重用位置時，鎖定 asset_id 加 asset_version。新的共享版本不會自動取代舊場景；場景專用變體只影響使用它的場景。提示詞措辭或綁定可有獨立 prompt_revision，同時保留已核准的動畫和外觀版本。提示詞若修正事實矛盾，也要更正目前設定與分鏡，不得留下相反的現況說法。取消被否決方案衍生的工作，舊檔保留作歷史，不依最新檔名自動選用。

將意見分為修正、創作變更、局部接受或整版採納。明確的修正可直接套用，不要求使用者重述。判斷影響的是文字、來源、外觀、動作、結構或攝影機，保留其他已採納要求。記錄實際變更及證據。使用者接受修訂成果後即可停止，不自動加做其他變體。

## 偏移與交接

已知的 Blender 手動修改若影響提示詞事實，記錄實際差異，只同步相關鏡頭、時間、路徑／朝向、道具歸屬或連續性欄位。先使用使用者回報與既有紀錄，必要時才做最小範圍唯讀查詢。核准後不掃描整個場景尋找假設性偏移。實際採納的差異可整合進工作修訂，或記為已核准例外。未經指示，不丟棄或覆寫使用者的 Blender 修改。缺少選用測試或參考影片不屬於 drift。

revisions/r####/handoff.md 的交接內容應指出專案 ID、相對於根目錄的路徑、已核准及工作修訂、目前場景、素材 ID／版本／實例、目前來源、stale／drifted 成果、已驗證範圍與未決問題。對話摘要或未登錄的絕對路徑不足以交接。連載故事還需記錄最後事件、角色／道具最終狀態、觀眾與角色各自已知資訊、後續已寫但尚未製作章節、未寫段落，以及下次接續的檔案與階段。完成一段不等於完成或授權整個系列。

## 分別記錄交付狀態

prompt_export 是流程階段，不代表影片、美術素材、上傳或生成影片已存在。以真實檔案與待辦工作追蹤 text_status、reference_video_status、appearance_assets_status、upload_binding_status 和 generation_status。附件尚未齊全時可先有條件草稿，但約定要交付的影片或角色影像若仍未完成，不能宣稱整體交接完成。匯出相同的已核准動畫，不變更創作修訂，也不觸發審閱。舊版 prompt_ready 影像狀態視為 planned；registered 表示已編目，核准與否由 review_status 記錄。

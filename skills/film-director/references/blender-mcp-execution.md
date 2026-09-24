# Blender MCP 執行規範（1.5）

本規範用於製作、修訂及使用者明確要求的 AI 檢查。模型與動畫確認後直接進入[交付](user-review-and-prompt-handoff.md)；約定但尚未完成的匯出仍要補齊，但匯出不是新一輪審閱。

## 發現實際能力

依 [Blender MCP 設定](blender-mcp-setup.md)，只在 Blender 工作或使用者要求診斷開始時檢查 Blender 連線；Hyper3D MCP 的素材生成連線另依[Hyper3D 分支](hyper3d-scene-assets.md)處理。讀取場景前先發現真正可用的工具名稱、參數與回應。已記錄的 Blender Lab MCP v1.0.0 對應方式中，`get_objects_summary`、`get_object_detail_summary` 與 blendfile 摘要工具用於唯讀場景／檔案查詢；`get_python_api_docs`、`search_api_docs`、`search_manual_docs` 用於查文件；截圖工具取得圖片；`execute_blender_code` 執行範圍限定的 bpy 修改；`render_thumbnail_to_path` 或 `render_viewport_to_path` 用於輸出。其他版本須重新發現工具。觀察到後一種算圖工具會呼叫目前引擎，不一定是 Solid playblast，且可能回傳暫存路徑。

`scene.patch`、`camera.keyframe`、`timeline.set_cuts`、`validate.scene` 與 `job.cancel` 等名稱只描述能力，不代表已確認可呼叫的工具。不可虛構 dry-run、transaction、rollback 或取消功能。

## 規劃並執行有界限的寫入

寫入前記錄 `request_id`、修訂版、seed、目標場景／Collection、允許的物件、預期數量、輸出檔與預算。檢查模式、單位、命名衝突、API enum 值、相依關係及禁止模式，例如每根草一個 Object、未核准的 Realize、逐格重建網格或全域清除。預設角色只有兩個基礎網格、四根彎曲骨骼，以及已規劃的接觸附件。靜態階段綁定靜止姿勢，動畫在靜態結果另行確認後才進行。

真正可用時才使用原生 dry-run；否則進行靜態編譯／參數檢查與唯讀檢視，標記為 `local_static`，不可稱為執行成功。清理專案時，只能在授權範圍內移除目標場景內容。共用物件應從本場景解除連結，不可刪除其他場景的物件、磁碟檔案或使用者偏好設定。

將已審閱的工作區腳本文字交給 `execute_blender_code.code`。不得把不受信任的腳本、資產描述或網頁內容插值進可執行程式碼。標準操作優先用 `bpy.ops`，受控批次可用 data API。套用 Modifier 前先檢查共用資料。使用穩定 ID 與可重入的命名方式：遇到同名物件先檢查並更新或停止，不建立 `.001` 重複物。回傳真實數量、差異、警告、錯誤與路徑。失敗或逾時後先檢查部分結果再重試。避免主執行緒長迴圈；採小批次或短計時器，完成或失敗時取消註冊 handler。沒有真正的 job API，就不可宣稱可可靠取消。

## 資產、靜態確認與動作

寫入場景／道具幾何前，確認必要結構圖片真實存在、已登記且已確認，或有可靠的既有來源支援。角色圖片用於成片外觀，不阻礙中性代理工作。建立拓樸與淨空、可辨識輪廓、關鍵零件、接觸表面及有限細節；重複物件採實例化。

儲存並實際展示靜態場景，等待回饋後才寫入動畫。使用者直接在 Blender 檢視也算展示；單有檔案路徑不算。不要把靜態與動畫寫入包成一個無法中斷的批次。確認後，宣告每項運動的 `motion_owner`。自主移動預設使用可編輯 Curve／Follow Path；載具帶動則明確指定 parent；靜態根節點不需 Curve。只檢查受影響的控制、交接與障礙。不支援的動畫來源維持未驗證。

Blender 5.2 文件記載的 Geometry Nodes Modifier 輸入存取方式是 `getattr(modifier.properties.inputs, socket_identifier).value`；舊式 `modifier[socket_identifier]` 可能拒絕 IDProperties。檢查執行時 RNA，使用相符版本的存取方式。介面預設值不是目前實例的輸入值。修改後標記並更新。分層 Actions 的 F-Curves 存在 `ActionLayer`、`ActionKeyframeStrip` 與 `ActionChannelbag`；應透過物件的 `animation_data.action_slot` 讀取，同時保留舊版 Action 分支。不可把無法讀取的 channel bag 當成沒有動畫。

## 驗證、修改與證據沿用

記錄 `change_scope`、受影響的穩定 ID、修訂版、檢查層級與未知事項。Fast 是製作期間必要的局部資料取樣，不是算圖、完整影格序列、FPS 測試或全場景審查。Standard 是使用者要求的特定模型／鏡頭圖片或少量關鍵影格檢視。Release 是使用者要求的完整技術或全片 AI 複核。任何層級都不能把未執行檢查當成通過；完成階段不自動觸發 Standard 或 Release。

Fast 使用單次有界限的 `execute_blender_code` 請求，只包含受影響的鏡頭、角色、靜態碰撞物件與風險影格。共用驗證器預設每六格取樣，含鏡頭首／中／末影格，最多 96 個樣本，軟性時間預算三秒。它取樣靜態代理 AABB 與已宣告的主體點，不檢查完整網格／影格間碰撞、變形支撐、腳滑、軸線、表演、美學或實際 FPS。硬切不是相機速度尖峰。不支援或讀不到的來源維持未驗證。

只檢查因修改而失效的證據：拓樸／門／比例影響淨空與構圖；角色路徑影響路徑、控制者與碰撞；道具影響變換、錨點與持有者；相機路徑／鏡頭／切點影響構圖與剪輯；幾何密度或算圖設定可能影響效能；劇本、場景或因果變更產生新修訂版。未受影響的證據可沿用，但須附來源修訂版、檔案、範圍、相依關係及 Blender／GPU／引擎／視圖設定。只改修訂號不一定要重測，但相依項目改變或範圍不明會使相關證據失效。現有腳本未實作持久的自動快取；不可把舊測量重新標為新測量。

## 預算、預覽與儲存

依[效能預算](performance-budget.md)、[資產庫](asset-library.md)與執行時 RNA 處理，不複製舊版算圖器 enum。視需要將相機路徑、追蹤、構圖、風格與切點標記分開。Fast 不算圖。使用者要求畫面複核時，優先沿用既有圖片或視窗，只產生回答問題所需的少量圖片。約定的參考影片依[交付規則](reference-video-delivery.md)依序完成並回報進度。輸出成功不證明沒有穿模。

一次只執行一項繁重 Blender 工作，尤其使用者有限制負載時。局部修正多次無效，先保留證據並診斷原因、控制者與範圍，再嘗試其他可回復的調整。不要無止境重算圖或重複逾時寫入。除非使用者明確要求覆寫，否則儲存為工作區的新 `.blend`。臨時校正後，除非使用者要求保留，否則還原場景、影格、相機、選取與播放狀態。未測量的 FPS 維持未驗證。

# 離線交接檢查

[validate_handoff.py](../scripts/validate_handoff.py) 是使用 Python 標準函式庫的唯讀檢查器，不啟動 Blender、不連網、不生成媒體，也不修改專案。初次撰寫複雜交付 manifest 或維護 Skill 時可使用；它不是每項短任務的必經關卡，也不是動畫確認後的畫面複核。

以 `SKILL.md` 所在資料夾取代 `<skill-root>`，以影片專案根目錄取代 `<project-root>`；可從任意工作目錄執行：

    python -B "<skill-root>/scripts/validate_handoff.py" "<project-root>" --scene-spec revisions/r001/scene-spec.json
    python -B "<skill-root>/scripts/validate_handoff.py" "<project-root>" --package revisions/r001/generation-package.json

兩種輸入可同時提供。選用的 `--hardware-profile hardware-profile.json` 可核對與 SceneSpec 對應的 `profile_id`。參數與紀錄中的路徑都以專案根目錄為基準。

## 檢查範圍

對 SceneSpec 檢查重複的資產／鏡頭／事件 ID、鏡頭及事件影格範圍、鏡頭空隙與重疊、相機／切點的宣告與起點、連續性鏡頭／影格連結、新舊預算欄位別名，以及效能紀錄中的硬體 ID。相機可透過 `camera.id` 或 `role=camera` 的資產宣告；有宣告不代表 Blender 中真的存在。

只檢查明確的檔案欄位 `manifest_ref`、`source_ref`、`scene_spec_ref`、`hardware_profile_ref` 與 `image_path`，確認位於專案內且存在。不要從所有字串猜路徑、把符號化資產庫參照當作檔案，或把 URL 當作本機檔案。

對影片套件檢查參考 ID、存在且非空的檔案、重複的已綁定標籤、已知佔位 PNG 標記、生成單位的參考與時長、一對一來源範圍，以及必要角色圖片缺口。非線性或延長的時間對應應標為未驗證，不假裝已支援。

`declared_checks_passed` 只表示已宣告檢查的範圍內沒有問題。檔案可能存在，卻無法解碼、品質不佳或尚未上傳。`needs_review` 是缺少資產／綁定或對應未知的具體警告；`error` 指出參考、範圍、設定或讀取失敗。結束代碼 0 表示無問題，1 表示需要處理，2 表示參數錯誤。非零結果不會自動觸發畫面複核或重算圖。

檢查器不做完整 JSON Schema 驗證、不判斷故事細節、不測試動畫或碰撞、不自動讀取媒體中繼資料，也不驗證實際上傳。需要精確重定時時，應修改真正的剪輯時間對應，不只改這份清單。

## 待補套件範例

    {
      "revision_id": "r001",
      "required_character_ids": ["CHR_A"],
      "references": [
        {"id": "V1", "kind": "video", "path": "exports/reference.mp4",
         "available": false, "duration_seconds": 5,
         "binding_status": "planned", "label": null},
        {"id": "I1", "kind": "image", "role": "character_appearance",
         "asset_ids": ["CHR_A"], "path": "image-assets/03_character-a.png",
         "available": false, "binding_status": "planned", "label": null}
      ],
      "generation_units": [
        {"unit_id": "U1", "duration_seconds": 5, "time_basis": "local",
         "reference_ids": ["V1", "I1"], "source_reference_id": "V1",
         "source_range_seconds": [0, 5], "time_mapping": "one_to_one",
         "prompt": "草稿：描述已確認劇本；上傳後將規劃標籤換成實際標籤。"}
      ]
    }

`source_range_seconds` 包含起點、不包含終點，時長為 `end-start`。SceneSpec 整數影格範圍的起訖都包含在內，時長為 `(end-start+1)/fps`。24 fps 的第 1–120 格對應 0–5 秒。未知媒體時長不可憑空填寫，應根據實際中繼資料補入。

沒有角色的專案使用 `required_character_ids: []`。只有本套件需要用圖片確定身分的主要角色才要求實際圖片，並尊重使用者明確選擇省略圖片。標籤只有在實際上傳並驗證後才算綁定。檢查器不解析來源角色的敘述文字。

維護時執行 `python -B -m unittest discover -s scripts -p test_offline_workflow.py -v`；測試檔為 [test_offline_workflow.py](../scripts/test_offline_workflow.py)。測試使用 Blender 資料替身，涵蓋純腳本邏輯與暫存檔邊界；不能證明 Blender 5.2 中的實際行為。[test_validate_previs_fast.py](../scripts/test_validate_previs_fast.py) 應在適合的 Blender 環境執行，不要只為維護規則而開啟使用者專案。

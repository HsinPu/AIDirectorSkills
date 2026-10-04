# 離線交接檢查

[validate_handoff.py](../scripts/validate_handoff.py) 是使用 Python 標準函式庫的唯讀檢查器，不啟動 Blender、不連網、不生成媒體，也不修改專案。初次撰寫複雜交付 manifest 或維護 Skill 時可使用；它不是每項短任務的必經關卡，也不是動畫確認後的畫面複核。

以 `SKILL.md` 所在資料夾取代 `<skill-root>`，以影片專案根目錄取代 `<project-root>`；可從任意工作目錄執行：

    python -B "<skill-root>/scripts/validate_handoff.py" "<project-root>" --scene-spec revisions/r001/scene-spec.json
    python -B "<skill-root>/scripts/validate_handoff.py" "<project-root>" --package revisions/r001/generation-package.json

兩種輸入可同時提供。選用的 `--hardware-profile hardware-profile.json` 可核對與 SceneSpec 對應的 `profile_id`。參數與紀錄中的路徑都以專案根目錄為基準。

## 檢查範圍

對 SceneSpec 檢查重複的資產／鏡頭／事件 ID、鏡頭及事件影格範圍、鏡頭空隙與重疊、相機／切點的宣告與起點、連續性鏡頭／影格連結、新舊預算欄位別名，以及效能紀錄中的硬體 ID。相機可透過 `camera.id` 或 `role=camera` 的資產宣告；有宣告不代表 Blender 中真的存在。

只檢查明確的檔案欄位 `manifest_ref`、`source_ref`、`scene_spec_ref`、`hardware_profile_ref` 與 `image_path`，確認位於專案內且存在。不要從所有字串猜路徑、把符號化資產庫參照當作檔案，或把 URL 當作本機檔案。

對生成套件檢查參考 ID、存在且非空的檔案、重複的已綁定標籤、已知佔位 PNG 標記、生成單位的參考與時長、一對一影片來源範圍，以及必要角色圖片缺口。選用的 `reference_method` 接受 `storyboard_images`、`blender_previs` 或 `hyper3d_blender_previs`，單元可覆寫套件預設；未宣告時保留舊版行為，不推定路線。圖片路線只要求其已宣告圖片與格子對照，不要求 `.blend`、影片、SceneSpec 或硬體檔。非線性或延長的時間對應應標為未驗證，不假裝已支援。

新製作套件依[起始畫面資產](start-frame-assets.md)宣告 `asset_contract: "start_frame_v1"`；檢查各單元的 `start_frame_reference_id` 是否存在、是 `start_frame_visual_reference` 圖片、`input_to_video_ai: true`、已列入本單元參考，且不是空檔或佔位圖。缺少欄位／錯誤用途回報錯誤，素材待補回報警告，不能宣稱已可提交。未宣告合約的舊包不強制補圖，新製作不可藉省略欄位跳過規則。

按每單元 `reference_ids` 與可選 `shots[]` 的各鏡 `reference_ids` 計數，圖片／影片／聲音上限為 9／3／3；完整六格頁算 1 張，重複輸入 ID 回報錯誤且仍占數量。套件及單元／鏡頭的 `reference_limits` 可加上已查證的更嚴格非負整數限制與 `total`，0 表示禁止該類型，較大值不放寬既有上限。確切 `model` 為 `minimax/hailuo-3` 或 `minimax/hailuo-3-max` 時另套用合計 12 個。結果 `reference_counts` 列出各範圍的計數與有效上限；只計算宣告的輸入，實際 `request.json` 仍須另核對。

圖片路線的 `storyboard_panels` 必須非空；逐格檢查 ID、單元內圖片參考、非遞減且位於單元時長內的時間、鏡頭 ID 及布林切點。預設圖片角色為 `storyboard_sequence_page`：同頁各格共用 `reference_id`，參考宣告正整數 `panel_count`，各格以 `panel_number` 指定1至格數的頁內位置；拒絕超出範圍、重複引用同一格或同頁跨不同鏡頭。已另行採用的 `storyboard_frame` 單格仍受支援。相鄰格在同鏡不能宣告切鏡，換鏡須宣告切點。僅供審閱而未採用為輸入的 `storyboard_review` 仍拒絕；已採用完整頁須登記為 `storyboard_sequence_page`，不因含格線、箭頭就視為非法參考。這只核對已宣告欄位，不證明圖片內容、模型支援或實際生成品質。

`declared_checks_passed` 只表示已宣告檢查的範圍內沒有問題。檔案可能存在，卻無法解碼、品質不佳或尚未上傳。`needs_review` 是缺少資產／綁定或對應未知的具體警告；`error` 指出參考、範圍、設定或讀取失敗。結束代碼 0 表示無問題，1 表示需要處理，2 表示參數錯誤。非零結果不會自動觸發畫面複核或重算圖。

檢查器不做完整 JSON Schema 驗證、不判斷故事細節、不測試動畫或碰撞、不自動讀取媒體中繼資料，也不驗證實際上傳。需要精確重定時時，應修改真正的剪輯時間對應，不只改這份清單。

## 圖片路線套件

以下為待補／未綁定範例；製作後填入真實路徑及可用狀態，實際上傳後才更新標籤與綁定。角色圖片仍以獨立來源指定，不以分鏡人物代替身分。

    {
      "revision_id": "r001",
      "reference_method": "storyboard_images",
      "asset_contract": "start_frame_v1",
      "reference_limits": {"image": 9, "video": 3, "audio": 3},
      "required_character_ids": ["CHR_A"],
      "references": [
        {"id": "SB_PAGE", "kind": "image", "role": "storyboard_sequence_page",
         "panel_count": 6, "input_to_video_ai": true,
         "path": "delivery/U1/media/SH01-six-panel-v001.png",
         "available": false, "binding_status": "planned", "label": null},
        {"id": "I1", "kind": "image", "role": "character_appearance",
         "input_to_video_ai": true,
         "asset_ids": ["CHR_A"], "path": "delivery/U1/media/character-a.png",
         "available": false, "binding_status": "planned", "label": null},
        {"id": "SF1", "kind": "image", "role": "start_frame_visual_reference",
         "input_to_video_ai": true, "path": "delivery/U1/media/SH01-start-v001.png",
         "available": false, "binding_status": "planned", "label": null}
      ],
      "generation_units": [
        {"unit_id": "U1", "duration_seconds": 5, "time_basis": "local",
         "reference_ids": ["SB_PAGE", "I1", "SF1"], "start_frame_reference_id": "SF1",
         "prompt": "草稿：@image1完整六格運鏡頁提供構圖、動作與攝影意圖；@image2已選定人物參考圖提供身分；@image3起始圖提供局部0秒構圖與成片風格。上傳後換成實際標籤；最終提示詞仍須完整。",
         "storyboard_panels": [
           {"panel_id": "PN1", "shot_id": "SH1", "reference_id": "SB_PAGE",
            "panel_number": 1, "time_seconds": 0, "cut_before": false},
           {"panel_id": "PN2", "shot_id": "SH1", "reference_id": "SB_PAGE",
            "panel_number": 2, "time_seconds": 0.8, "cut_before": false},
           {"panel_id": "PN3", "shot_id": "SH1", "reference_id": "SB_PAGE",
            "panel_number": 3, "time_seconds": 1.6, "cut_before": false},
           {"panel_id": "PN4", "shot_id": "SH1", "reference_id": "SB_PAGE",
            "panel_number": 4, "time_seconds": 2.4, "cut_before": false},
           {"panel_id": "PN5", "shot_id": "SH1", "reference_id": "SB_PAGE",
            "panel_number": 5, "time_seconds": 3.2, "cut_before": false},
           {"panel_id": "PN6", "shot_id": "SH1", "reference_id": "SB_PAGE",
            "panel_number": 6, "time_seconds": 4.8, "cut_before": false}
         ]}
      ]
    }

圖片不填 `duration_seconds`；時間點存在單元的格子對照中。只有影片來源才使用 `source_reference_id`／`source_range_seconds`。同一長鏡頭的多格不製造新鏡頭 ID。僅供審閱的 `storyboard_review` 頁不放進生成單元的 `reference_ids`；已採用的完整運鏡頁須以 `storyboard_sequence_page` 列入。

## 待補影片套件範例

    {
      "revision_id": "r001",
      "asset_contract": "start_frame_v1",
      "required_character_ids": ["CHR_A"],
      "references": [
        {"id": "V1", "kind": "video", "path": "exports/reference.mp4",
         "available": false, "duration_seconds": 5,
         "binding_status": "planned", "label": null},
        {"id": "I1", "kind": "image", "role": "character_appearance",
         "asset_ids": ["CHR_A"], "path": "image-assets/03_character-a.png",
         "available": false, "binding_status": "planned", "label": null},
        {"id": "SF1", "kind": "image", "role": "start_frame_visual_reference",
         "input_to_video_ai": true, "path": "delivery/U1/media/SH01-start-v001.png",
         "available": false, "binding_status": "planned", "label": null}
      ],
      "generation_units": [
        {"unit_id": "U1", "duration_seconds": 5, "time_basis": "local",
         "reference_ids": ["V1", "I1", "SF1"], "start_frame_reference_id": "SF1", "source_reference_id": "V1",
         "source_range_seconds": [0, 5], "time_mapping": "one_to_one",
         "prompt": "草稿：描述已確認劇本；上傳後將規劃標籤換成實際標籤。"}
      ]
    }

`source_range_seconds` 包含起點、不包含終點，時長為 `end-start`。SceneSpec 整數影格範圍的起訖都包含在內，時長為 `(end-start+1)/fps`。24 fps 的第 1–120 格對應 0–5 秒。未知媒體時長不可憑空填寫，應根據實際中繼資料補入。

沒有角色的專案使用 `required_character_ids: []`。只有本套件需要用圖片確定身分的主要角色才要求實際圖片，並尊重使用者明確選擇省略圖片。標籤只有在實際上傳並驗證後才算綁定。檢查器不解析來源角色的敘述文字。

維護時執行 `python -B -m unittest discover -s scripts -p test_offline_workflow.py -v`；測試檔為 [test_offline_workflow.py](../scripts/test_offline_workflow.py)。測試使用 Blender 資料替身，涵蓋純腳本邏輯與暫存檔邊界；不能證明 Blender 5.2 中的實際行為。[test_validate_previs_fast.py](../scripts/test_validate_previs_fast.py) 應在適合的 Blender 環境執行，不要只為維護規則而開啟使用者專案。

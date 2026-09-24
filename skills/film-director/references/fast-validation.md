# 快速驗證請求與證據

[validate_previs_fast.py](../scripts/validate_previs_fast.py) 是 Blender 製作期間有範圍限制的資料檢查工具。它不算圖產生審閱影像、不修復場景，也不維護永久快取。只有製作／修訂期間的相關資料需要檢查，或使用者要求時才執行。模型和動畫核准後，不為了匯出提示詞而執行。

## 單次請求

在獲授權的批次中，將相關 SceneSpec 範圍序列化為 JSON，存入 scene["previs_validation_request"]。納入受影響鏡頭、相關角色（包括機位變更涉及的主體）、簡單障礙物和高風險影格。登錄請求只寫入中繼資料；驗證器會暫時切換影格，不會建立或儲存物件或動畫。經檢視的程式文字應透過 execute_blender_code.code 一次送出並讀回結果，而非每個物件或影格都呼叫一次 MCP。

    {
      "mode": "fast",
      "revision_id": "r008",
      "change_scope": "camera_path",
      "affected_shot_ids": ["SH_020"],
      "active_camera_strategy": "single_scene_markers",
      "sample_stride": 6,
      "max_samples": 96,
      "max_seconds": 3.0,
      "risk_frames": [49, 72, 96],
      "characters": [{
        "id": "CHR_hero", "root": "CHR_hero_root",
        "path": "CRV_PATH_CHR_hero", "collision_radius_m": 0.35,
        "subject_points": ["CHR_hero_head", "CHR_hero_chest"]
      }],
      "collision_objects": ["ENV_COL_wall_left", "ENV_COL_wall_right"],
      "shots": [{
        "id": "SH_020", "frame_range": [49, 96],
        "camera": "CAM_SH_020", "subject": "CHR_hero",
        "safe_region": {"x": [0.05, 0.95], "y": [0.05, 0.95]},
        "camera_radius_m": 0.2, "check_occlusion": true
      }],
      "camera_cuts": [{"frame": 49, "camera": "CAM_SH_020"}],
      "motion_limits": {"camera_speed_mps": 4.0}
    }

這些只是範例值，不是通用運動限制。距離指標須使用公尺且 scale_length=1，否則應回報錯誤。靜態角色可設 motion_scope: static。獨立鏡頭場景使用 active_camera_strategy: per_shot_scene，只檢查目前場景，剪輯時間軸須另外驗證；標記檢查只適用 single_scene_markers。

高風險影格應包括實際轉彎、牆面、門、停止、剪接及相鄰影格。腳本不會推斷所有風險事件。明列 sample_frames 會取代自動選樣，但仍受數量上限限制，並須包含重要影格。長鏡頭或過長風險清單應拆分檢查，不能把截斷結果視為全面涵蓋。沒有 shots 時，只執行目前可用的影格檢查。

## 抽樣能與不能證明的事

碰撞物件必須是目前檢視圖層中的簡單已評估 Mesh 或 Curve 代理，代表真實牆、柱、門。不要用一個包住整間房的建築盒，也不要把地板、演員或裝飾散布物當作牆。角色根部／攝影機球體與世界座標軸對齊包圍盒（AABB）的比較，只能找出粗略候選碰撞。旋轉、凹面與開口可能造成誤報，身體或兩個抽樣影格間的快速移動也可能漏判。修改場景前，應以適當的簡單碰撞體、BVH／射線或掃掠，以及受影響區間更密的抽樣，在局部查證命中。

主體點使用已評估的世界位置與攝影機。宣告實際球心和身體點，不虛構手腳。只有實際建立附著點時才使用手腕／手掌／道具點；只有詳細角色身體才使用腳部點。特寫需要追蹤必須入鏡的點，不能只檢查根部。刻意出框或被遮擋的區間要明確允許。投影無法證明角色身分、道具類別或構圖品質。

選用的 scene.ray_cast 遮擋檢查，只回報目前相依圖中的幾何命中；無法判定透明度、算圖可見性差異、所有實例或語意遮擋。攝影機包絡檢查也不會掃過近裁切平面的所有角落。

Curve 模式檢查根部與父層的 Action／NLA／Location 驅動及 Follow Path 目標。分層 Action 應透過實際 slot 讀取。若 Channelbag／slot 讀取失敗，回報 ANIMATION_DATA_UNREADABLE 與未驗證的 root_motion_sources，不能當作沒有衝突運動的證據。明定 motion_owner: parent 時，只檢查父層連結及根部路徑／位置沒有競爭來源，不能證明整個載體動作或交接。static 可略過路徑要求，但不證明完全不動。其他 owner 在建立專門檢查前回報 UNSUPPORTED_MOTION_OWNER。

預設彎曲骨架不改變根部運動的歸屬。此腳本不檢查變形圓柱支撐、選用手部 IK、手掌接觸或道具交接。full_constraint_and_parent_motion_composition 和 full_event_time_mapping 維持未驗證。攝影機限制是鏡頭內離散平移估計，不是完整旋轉晃動、加加速度或影片品質評估。

## 限制與結果

預設最多抽樣 96 個影格，軟性執行時間預算為三秒。每個影格只設定一次，並共用相依圖。只在影格之間檢查預算；正在執行的高成本 Blender 評估無法中斷，所以三秒不是硬性逾時。發生錯誤時也要還原影格、子影格和作用中攝影機。場景處理函式仍可能執行；有副作用的專案應用背景複本檢查。

結果包含 status、planned_sample_frames、actual sample_frames、errors、warnings、unverified 及 timings.validation_wall_ms。每組詳細問題最多輸出 200 件，超出時以 ISSUE_OUTPUT_LIMIT 摘要。

- sampled_checks_passed 表示已宣告的抽樣檢查沒有錯誤，不代表整部影片核准。
- needs_review 包含警告、缺少代理或主體點、截斷或逾時。
- error 包含設定、控制、投影、候選碰撞或執行問題；粗略碰撞命中須局部確認。
- unverified 保留未測的全身碰撞、連續路徑、導演品質與即時 FPS。

原始結果存為目前修訂下的 validation_run.json，另行加入變更範圍、ID、MCP 往返時間、算圖時間及重用證據。腳本執行時間不等於總等待時間或檢視埠 FPS。腳本不會自動查閱舊 JSON 來決定跳過哪些檢查。

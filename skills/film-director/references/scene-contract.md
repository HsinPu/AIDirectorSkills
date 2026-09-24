# SceneSpec 與 ShotSpec

修改 Blender 場景前，先建立可重播、可增量更新的資料約定。[SceneSpec JSON Schema](scene-contract.schema.json)應保持精簡且嚴謹；新增欄位要有預設值與相容規則。即使技能流程紀錄擴充，機器使用的 SceneSpec Schema 仍是 1.1。

## 頂層狀態與證據

project-state.json 是專案目前狀態的權威來源。SceneSpec 只保存綁定修訂的快照，不能覆寫專案入口。實用的頂層流程紀錄包括 project_state（skill_rule_version、project_root: "."、project_state_ref、approved_revision、working_revision、等於 working_revision 的選用舊欄位 revision_id、parent_revision、active_scene_id、development_stage、approval_status、source_of_truth、artifact_context、drift）、帶真實檢查／證據的 directing_review、previs_profile、prompt_export 和 asset_reference_export。這些擴充不強迫修改舊 JSON Schema。

所有 *_ref、path、image 和交接路徑都以專案根目錄為基準，使用 / 分隔。approved_revision 是最後由使用者接受的正式來源；working_revision 是可編輯草稿。只有舊版 revision_id 時，讀作 working_revision，並在下次寫入時補齊。草稿不可當成已核准提示詞來源。

第一份製作計畫需要授權。有阻擋性的 directing_review 修訂問題，應在製作前針對受影響鏡頭解決；若既有授權或使用者要求變更，不因舊狀態紀錄落後而再次要求許可。新變更更新工作修訂，只將相依成果標為 stale，先前成果保留為 superseded。已知且影響提示詞事實的 Blender 手動偏移，須做範圍明確的對齊或記錄已接受例外，不作假設性的全場景掃描。

使用者核准目前模型與動畫時，將該修訂升為已核准，進入 prompt_export 並交付，不增加 AI 審閱、Release 或創作修訂。技術驗證另記；未驗證不阻擋已核准交接。必要的場景／重要道具結構參考圖，須是真實、已登錄且已接受的影像，或由可靠既有來源取代。角色美術圖另行追蹤，不阻擋中性代理工作。

## 地點素材使用與穩定 ID

可重用的賭場、住處、公園、街道或辦公室，預設視為含配置、固定內容、尺度及介面的完整地點素材。asset_uses 將已登錄地點綁定到場景實例，assets 則保留穩定場景物件 ID。地點使用紀錄包含 asset_id、asset_version、instance_id、kind、library_ref、manifest_ref、source_ref、root_collection、use_mode、placement、local_variant_ref、static_review_ref、presentation_owner，以及 imports_story_or_shot_data: false。

asset_id、確切 asset_version、instance_id 和 placement 是必填；不得以「latest」、猜測檔名或 Blender 的 .001 尾碼辨識身分。placement 是錨點、碰撞與導航從素材局部到場景世界的唯一變換。一份素材可有多個實例；改實例不重寫來源。連續場景在同一地點時，鎖定確切版本；升版或換地點需列出拓樸、錨點、走位和鏡頭的影響清單。

可重用地點只包含靜態結構與介面，不帶入前一場的劇本、鏡頭、作用中攝影機、人物、路徑、動畫、NLA、時間軸標記、場景天氣／照明、節奏或提示詞。場景專用調度由 presentation_owner 管理；暫時修改放在 local_variant_ref，不污染共享素材。

真實或專門地點可用 scene_research_manifest 記錄來源 ID／網址／類型、evidence_level（confirmed、inferred、artistic）、支持的主張與範圍。design_intent 可記錄層級、模組順序、轉場、視線及語意元素。沒有來源支持的事實維持假設；抽象場景可標 research_scope: not_applicable。

所有場景、素材、物件、鏡頭、事件、動作、碰撞、燈光及集合 ID 都須唯一且穩定。機器頂層欄位包括 schema_version、project.id、seed、request_id、assumptions、warnings、source_refs 和 budgets。使用公尺與 Z 軸向上，宣告 FPS、影格範圍、畫面比例及色彩管理。sequence 明確分開動作時間、剪輯時間和作用中攝影機。每條相鄰場景的 continuity_link 或 camera_cut 都要附 handoff_state，不以一段全域文字代替。

## 節奏層級

screen-language.md 設定長期界線，例如畫面比例／FPS、安全構圖、軸線／連續性原則、容許的攝影機／手持條件、代理用途及禁令；它不替每場戲指定相同「慢」或「快」的時長。sequence.pacing_profile 描述跨場景的能量與資訊弧線；scene.pacing_profile 指定本場的資訊速度、表演能量、攝影機能量、剪接密度、聲音節奏與 required_readability。每個節拍說明觸發、可見動作、資訊變化、結果狀態與可讀時間窗；每個鏡頭落實影格範圍、隨時間變化的攝影機行為、停頓和剪接條件。

例如 conversational_tension 場景可設 information_rate: measured、performance_energy: restrained、camera_energy: low、editorial_density: sparse、required_readability: [reaction_before_cut]。與 beat_ids 相連的鏡頭，可以等角色看見空椅子後才緩緩推進，並在決定變得可見後才剪接。動作戲的人物可有高能量，攝影機仍維持穩定空間資訊。

優先順序是使用者目前明確指示、已確認鏡頭例外、節拍目的、場景設定、段落弧線、影片語言、技能預設。低層級若刻意違反長期界線，需記錄例外。節奏修改同步受影響的節拍時間、鏡頭影格／剪接、演員 Curve 對應、停頓／轉彎／道具、攝影機曲線、連續性、軌跡與提示詞，且只將相關成果標為 stale。快速抽樣不能證明完整事件或來源／剪輯時間對應。藝術可讀性由使用者觀看判斷；核准不觸發 Standard 或 Release。

## 最低場景與鏡頭結構

[minimal-scene-spec.json](minimal-scene-spec.json)是可解析的 Schema 1.1 範例：單鏡頭、無人物的靜態產品計畫。它宣告參照，performance 為 not_run／null，不能證明 Blender 物件已存在。按任務調整，不照抄預算或編造人物。[離線交接檢查](offline-handoff-check.md)驗證已實作的 ID、影格、剪接、別名與路徑，不能取代完整 Schema 驗證或視覺判斷。

每個鏡頭記錄影格範圍、意圖、實際景別、焦距、對焦、主體畫面區域、路徑及連續性連結。故事鏡頭還應有 beat_ids 和節奏；純功能鏡頭可在 pacing.not_applicable 說明原因。sequence.camera_cuts 是主時間軸作用中攝影機的權威來源；第一筆可能只是指定初始攝影機，不代表可見剪接。單鏡頭影片可以沒有相鄰鏡頭連結。

pre_roll／post_roll 供內部運算，匯出只含有效 edit_frame 區間。用時間軸標記宣告單場景攝影機，或用分鏡頭場景，讓作用中機位可以還原。選用鏡頭欄位只有實際使用時才填：運動類型（dolly、truck、pan、tilt、orbit、crane、handheld、zoom、POV、whip pan、crash zoom）及相關速度／加速度／加加速度／幅度界線；rack_focus 的起訖與目標；綁定事件及固定 seed 的 impact_shake；含 bbox／頭部留白／視線留白／安全框／地平線／前景的構圖；以及說明原因與方式的 axis_crossing。

## 事件與連續性

預設結構事件記錄演員／道具 ID、時間、起訖位置／朝向、重要轉彎、持有、釋放／交接及結果狀態。意圖、預備、執行、接觸與恢復可描述節拍，不必因此製作肢體動畫。圓柱代理預設不需要受擊盒、腳部固定、衝量或受擊停頓。

只有明確選用且有詳細接觸的 articulated_performance，才需要 attacker、receiver、hitbox／receiver_hitbox、contact_frame 與容差、impact_point、reaction_delay_frames、hit_result、impact_strength 或 hit_stop_frames。hit_result 是 hit、miss、blocked 或 glancing。物理受力反應發生在撞擊之後；預先閃躲／格擋是另一項行為。一般抓握可由持有者、代理錨點與放開時間表示，不需手指。

每對相鄰鏡頭要交接角色／道具的世界變換、速度、朝向、姿勢、視線、抓握、傷害／損壞、入出鏡、可見性、光線、天氣與環境狀態。每條連結含 from_frame、to_frame、handoff_state、allowed_error 及實際驗證結果。刻意跨軸、時間跳躍、主觀鏡頭或跳接應記錄，不能省略狀態。

## 選用門檻與預算

門檻只在選定且相關的技術檢查中使用，不適用使用者核准後的交接。詳細腳部固定／全身 IK 門檻不適用預設無手代理；簡易手部有自己的接觸計畫。起始參考值：支撐期間接觸誤差 0.01 公尺、接觸位置誤差 0.08 公尺、在指定解析度下支撐錨點投影殘差每影格三像素、對焦誤差約主體深度 10%、主體超出安全框面積約 5%。依風格和事件調整；刻意裁切、離框及失焦須列為例外。

檢查腳部固定時，在支撐局部空間比較實際接觸點與支撐錨點。畫面檢查時，逐影格以同一攝影機投影兩者，觀察殘差變化；不同深度不能直接相減一個全域攝影機像素值。跨鏡頭應比較對應來源時間的角色／道具狀態，或經過時間的運動預測。起始參考值為位置 0.05 公尺、旋轉五度、速度差 0.25 公尺／秒。不要套用在硬切兩側攝影機位置，也別把正常跑動位移當成連續性斷裂。在單一連續鏡頭內，應以適當世界／畫面速度、加速度與加加速度檢查高速運動。

超過預算時，依序減少鏡頭外仍被評估的集合、遠處 LOD、實例密度、材質貼圖、模擬，再考慮細分；同時保護接觸、遮擋、構圖與因果必要幾何。實質取捨記入 warnings。

Schema 1.1 的預算／效能紀錄使用 hardware_profile_id，並分開規劃的 target_fps 與量測的 viewport_fps。常見欄位有 calibration_status、visible_triangles 與 expanded_visible_triangles 別名、objects 與 base_objects 別名、instance_count_soft、texture_mb、target_fps、viewport_status、render_resolution、measurement_method、depsgraph_ms_p95 和 warnings。不得把目標 FPS 填入量測 FPS。需要一致的舊／新別名應保持相等，profile ID 也須一致。單場景的一般 source_frame 等於 edit_frame，除非實際剪輯／動作軌有重新對應。

## 導演擴充與相容性

故事工作可新增 directing：scene_question、character_objectives、viewer_alignment、audience_information、beats、style_contract、reference_roles、assumptions；blocking：座標原則、可走區、障礙、演員／攝影機／瞄準／對焦路徑；以及鏡頭擴充，如 viewpoint、information_delta、composition_start／end、movement_motivation、path_id、aim_id、focus_id、剪接理由、readability_windows 和例外。自主演員路徑引用穩定且可編輯的 Blender Curve，弧長／時間對應另存；靜態與由父層帶動的運動應宣告實際 root_motion_owner。快速請求使用 motion_owner。進階原地動作片段與腳部固定階段，只有實際製作時才記錄。

sequence 保存來源／剪輯時間及對應。非整數時間只量化一次，包含端點的影格範圍須一致。剪輯餘量、動作／模擬預跑及觀眾可讀時間，是不同欄位。敘事、走位、動畫、攝影機、連續性、檢視埠與匯出的審閱狀態，需有真實證據與方法；欄位填完不等於通過「電影品質」檢查。

新專案紀錄可參照 creative_documents、stage_reviews、project_kind、work_scope、章節進度、last_checkpoint 和 resume_context。新代理採 cylinder_and_sphere、root_and_simple_bend、四根骨骼及有來源的 H／W／D。讀取舊版 root_and_torso_transform 等值時，不必重建已核准成果。contact_hand_plan 可省略；舊紀錄沒有它不表示必須補手。Schema 容許擴充，也不能證明訪談、展示、綁定、IK 或支撐檢查確實執行。

實際寫入 shots[].shot_size，不可用 planned_per_director_plan 等佔位值。機器表格不能取代向使用者展示的完整分鏡。新紀錄一律使用 information_rate，以及清單型 required_readability。讀取舊資料時，把 narrative_information 視為 information_rate、單值可讀性視為單項清單，重寫時保留 low_to_medium 等舊 camera_energy 值的意義。只記錄目前任務需要的資料。

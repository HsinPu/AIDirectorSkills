# 導演與動畫來源索引

導演與動畫資料於 2026-09-08 查閱；影片參考提示詞資料於 2026-09-10 加入，後續備註日期見下文。「已閱讀」表示實際檢視公開文章或原始碼文字；除非另有註明，沒有觀看嵌入影片、付費課程或完整教科書。本技能的方法是獨立整理，不是複製第三方技能。來源支持理論或實作選擇，不能證明新場景有電影品質、即時播放效能或特定生成成功率。

## 教學與作者資料

| ID | 已閱讀資料 | 用途與證據界線 |
|---|---|---|
| D01 | Yale Film Analysis，[Cinematography](https://filmanalysis.yale.edu/cinematography/) | 構圖、視角、跟拍／重新構圖與敘事性運鏡。光學簡化說法需對照 B06 與投影關係，不採固定的焦距情緒規則。 |
| D02 | Yale Film Analysis，[Editing](https://filmanalysis.yale.edu/editing/) | 連續性、動作銜接與鏡頭停留目的。節奏也受畫面內動作與聲音影響；文中的鏡頭時長不是硬性門檻。 |
| D03 | Yale Film Analysis，[Mise-en-scene](https://filmanalysis.yale.edu/mise-en-scene/) | 深度調度、距離、關係與畫外空間。已讀文字，未另行觀看其中影片片段。 |
| D04 | Judith Weston，[Top 10 Ideas from Directing Actors](https://judithweston.com/web/archive/top-10-ideas-directing-actors) | 用動詞、事實、意象、身體動作與事件分析劇本和表演。情緒詞不會機械式對應單一姿勢。這是公開文章，不是完整書籍。 |
| D05 | Judith Weston，[12 Tips for Directors](https://judithweston.com/web/extras/12-tips-directors) | 視覺／語氣選擇與保有彈性的準備。Blender 欄位是本專案自行設計。 |
| D06 | David Bordwell，[Creating suspense through film form](https://www.davidbordwell.net/blog/2006/09/26/film-form-and-the-viewers-experience/) | 觀眾已知資訊會影響好奇、懸念、驚訝與感受節奏；不能單看鏡頭時長判斷拖沓。 |
| D07 | David Bordwell，[Calm that camera!](https://www.davidbordwell.net/blog/2023/04/30/calm-that-camera/) | 與 Ken Kwapis 討論機位和運動；靜止、克制跟拍、自由攝影與長鏡頭都是選擇，持續移動不會自動產生故事價值。 |
| D08 | ASC，[Shot Craft: Tools for Camera Movement](https://theasc.com/article/shot-craft-camera-movement/) | 依敘事目的選 dolly、tracking、Steadicam、手持與升降。 |
| D09 | ASC，[Casino Royale: High Stakes For 007](https://theasc.com/article/casino-royale-high-stakes-007/) | 賭桌場景的前／中／後景層次、視線與景別變化，可用於設計可拍攝視線。 |
| D10 | ASC，[Beyond The Frame: Casino](https://theasc.com/article/beyond-the-frame-casino-1995/) | 賭場環境的運鏡與節奏；運動應服務資訊和感受。 |
| D11 | ASC，[Ocean's Eleven: Smooth Operators](https://theasc.com/article/oceans-eleven-smooth-operators/) | 在複雜空間以運鏡釐清人物與位置，不提供固定鏡頭範本。 |
| A01 | AnimSchool／Angelo Sta Catalina，[The Key Poses of a Run Cycle](https://blog.animschool.edu/2024/04/10/the-key-poses-of-a-run-cycle/) | 接觸、下降、推進與高點；自然／誇張跑動、輪廓與接觸。不是通用的迪士尼官方標準，未觀看完整課程。 |
| A02 | AnimSchool／Tyler Phillips，[Storytelling in Staging](https://blog.animschool.edu/2025/03/07/storytelling-in-staging/) | 簡潔姿勢與機位如何組織故事、思考節拍及時間對比。文章中的節拍數不是通用配額。 |
| P01 | OpenStax／Rice University，[6.3 Centripetal Force](https://openstax.org/books/college-physics-2e/pages/6-3-centripetal-force) | 速度平方除以半徑可描述轉彎成本，不能當作人體極限或完整步態模型。 |

## Blender 5.2 實作證據

| ID | 官方文字或原始碼 | 已確認界線 |
|---|---|---|
| B01 | [Follow Path](https://docs.blender.org/manual/en/5.2/animation/constraints/relationship/follow_path.html) | 路徑時間／偏移、擁有者偏移與約束；不自動規劃攝影機路線或避障。 |
| B02 | [Damped Track](https://docs.blender.org/manual/en/5.2/animation/constraints/tracking/damped_track.html) | 純擺動旋轉，沒有時間延遲或彈簧阻尼。 |
| B03 | [Track To](https://docs.blender.org/manual/en/5.2/animation/constraints/tracking/track_to.html) | 追蹤／向上軸及靠近極點時的翻滾風險。 |
| B04 | [F-Curve Properties](https://docs.blender.org/manual/en/5.2/editors/graph_editor/fcurves/properties.html) | 插值、速度連續性與自動控制柄過衝；不是每個路點都應緩入緩出。 |
| B05 | [NLA Sidebar](https://docs.blender.org/manual/en/5.2/editors/nla/sidebar.html) | Replace／Add／Combine、延伸與片段時間；軌道名稱不能隔離通道或管理根部運動。 |
| B06 | [Cameras](https://docs.blender.org/manual/en/5.2/render/cameras.html) | 鏡頭／感光元件／視角、機位、推拉變焦與對焦物件／距離。 |
| B07 | [Blender 5.2 發行分支的 anim_path.cc](https://github.com/blender/blender/blob/blender-v5.2-release/source/blender/blenkernel/intern/anim_path.cc) | 查閱快照採累計抽樣路徑長度及第一條 spline，不只是原始 Bézier 參數移動。分支日後可能變更。 |

## MCP 設定證據

下列資料於 2026-09-10 核對；安裝時應針對目標環境重新確認。

| ID | 官方來源 | 界線 |
|---|---|---|
| M01 | [Blender Lab MCP](https://www.blender.org/lab/mcp-server/) 與[官方儲存庫](https://projects.blender.org/lab/blender_mcp) | 外掛、伺服器與用戶端都需設定；.mcpb 需要相容用戶端。曾檢視官方本機發行包 v1.0.0 的 README、pyproject 與程式碼入口。 |
| M02 | [Codex MCP 設定](https://developers.openai.com/codex/mcp) | CLI 或設定檔可登錄本機服務，但設定檔存在不代表目前工作階段已載入或連上 Blender。 |

## 其他攝影案例

C01 重用 ASC 的[運鏡資料](https://theasc.com/article/shot-craft-camera-movement/)：多運動不會自動改善敘事。C02 [Casino Royale](https://theasc.com/article/casino-royale-high-stakes-007/)討論視線與分層空間。C03 [Casino](https://theasc.com/article/beyond-the-frame-casino-1995/)討論公共室內的位置、遮擋與場面調度。C04 [Ocean's Eleven](https://theasc.com/article/oceans-eleven-smooth-operators/)結合穩定器、dolly 與多人調度，但不規定焦距或鏡頭數。C05 BFI 的 [Film Language](https://www.bfi.org.uk/education-research/education/teaching-film-language)說明景別、畫框、剪輯與聲音如何共同作用。

## 六個社群儲存庫的指定版本

R01–R06 是創作者工作流程範例。其「最高準則」、成功率或電影成果主張，不是權威證據。本技能只採用並自行調整可用想法，不照搬工具呼叫、提示詞限制或審核政策。未執行遠端程式、付費服務或重現生成結果。

| ID | 檢視的儲存庫與檔案 | 採用／調整內容與授權界線 |
|---|---|---|
| R01 | Higgsfield [generate](https://github.com/higgsfield-ai/skills/blob/fb18134b4aabe99c4bf7ff01c8f4883400efc80d/higgsfield-generate/SKILL.md) 與 [explainer](https://github.com/higgsfield-ai/skills/blob/fb18134b4aabe99c4bf7ff01c8f4883400efc80d/higgsfield-video-explainer/SKILL.md) | 來源用途、聲音／影像時序與分段交付。檢視模組主要處理生成服務協調，不處理 Blender 表演或步態。已閱讀根目錄 MIT 授權。 |
| R02 | Manju Laoli [director skill](https://github.com/lixiaoxiao9888-create/manju-laoli-skill/blob/aa20fb60054ae52553a4b13f8810ed2fcd89ba70/short-drama-director/SKILL.md)、[top-down space](https://github.com/lixiaoxiao9888-create/manju-laoli-skill/blob/aa20fb60054ae52553a4b13f8810ed2fcd89ba70/short-drama-director/references/spatial-topview-camera.md)、[causal beats](https://github.com/lixiaoxiao9888-create/manju-laoli-skill/blob/aa20fb60054ae52553a4b13f8810ed2fcd89ba70/short-drama-director/references/screenplay-gate-engine.md) | 目標、阻力、選擇、鏡頭工作、空間圖與參與者狀態；不採強制十二節拍、反轉及僵硬攝影／動作禁令。已閱讀該目錄 MIT 授權。 |
| R03 | MapleShaw [Seedance skill](https://github.com/MapleShaw/seedance2.0-prompt-skill/blob/a2ab7fd9b73e1d531fabd7f59f390e8d39dc57a5/SKILL.md)、[camera codec](https://github.com/MapleShaw/seedance2.0-prompt-skill/blob/a2ab7fd9b73e1d531fabd7f59f390e8d39dc57a5/references/camera-codec.md)、[storyboard](https://github.com/MapleShaw/seedance2.0-prompt-skill/blob/a2ab7fd9b73e1d531fabd7f59f390e8d39dc57a5/references/storyboard-driven.md) | 攝影描述、時間段與剪接區別、失敗界線。其提示詞 X／Y／Z 不是 Blender 世界座標軸；不採固定軸線數、節奏公式或強制裁短。已閱讀根目錄 MIT 授權。 |
| R04 | songguoxs [Seedance skill](https://github.com/songguoxs/seedance-prompt-skill/blob/57d1e2f273747c238dd892698a05137ab2f10d4a/.claude/skills/seedance/SKILL.md) | 時間段、來源用途、聲音／影像區別與跨段狀態。產品語法和時長依平台而定。README 稱採 MIT；本次未找到獨立 LICENSE 內文。 |
| R05 | jnMetaCode [short-film skill](https://github.com/jnMetaCode/ai-shortfilm-prompts/blob/f21500e5946973949c6bbf02e67e0c21b2e63a35/skills/shortfilm-prompt/SKILL.md) 與 [NOTICE](https://github.com/jnMetaCode/ai-shortfilm-prompts/blob/f21500e5946973949c6bbf02e67e0c21b2e63a35/NOTICE) | 主體清單、鏡頭卡、畫外資訊、動作／情緒落點。不採錯誤的同邊畫面方向、強制呼吸式手持／無音樂／固定鏡頭數。MIT 涵蓋原創部分；NOTICE 區分保留權利的 Mx-Shell 提示詞，本技能未複製。 |
| R06 | [fight-video-create-skill](https://github.com/qualsenWeb/fight-video-create-skill/blob/28ab4b658fe41cbd54842f470fd879c38e9c9737/SKILL.md) | 打鬥故事、動作、空間與鏡頭：先定路線、保留結果、明確鏡頭意圖及壓力交接。不採固定動作密度、動態結尾或把遮擋自動當作跨軸。README 未列獨立授權；僅用於研究、連結與獨立摘要。 |

<a id="video-generation-and-reference-prompts"></a>

## 影片生成與參考提示詞

以下公開文字於 2026-09-10 閱讀，未執行生成或重現效果。實作寫在 [AI 影片提示詞](ai-video-and-asset-prompts.md)，不依賴特定專案或本機研究資料夾。

| ID | 官方來源 | 採用方法與界線 |
|---|---|---|
| V01 | ByteDance Seed，[Introducing Seedance 2.5](https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5)，發表於 2026-07-31 | 以結構白模提供運動、影像提供外觀的範例。當時公布的 30 秒模式與時間標記控制，不是全球通用片長或逐影格保證；複雜動作與多人互動仍有限制。 |
| V02 | [Dreamina Seedance 2.5 User Guide](https://bytedance.larkoffice.com/wiki/NjnWwvf4BiFYFLk2RzrcEgaunGf#VhDjdmAjyo1YoQxrp0dcb8wenbd)，頁面顯示 8 月 17 日編輯 | 來源宣告、物件對應、情節細節與場景處理。粗略白模提供結構，文字補充表演；這不禁止所有肢體參考，也不要求重做已核准預演。 |
| V03 | Dreamina [Motion Reference Guide](https://dreamina.capcut.com/seedance/seedance-2-5-motion-reference-guide) | 逐一說明身分、運動、風格與聲音來源的用途及保留／變更屬性。廠商指引不是量測成功率或僵硬內部優先規則。 |
| V04 | Dreamina [Prompt Guide](https://dreamina.capcut.com/seedance/seedance-2-5-prompt) | 可觀察的動作、大致時間節拍及必要具體限制；範例人物／鏡頭／節拍／風格數量不是預設。 |

另重新閱讀 [HiAPIAI Blender Previs Engine](https://github.com/HiAPIAI/awesome-ai-video-workflows/tree/main/blender-previs/engine) 作者對影片、提示詞及來源共同交接的說明。該流程以 Seedance 2.0 為目標，其時長與核准流程不照搬到 2.5；R03、R04 也不是目前 2.5 參數證據。只有時長、來源數、上傳格式、引用語法或編輯能力重要時，才使用目前已查證的平台資料；針對版本不確定處查證，不為一般提示詞重跑所有研究。

## 來源資料如何使用

2026-09-10 的流程修訂重讀六個社群儲存庫中十二份相關文件，涵蓋創作訪談、攝影／色彩、可見分鏡、代理模型及參考提示詞。Higgsfield 強化明確風格決策及生成、參考、編輯、延伸之分，未引入其 CLI／模型／工作預設。Manju Laoli 強化鏡頭目的、攝影／色彩／材質／聲音的具體性，未採十二節拍、十五秒、反轉或額外審閱規定。MapleShaw 強化構圖及時間段與剪接之分，未沿用 Seedance 2.0 限制。songguoxs 強化逐來源 @ 用途與連續性，不把預定標籤當成已上傳。jnMetaCode 強化主體身分及獨立的鏡頭／聲音規劃，不採通用手持或禁止音樂規則。打鬥技能強化因果動作鏈，不把圓柱代理當成完整武術動畫。

3.1 修訂回應使用者要求：創作問題提供三個選項且可自由描述；駕駛／持物等指定鏡頭可採與軀幹連結的簡易手部 IK。這是互動與製作範圍選擇，不是 Seedance 效能比較。曾檢視 [Blender 5.2 KinematicConstraint API](https://docs.blender.org/api/5.2/bpy.types.KinematicConstraint.html) 與 [Blender 5.0 IK manual](https://docs.blender.org/manual/id/5.0/animation/constraints/tracking/ik_solver.html)，據以使用鏈長、極點與伸展術語。英文版 5.2 手冊頁面當時無法直接取得，因此不宣稱已閱讀該頁或測試新骨架；實作時須查實 Blender RNA。

3.0 修訂把同輪展示劇本／分鏡、固定角色設定圖比例、連載接續、預設圓柱彎曲骨架與平順轉彎加入流程。身體比例與四骨設定是可調整的製作預設，不是醫學比例或 Seedance 實驗；也不追溯重建已核准專案。

使用來源時，保留參考 ID、用途（故事／畫面／動作／攝影／聲音／外觀）、範圍、版本與實際閱讀部分。借用影片片段的運鏡，不等於引入其演員、服裝、對白或事件。教學說明原理、官方文件說明軟體行為、社群技能提供組織範例。本專案的路徑公式、時間欄位、碰撞抽樣及審閱步驟是工程與創作整理，不是逐字照搬。未讀頁面、書籍目錄或未看影片不可列成完整知識。實際案例記錄計畫、假設、實作、審閱問題與變更；按案例／風格／版本界定經驗，再考慮升為通用規則。

## 多人動作證據，2026-09-12 核對

ByteDance Seed 的[官方 Seedance 2.5 介紹](https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5)說明白模姿勢、路徑與攝影參考，也指出複雜物理動作與多人一致性仍有改進空間。它無法判定某次失敗輸出的唯一原因，也不能證明其他模型的行為。Chris Hurtt／Animation Mentor 的 [Anticipation](https://www.animationmentor.com/blog/anticipation-the-12-basic-principles-of-animation/)將預備時間、速度及幅度與後續動作相連；Shawn Kelly／Animation Mentor 的 [Contrast in Timing](https://newsletters.animationmentor.com/newsletter/1006/feature_geek.html)說明等距時序為何可能顯得機械。可見道具遺漏、分離目標反應與參與者狀態表，是本技能的整理，不是廠商保證的流程。

## 粗略預演、自然表演與使用者回饋（3.2.3）

先前研究與使用者生成回饋共同形成[自然表演與身分連續性](ai-video-and-asset-prompts.md)及[提示詞範本](reference-prompt-template.md)；本次規則修訂沒有執行新的生成實驗。

| 證據 | 方法與界線 |
|---|---|
| [Dreamina／ByteDance Seedance 2.5 User Guide](https://bytedance.larkoffice.com/wiki/NjnWwvf4BiFYFLk2RzrcEgaunGf) | 先前已閱讀粗模及長影片段落：來源用途、可辨識代理／人物對應、由文字補足局部表演、按時間或邏輯組織故事。不是逐影格控制保證，也不要求刪除所有時間。 |
| Dreamina [Motion Reference](https://dreamina.capcut.com/seedance/seedance-2-5-motion-reference-guide) 與 [Prompt Guide](https://dreamina.capcut.com/seedance/seedance-2-5-prompt) | 來源用途、局部編輯及必要具體限制；依任務調整，不固定提示詞長度。 |
| GrandVisionsAI 的[簡／詳預演比較](https://x.com/GrandVisionsAI/status/2096993565599490465)與[公開提示詞回覆](https://x.com/GrandVisionsAI/status/2096993966549880939) | 創作者自述支持將大致路徑與局部自然互動分開；未獨立重現，不能推論簡單代理一定較好。 |
| Emily2040 的[參考流程](https://github.com/Emily2040/seedance-2.0/blob/main/references/reference-workflow.md)與[表演範例卡](https://github.com/Emily2040/seedance-2.0/blob/main/references/performance-example-cards.md) | Seedance 2.0 的來源組織及表演範例可供比較；卡片明說未生成，不能視為 2.5 效能證據。 |
| 使用者回報的生成回饋 | 以大致故事時間段安排自然動作，曾改善整體／動作自然度；因此來源用途開頭及寬鬆段落成為專案修訂基準。後續入鏡、服裝與混合歧義須局部診斷，不能換算成功率或歸咎唯一原因。 |

對白的意圖、傾聽、潛台詞、情緒延續及符合景別的細節，是結合 D04–D05 與本任務需求的整理。新的打鬥和對白範例為獨立撰寫，尚未生成測試。人類自然度、空間／攝影、身分連續性及互動結果應分開記錄。

## 細微表情、對白與情緒發展（3.2.4）

2026-09-12 重新閱讀官方表演範例，並對照先前聚焦研究，以及使用者對「安靜邀請」與「爭執轉失落」兩則文字案例的回饋。實作見[對白指引](ai-video-and-asset-prompts.md)與[對白範例](reference-prompt-template.md)；使用本技能不需本機報告或專案影片。

| 已閱讀資料 | 用途與界線 |
|---|---|
| ByteDance 的[長影片對白範例](https://bytedance.larkoffice.com/wiki/NjnWwvf4BiFYFLk2RzrcEgaunGf#Kepid00aXojXyAxGSmKcaOv0nzc)與[聲音參考章節](https://bytedance.larkoffice.com/wiki/NjnWwvf4BiFYFLk2RzrcEgaunGf#Gvstd4xHuoF0yFxQTSHcx2esnGf) | 具體表情、聲線變化與情緒原因如何轉成可辨識表演。特寫與細緻時間只是範例，不是逐身體部位排程。最終生成範例未獨立檢視。 |
| Dreamina [Prompt](https://dreamina.capcut.com/seedance/seedance-2-5-prompt) 與 [Motion Reference](https://dreamina.capcut.com/seedance/seedance-2-5-motion-reference-guide) | 可觀察指示、視線及來源用途可填補實際表演缺口；不能證明「越短越自然」或「細節越多越好」。 |
| [FlyAIgh 表演指示稽核](https://www.flyaigh.com/blog/guide-ai-video-acting-directions) | 已讀公開提示詞、方法與結果表。兩個輸出是五與八秒的純文字輸入，未獨立逐影格檢視，不能當成受控比較。 |
| [Higgsfield 提示詞指引](https://higgsfield.ai/blog/seedance-2-5-prompting-guide) 與 [Pray 真人參考教學](https://www.prayproductionstudio.com/tutorials/seedance-video-references) | 前者使用詳細多鏡頭案例，後者使用真人對白參考；輸入差異不能支持「粗預演已包含臉或聲線表演」的假設。 |
| Emily2040 [表演卡](https://github.com/Emily2040/seedance-2.0/blob/main/references/performance-example-cards.md)與[流程](https://github.com/Emily2040/seedance-2.0/blob/main/references/reference-workflow.md) | 來源用途、預估朗讀時間及分開檢查說話／對嘴具有參考價值；卡片註明未生成，2.0 脈絡也不能證明 2.5 能力。 |
| 使用者審閱與授權 | 使用者看過安靜邀請與爭執轉失落案例後，要求關鍵轉折能看見細微表情，並授權撰寫指引。這核准的是寫作方法，不是影片自然度、時長或成功率測試；三段情緒及結尾都不是通用規則。 |

因此寫作時，要把觸發資訊連到可見變化，讓聽者在關鍵資訊到來時反應，讓情緒跨段延續，並依鏡頭實際看得到的程度選細節。保留來源用途與大致時間組織，允許強烈或克制的表演，不新增強制測試、素材或核准階段。

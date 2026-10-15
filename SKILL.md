---
name: travel-photo-cards
description: 把一批旅行照片做成小红书/抖音风格的 3:4 图文卡片组（1242×1656 PNG，一张 HTML 渲染出整套）。Turn a folder of travel photos into a ready-to-post deck of 3:4 editorial cards (1242×1656 PNG, one HTML renders the whole deck). 触发词：小红书图文、抖音图文、旅行照片排版、3:4 卡片、图文卡片、旅行纪念册图片版、自驾/车宿路书图文、把照片做成图文；English triggers: travel photo cards, photo essay deck, RED/Xiaohongshu style cards, 3:4 image cards, trip recap cards, travel carousel. 也适用于"真实路线地图"（高德瓦片拼接）、照片自然比例排版、公共图片来源（Wikimedia Commons CC 图）等子任务——即使用户没说"小红书"三个字。
---

# 旅行照片 → 3:4 图文卡片组

把一个照片文件夹 + 行程信息，做成一套可直接发布到小红书/抖音的竖版图文卡片。
本仓库自带全部脚本（`scripts/`），示例见 `examples/`。

## 产出规格

- 单卡 1242×1656px（3:4，小红书/抖音通用），整套一个 HTML 渲染成一个多页 PDF，再按页切 PNG
- 每张卡片有明确职责：封面（最强照片+大标题）→ 路线/概览 → 数据卡 → 逐日/逐地卡 → 盘点/攻略卡 → 结尾卡
- 总数 ≤18（小红书单篇上限），13–17 张最佳；示例演示用 10 张

## 环境

- Python 3.9+ 与 `pip install pillow pymupdf`
- 渲染器（`scripts/html2pdf.py` 自动发现，任一即可）：
  1. `pip install playwright && playwright install chromium`
  2. Node + playwright（NODE_PATH 指向含 playwright 的 node_modules）
  3. 本机已有的 Edge / Chrome（Windows 与 macOS 桌面机通常自带）
- Windows 字体直接用；macOS/Linux 由 `scripts/fontpick.py` 自动回退（PingFang/Noto CJK）

## 工作流

1. **清点照片**：`python scripts/contact_sheet.py <照片目录> select` 生成带编号标签的缩略拼版，逐张目检选图。**先看再选**：确认地点归属、方向是否颠倒。
2. **预处理**：`python scripts/prep_photos.py <照片目录> photos_work`——手机原图常带 EXIF 旋转标记，必须转正；同时压到 ≤2000px。输出的真实宽高表用于第 4 步。
3. **路线图二选一或都用**：开头放**卡通顺序环/示意图**（SVG 虚线环只表达先后关系，可写较多注释）；结尾放**真实轨迹图**（`python scripts/amap_route_map.py route.json`，高德瓦片拼接，只标每天的进程徽章，不加细致标注——真实地图信息一多文字必然互相覆盖）。
4. **排版生成**：所有照片槽位用 `scripts/aspect_row.py` 的 `gen_row()` 按图片**真实宽高比**计算（PIL 读尺寸，等高排布、宽度=高×比例；放不下的照片直接删，宁可少放不要压扁/怪异裁切）。竖图配竖槽、横图配横槽。
5. **渲染 → 蒙太奇目检 → 修正**：`html2pdf.py` 出 PDF，`render_cards.py` 切 PNG，`review_montage.py` 拼版逐张目检。重点查：图片是否被压扁、跨卡重复用图、文字溢出拆页（**页数 > 卡片数即有溢出**）。
6. **打包交付**：`package_cards.py` 按发布名清单重命名 PNG 并打 zip，附小红书标题/话题建议。

## 设计系统（米白编辑刊）

- 底 `#F5F1E8` 宣纸米白；墨色文字 `#26221C`；点缀赭金 `#A6803C`（浅底上别用亮金）
- 大标题：细字重（300）+ 大字号 + 字距 6–8px（细、大、疏 = 高级感第一定律）
- 英文点缀：Georgia italic（`Route · In Order`、`No.04 — 17` 页码式标注）
- 竖排汉字：`writing-mode:vertical-rl; text-orientation:upright;` 楷体，立在图片旁（最出效果的一笔）
- 分隔全用 0.5–1px 发丝线账本行，**无圆角、无彩色色块、无底色框**
- 照片通栏出血（贴卡片边缘）+ 少量留白；封面文字压在照片暗部渐晕上
- 图注用小号灰字（照片内容 + 拍摄时间），像杂志图片说明

**英文受众排版**（完整参考 `examples/kyoto-en/`）：标题用大号细无衬线（weight 300，字距 2–3px），不用竖排 CJK，改用 Georgia 斜体大号引言做视觉锚点（Gion 卡）或多行堆叠大标题（Arashiyama 卡）；账本行英文标签左对齐、数值右对齐 Georgia。英文文案保持克制、观察式、不用感叹号和营销腔。同一套 HTML 双语各出一份时，照片目录可用相对路径共享（`../kyoto/photos_work/`），避免重复存图。

## 照片排版铁律（每条都是实测教训）

1. **槽位比例 = 照片原生比例**。竖图配竖槽、横图配横槽；用 PIL 读真实尺寸算槽位，不要目测。
2. **放不下就删**。怪异裁切比少一张图更伤。
3. **同一张照片不要跨卡重复**（封面背景除外）。
4. **通栏横幅只用于抽象/氛围图**。竖构图人像、招牌、特写塞进横幅=灾难。
5. 卡通/示意地图只表达先后关系（一个圈按顺序读完），真实地图只标每天进程徽章——两边的文字密度都要克制，真实地图上叠加细致标注必然文字互相覆盖。

## 公共图片来源（Wikimedia Commons）

需要示例/演示素材时，用 `scripts/fetch_commons.py`：

- `search` 列出候选（尺寸 | 许可 | 作者），**逐张人工核验地点归属**（搜索同名地点会混入外地）；
- `download` 取定宽缩图并自动把 `文件 | 作者 | 许可 | 来源页` 追加进 `credits.tsv`；
- **CC 授权信息必须写进尾注卡**，照片权利归原作者；
- 直连 upload.wikimedia.org 失败（部分国内网络）时自动经 wsrv.nl 图片代理重试；
- Wikimedia API 对并发限流（429）：脚本已内置退避重试，仍应避免多进程并发调用。

## 常见坑（实测）

- **同一行 cmd 里 `set` 的变量不展开**（`set K=path&& python ... %K%` 会把 `%K%` 当字面量）。路径直接写全，或分两行。
- **多行内联 `python -c` 会静默失败或吞输出**：超过一行的 Python 逻辑写成 .py 文件再跑。
- **不要把脚本命名为 `inspect.py`** 等标准库同名文件——会遮蔽 stdlib，导致其他脚本报 `module 'inspect' has no attribute 'signature'`。
- **`open(p,"w").write(open(p).read()...)` 会先截断再读**，直接清空文件。读和写分开两步。
- **输出 PDF 被占用（EBUSY/Permission denied）**：用户可能正开着 PDF 预览。渲染到 `_new.pdf`，让用户关掉后重命名。
- **EXIF 方向**：不 `exif_transpose` 竖拍图会横躺；`prep_photos.py` 已处理。
- 多轮补丁互相覆盖导致状态混乱时：先转储相关段落真实字节（repr），基于事实写幂等修正脚本（能匹配才改，改过自动跳过）。

## 打包清单（一套交付）

1. `cards.pdf`（预览）+ 按序命名的 PNG（`01_封面.png`…，`names.txt` 给 `package_cards.py`）
2. `cards.html`（可改字重重新渲染）
3. 小红书发布建议：标题（数字+情绪，≤20 字）、正文（账本展开+评论区引导）、话题标签

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Tech Stack
- **Frontend**: Vue 3 + Vite + Tailwind CSS + Vue Router + Axios
- **Backend**: Python FastAPI + SQLAlchemy + SQLite
- **TTS**: Browser Web Speech API + edge-tts for server-side

## Build & Run

### Systemd Services (production / auto-start)
Both services are system-level systemd services, running as user `xsq`:

```bash
# Backend (port 9000)
sudo systemctl [start|stop|restart|status] happy-learning-backend

# Frontend (port 5173)
sudo systemctl [start|stop|restart|status] happy-learning-frontend

# Ngrok tunnel (forward 5173 to public)
sudo systemctl [start|stop|restart|status] happy-learning-ngrok
# Tunnel URL: curl -s http://localhost:4040/api/tunnels | python3 -c "import sys,json; d=json.load(sys.stdin); [print(t['public_url']) for t in d['tunnels']]"

# Service files: /etc/systemd/system/happy-learning-{backend,frontend}.service
```

> 重启服务时不要关闭其他端口的服务，仅重启后端 9000 端口或前端 5173 端口。

### Manual Run (dev / debugging)
```bash
# Backend (port 9000)
cd /home/xsq/happy-learning && python3 -m uvicorn app.main:app --port 9000

# Frontend dev (port 5173)
cd /home/xsq/happy-learning/frontend && npm run dev

# Frontend build (served by FastAPI in production)
cd /home/xsq/happy-learning/frontend && npm run build
```

## Content Scripts
- `scripts/generate_questions.py` — 生成 Big Muzzy 题库（6种题型），从 MUZZY_DATA 配置生成
- `scripts/import_muzzy_cards.py` — 导入 Muzzy 单词图卡到数据库
- `scripts/import_muzzy_from_anki.py` — ⚠️ 旧版：从 Anki .apkg 导入（图片顺序错误，已废弃）
- `scripts/import_muzzy_from_docx.py` — ✅ 当前：从 .docx 导入 Big Muzzy 题库（图片正确）
- `scripts/import_yakka_dee.py` — 导入 Yakka Dee 单词图卡
- `scripts/import_nc_english.py` — 导入新概念英语内容
- `scripts/setup_textbooks.py` — 创建教材和单元记录

### Big Muzzy 题库生成流程（从原始 .doc 文件）

原始 .doc 文件位于 `F:\1.英语启蒙\Big Muzzy 玛泽的故事\07、单词图卡可打印\`（共12个 unit 文件）。

**步骤 1：将 .doc 复制到 ASCII 路径**（避免 PowerShell 中文编码问题）
```bash
# 在 WSL 中
cp "/mnt/f/1.英语启蒙/Big Muzzy 玛泽的故事/07、单词图卡可打印/Unit01.doc" /tmp/muzzy_ascii/unit01.doc
# ... 对 unit01-unit12 重复
```

**步骤 2：用 Word COM 将 .doc 转为 .docx**（在 Windows PowerShell 中执行）
```powershell
# /tmp/convert_one.ps1 模板（修改 NN 为单元号）
$srcFile = "\\wsl.localhost\Ubuntu\tmp\muzzy_ascii\unitNN.doc"
$outFile = "C:\temp\muzzy_docx\unitNN.docx"
New-Item -ItemType Directory -Path "C:\temp\muzzy_docx" -Force | Out-Null
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open($srcFile, $false, $true)
    $doc.SaveAs2($outFile, 12)  # format 12 = wdFormatXML，实际生成 .docx
    $doc.Close([ref]$false)
} finally {
    $word.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
}
```
> ⚠️ 必须用 `SaveAs2($path, 12)` 而非 `SaveAs([ref]$path, [ref]8)`。format 8 (HTML) 会挂起，format 12 生成正确的 .docx ZIP 文件。

从 WSL 调用：
```bash
powershell.exe -ExecutionPolicy Bypass -File /tmp/convert_one.ps1
```

**步骤 3：从 .docx 提取图片和文字**
```python
import zipfile, re, os
with zipfile.ZipFile("unitNN.docx") as zf:
    # 提取图片到 /tmp/muzzy_final_images/NN/
    for name in zf.namelist():
        if name.startswith('word/media/'):
            data = zf.read(name)
            with open(f"/tmp/muzzy_final_images/NN/{os.path.basename(name)}", 'wb') as f:
                f.write(data)
    # 解析 rId→图片 映射
    rels_xml = zf.read('word/_rels/document.xml.rels').decode('utf-8')
    rid_to_image = {m.group(1): os.path.basename(m.group(2))
                    for m in re.finditer(r'Id="(rId\d+)"[^>]*Target="(media/[^"]*)"', rels_xml)}
    # 按文档顺序提取 图片-单词-句子
    doc_xml = zf.read('word/document.xml').decode('utf-8')
    paragraphs = re.findall(r'<w:p[^>]*>(.*?)</w:p>', doc_xml, re.DOTALL)
    # 每个段落提取 <w:t> 文本和 r:embed 图片引用
    # 图片段落开始新条目，后续文本段落追加到当前条目
```

**步骤 4：运行导入脚本**
```bash
python3 scripts/import_muzzy_from_docx.py
```
该脚本自动完成：解析 .docx → 复制图片到 `data/muzzy_word_cards/NN/` → 清理旧数据 → 生成6种题型 → 写入数据库。

**重要说明**：
- Anki .apkg 中的图片按 OLE2 二进制存储顺序排列，与文档顺序不一致（~97% 的图片映射错误）
- .docx 的 `word/media/` 图片按文档顺序排列，`document.xml` 中的文字与图片正确对应
- 因此必须从 .docx 提取，不能用 Anki 图片

## Architecture

### Data Model
- **Textbook** → contains Units + VocabWords
- **Unit** → contains Questions + VocabWords, has video_path
- **Question** → 6 types: `image_select_word`, `image_select_sentence`, `listen_select`, `listen_spell`, `listen_spell_sentence`, `image_listen_spell_sentence`
- **User** → has avatar (emoji), Scores, DailyProgress, UnitProgress
- **VocabWord** → word with image_path and example_sentence

### Static Mounts
- `/muzzy_word_cards/` → `data/muzzy_word_cards/`
- `/yakka_dee/` → `data/yakka_dee/`
- `/` → `frontend/dist/` (production only)

### Frontend Routes
`/` (avatar select) → `/dashboard` → `/video/:unitId` → `/quiz/:unitId` → `/results`

### Key Routers
- `users` — user CRUD
- `courses` — textbooks listing (legacy alias in frontend)
- `questions` — by unit/textbook, quiz generation, word-to-image
- `scores` — record scores, unit completion, user scores
- `progress` — daily/unit progress tracking
- `media` — video streaming from `data/videos/`
- `tts` — text-to-speech endpoint

## Code Style
- Python: PEP 8, snake_case functions/variables
- Vue: `<script setup>` composition API, kebab-case components
- No comments unless WHY is non-obvious

## Conventions
- Use planning-with-files skill for multi-step tasks
- Phase-based development tracked in task_plan.md
- Content import scripts in `scripts/` for different sources (Muzzy, Yakka Dee, NC English)

## Deployment
- Linux 生产部署使用 systemd 服务（见上方 Systemd Services 部分）
- Windows Server 2022 部署使用 NSSM + IIS 反向代理，详见 `DEPLOY_WINDOWS.md`
- 所有路径已改为相对路径或基于 `__file__` 的动态路径，跨平台兼容
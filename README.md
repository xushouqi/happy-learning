# 🌟 快乐学英语 (Happy Learning)

一款面向少儿的英语启蒙互动学习应用，支持**在线 Web 版**和 **Android 离线版**。融合视频教学、互动课程、多题型答题、语音朗读与发音练习，让孩子在游戏中快乐学英语。

---

## ✨ 功能特色

### 🎓 互动课程
- **故事开场**：中文引入，激发学习兴趣
- **词卡学习**：图文结合，点击即听发音（Big Muzzy / Oxford Phonics World）
- **听音选图**：播放单词发音，从多张图卡中点选正确答案
- **看图选词**：显示图片，从多个单词中选择匹配项
- **句子跟读**：图片 + 例句 + 发音示范，培养语感

### 📝 多题型答题（6 种题型）
| 题型 | 说明 |
|------|------|
| `image_select_word` | 看图选词（790 题） |
| `image_select_sentence` | 看图选句（173 题） |
| `listen_select` | 听音选词（764 题） |
| `listen_spell` | 听音拼词（763 题） |
| `listen_spell_sentence` | 听音排列句子（131 题） |
| `image_listen_spell_sentence` | 看图听音组句（131 题） |

- 支持**单题型练习**和**混合模式**
- 支持按单元或按教材出题

### 🎤 语音功能
- **服务端 TTS**：Microsoft Edge TTS 神经网络语音（`en-US-GuyNeural`），发音自然
- **客户端 TTS**：Android 原生 TTS 插件 + Web Speech API 双回退
- **预生成音频**：离线版打包全部单词/句子的高质量 mp3，无需联网
- **语音评测**（实验性）：Web Speech API 识别用户发音，对比评分

### 👦 多用户系统
- Emoji 头像选择（🦄 🐰 🐶 等）
- 独立学习进度与成绩记录
- 错题本：自动收集做错的题目，支持重做

### 📊 学习追踪
- **每日进度**：记录每天完成的单元和得分
- **单元进度**：最佳分数、尝试次数、完成状态
- **学习日历**：可视化展示学习打卡记录
- **题型统计**：按题型分析正确率

### 📱 多平台支持
- **Web 版**：响应式设计，手机/平板/电脑均可访问
- **Android APK**：基于 Capacitor，数据内嵌，完全离线可用
- **Linux 服务器**：systemd 一键部署
- **Windows Server**：IIS 反向代理 + NSSM 服务

---

## 🛠 技术栈

### 前端
| 技术 | 版本 | 用途 |
|------|------|------|
| Vue 3 | 3.5+ | UI 框架（Composition API + `<script setup>`） |
| Vite | 6.0+ | 构建工具 |
| Tailwind CSS | 3.4+ | 原子化 CSS |
| Vue Router | 4.4+ | SPA 路由（History 模式） |
| Axios | 1.7+ | HTTP 客户端 |
| Capacitor | 8.5+ | Android 原生封装 |
| @capacitor-community/text-to-speech | 8.0+ | Android 原生 TTS |

### 后端
| 技术 | 用途 |
|------|------|
| Python 3.12+ | 运行环境 |
| FastAPI | Web 框架 |
| SQLAlchemy | ORM |
| SQLite | 数据库（零配置，文件存储） |
| edge-tts | 服务端神经网络语音合成 |

### 配色方案
- 🌸 Primary: `#FF6B6B`（珊瑚粉）
- 🌊 Secondary: `#4ECDC4`（薄荷绿）
- 🌻 Accent: `#FFE66D`（向日葵黄）

---

## 📁 项目结构

```
happy-learning/
├── app/                          # 后端 (FastAPI)
│   ├── main.py                   # 应用入口、路由注册、静态文件挂载
│   ├── database.py               # SQLite 连接配置
│   ├── models/__init__.py        # 数据模型 (11 张表)
│   ├── schemas.py                # Pydantic 请求/响应模型
│   ├── routers/
│   │   ├── users.py              # 用户 CRUD
│   │   ├── courses.py            # 教材/单元列表
│   │   ├── questions.py          # 题目查询、组卷、词图映射
│   │   ├── scores.py             # 成绩记录、错题本、题型统计
│   │   ├── media.py              # 视频流媒体
│   │   ├── tts.py                # Edge TTS 语音合成
│   │   └── course_module.py      # 互动课程（步骤式教学）
│   └── services/
│       ├── question_generator.py # 题目生成器
│       └── script_parser.py      # 脚本解析器
│
├── frontend/                     # 前端 (Vue 3 + Vite)
│   ├── src/
│   │   ├── App.vue               # 根组件
│   │   ├── main.js               # 入口
│   │   ├── router.js             # 路由配置（16 个页面）
│   │   ├── api/index.js          # API 客户端（含离线适配）
│   │   ├── lib/tts.js            # 统一发音模块（预生成音频 → 原生TTS → Web Speech）
│   │   ├── views/                # 页面组件
│   │   │   ├── AvatarSelect.vue  # 头像选择/登录
│   │   │   ├── Dashboard.vue     # 主页（互动课程 + 单元列表）
│   │   │   ├── CourseList.vue    # 课程列表
│   │   │   ├── CourseDetail.vue  # 课程详情（课时列表）
│   │   │   ├── LessonPlayer.vue  # 课时互动播放器
│   │   │   ├── VideoPlayer.vue   # 视频播放
│   │   │   ├── QuizTypeSelect.vue# 题型选择
│   │   │   ├── Quiz.vue          # 答题界面（6种题型）
│   │   │   ├── SpeechPractice.vue# 语音练习
│   │   │   ├── SpeechQuiz.vue    # 语音测评
│   │   │   ├── Results.vue       # 答题结果
│   │   │   ├── WrongBook.vue     # 错题本
│   │   │   ├── Progress.vue      # 学习进度
│   │   │   └── Calendar.vue      # 学习日历
│   │   ├── offline/              # 离线模式支持
│   │   │   ├── api.js            # Axios 离线适配层
│   │   │   ├── data.js           # 数据加载入口
│   │   │   ├── data-embedded.js  # 内嵌数据（打包生成）
│   │   │   ├── audio-map.js      # 文本→音频文件映射
│   │   │   ├── content.js        # 课程内容离线组装
│   │   │   └── quiz.js           # 答题逻辑离线适配
│   │   └── assets/style.css      # 全局样式
│   ├── capacitor.config.json     # Capacitor 配置
│   ├── android/                  # Android 原生工程
│   ├── vite.config.js            # Vite 配置（含开发代理）
│   └── tailwind.config.js        # Tailwind 主题配置
│
├── data/                         # 数据目录（不纳入 Git）
│   ├── english_learning.db       # SQLite 数据库
│   ├── muzzy_word_cards/         # Big Muzzy 单词图卡（12 个 unit）
│   ├── phonics/                  # Oxford Phonics World 页面图
│   └── videos/                   # 教学视频
│
├── scripts/                      # 数据导入/生成脚本
│   ├── seed_courses.py           # 📚 互动课程种子数据（84KB 配置）
│   ├── import_muzzy_from_docx.py # Big Muzzy 题库导入（从 .docx）
│   ├── import_nc_english.py      # 新概念英语内容导入
│   ├── import_yakka_dee.py       # Yakka Dee 单词图卡导入
│   ├── generate_questions.py     # 题目生成器
│   ├── export_offline_data.py    # 导出离线数据 JSON
│   ├── generate_offline_audio.py # 预生成离线语音（edge-tts）
│   └── setup_textbooks.py        # 教材/单元初始化
│
├── deploy/
│   └── happy-learning-backend.service  # systemd 服务文件
│
├── DEPLOY_WINDOWS.md             # Windows Server 部署指南
├── CLAUDE.md                     # 开发文档
└── README.md                     # 本文件
```

---

## 🚀 快速开始

### 环境要求

- **Python** 3.12+
- **Node.js** 20+（前端构建）
- **Git**

### 1. 克隆仓库

```bash
git clone https://github.com/xushouqi/happy-learning.git
cd happy-learning
```

### 2. 后端启动

```bash
# 安装依赖
pip install fastapi uvicorn[standard] sqlalchemy edge-tts pydantic

# 启动 API 服务（端口 9000）
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9000
```

数据库 (`data/english_learning.db`) 首次启动时自动创建。如需导入示例数据：

```bash
python3 scripts/setup_textbooks.py
python3 scripts/import_muzzy_from_docx.py
python3 scripts/seed_courses.py
```

### 3. 前端开发

```bash
cd frontend
npm install
npm run dev          # 开发服务器 → http://localhost:5173
```

开发模式下 Vite 自动将 `/api`、`/muzzy_word_cards`、`/yakka_dee` 请求代理到后端 9000 端口。

### 4. 前端生产构建

```bash
cd frontend
npm run build        # 输出到 frontend/dist/
```

生产模式下 FastAPI 直接托管 `frontend/dist/` 静态文件，**无需单独的前端服务**。

---

## 🏭 生产部署

### Linux (systemd)

```bash
# 复制服务文件
sudo cp deploy/happy-learning-backend.service /etc/systemd/system/

# 启动
sudo systemctl daemon-reload
sudo systemctl enable --now happy-learning-backend

# 管理
sudo systemctl status happy-learning-backend
sudo systemctl restart happy-learning-backend
```

服务运行在端口 9000，建议前面加 Nginx 反向代理 + SSL。

```
nginx (80/443) → uvicorn (9000)
                   ├── /api/*          → FastAPI 路由
                   ├── /muzzy_word_cards/ → 静态图卡
                   ├── /phonics/        → 静态页面
                   └── /*               → SPA (frontend/dist/)
```

### Windows Server 2022

详见 [DEPLOY_WINDOWS.md](DEPLOY_WINDOWS.md)。

```
IIS (80/443, SSL) → 反向代理 → uvicorn (9000, NSSM 服务)
```

---

## 📱 Android 离线版

基于 [Capacitor](https://capacitorjs.com/) 封装为原生 Android 应用，所有数据内嵌，无需网络连接。

### 构建 APK

```bash
cd frontend

# 1. 导出离线数据
python3 scripts/export_offline_data.py

# 2. 预生成语音
python3 scripts/generate_offline_audio.py

# 3. 构建前端（离线模式）
VITE_OFFLINE=true npm run build

# 4. 同步到 Android
npx cap sync android

# 5. 用 Android Studio 打开
npx cap open android
```

### 离线架构
- **数据**：`data-embedded.js` 内嵌全部教材/课程/单词数据为 JS 模块
- **音频**：预生成 mp3 打包到 `public/audio/`，通过 `audio-map.js` 映射
- **API**：`offline/api.js` 拦截 Axios 请求，返回本地数据
- **TTS**：优先播放预生成音频 → 回退到 Capacitor 原生 TTS → 回退到 Web Speech API

---

## 📖 数据模型

```
Textbook (教材)
  ├── Unit (单元)          ← 每个单元有视频、单词、题目
  │     ├── Question (题目) ← 6 种题型，JSON 格式选项
  │     └── VocabWord (单词) ← 含图卡路径和例句
  └── Course (课程)         ← 互动课程，挂在单元上
        └── CourseLesson (课时) ← JSON 步骤：story → learn → listen_tap → ...

User (用户)
  ├── Score (答题记录)
  ├── DailyProgress (每日进度)
  ├── UnitProgress (单元进度)
  └── CourseProgress (课时进度 + 星星)
```

---

## 🔌 API 端点

### 用户 `/api/users`
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 列出所有用户 |
| POST | `/` | 创建用户（name + avatar） |
| GET | `/{id}` | 获取用户信息 |

### 教材与单元 `/api/textbooks` `/api/units`
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/textbooks/` | 列出教材（含单元） |
| GET | `/textbooks/{id}` | 获取教材详情 |
| GET | `/units/{id}` | 获取单元详情 |

### 题目 `/api/questions`
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/unit/{unit_id}` | 获取单元所有题目 |
| GET | `/quiz/{unit_id}` | 组卷（支持题型筛选） |
| GET | `/types/{unit_id}` | 获取单元可用题型 |
| GET | `/textbook/{textbook_id}` | 获取教材所有题目 |
| GET | `/word-to-image` | 单词→图卡路径映射 |
| GET | `/by-ids` | 按 ID 批量获取 |

### 成绩 `/api/scores`
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/` | 记录答题得分 |
| GET | `/user/{user_id}` | 用户成绩列表 |
| POST | `/unit-complete` | 完成单元（更新最佳分数 + 每日进度） |
| GET | `/user/{user_id}/wrong-questions` | 错题列表 |
| GET | `/user/{user_id}/wrong-questions/quiz` | 错题重做组卷 |
| GET | `/user/{user_id}/type-stats` | 按题型统计正确率 |

### 课程模块 `/api/course`
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 课程列表（按教材分组） |
| GET | `/{id}` | 课程详情（含课时列表 + 进度） |
| GET | `/{course_id}/lesson/{lesson_id}/content` | 课时互动内容（动态组装游戏题） |
| POST | `/lesson-complete` | 完成课时（记录星星） |
| GET | `/progress/{user_id}` | 用户课程进度 |

### 其他
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| GET | `/api/tts/speak?text=...` | 文本转语音（Edge TTS） |
| GET | `/api/media/video/{filename}` | 视频流 |

---

## 🗺️ 前端路由

| 路径 | 页面 | 说明 |
|------|------|------|
| `/` | AvatarSelect | 选择头像/用户 |
| `/dashboard` | Dashboard | 主页（课程入口 + 单元列表） |
| `/courses` | CourseList | 互动课程列表 |
| `/courses/:courseId` | CourseDetail | 课程详情（课时列表） |
| `/courses/:courseId/lesson/:lessonId` | LessonPlayer | 课时互动播放器 |
| `/video/:unitId` | VideoPlayer | 视频播放 |
| `/quiz-type/:unitId` | QuizTypeSelect | 选择答题题型 |
| `/quiz/:unitId` | Quiz | 答题界面 |
| `/quiz/wrong` | Quiz | 错题重做 |
| `/results` | Results | 答题结果 |
| `/speech-practice` | SpeechPractice | 语音练习 |
| `/speech-quiz/:unitId` | SpeechQuiz | 语音测评 |
| `/wrongbook` | WrongBook | 错题本 |
| `/progress` | Progress | 学习进度 |
| `/calendar` | Calendar | 学习日历 |

---

## 📦 内容来源

| 教材 | 说明 | 导入脚本 |
|------|------|----------|
| **Big Muzzy** | BBC 英语启蒙动画，12 个单元，612+ 单词，配图 + 例句 | `import_muzzy_from_docx.py` |
| **Oxford Phonics World** | 牛津自然拼读，5 级，字母/发音规则页面 | `import_yakka_dee.py` |
| **新概念英语** | 经典教材，课文 + 单词 | `import_nc_english.py` |

> Big Muzzy 题库必须从 `.docx` 文件导入（`.doc` 需先用 Word COM 转为 `.docx`），因为 Anki 卡包的图片按 OLE2 二进制存储顺序排列，与文档顺序不一致（~97% 映射错误）。详见 [CLAUDE.md](CLAUDE.md)。

---

## ⚙️ 配置

### Vite 开发代理 (`frontend/vite.config.js`)
```
/api/*            → http://localhost:9000
/muzzy_word_cards → http://localhost:9000
/yakka_dee        → http://localhost:9000
```

### Tailwind 主题 (`frontend/tailwind.config.js`)
自定义色：`primary` `secondary` `accent` `sky` `grass`

### Capacitor (`frontend/capacitor.config.json`)
```json
{
  "appId": "com.xsq.happylearning",
  "appName": "快乐学英语",
  "webDir": "dist"
}
```

### 离线模式开关
```bash
# .env 或构建命令
VITE_OFFLINE=true   # 启用离线数据适配层
```

---

## 📊 当前数据规模

| 项目 | 数量 |
|------|------|
| 教材 | 2（Big Muzzy + Oxford Phonics World） |
| 单元 | 17 |
| 题目 | 2,752 |
| 单词 | 612 |
| 互动课程 | 17（56 课时） |
| 图卡 | 12 个 unit × ~20 张 |

---

## 🤝 开发约定

- **Python**: PEP 8，snake_case
- **Vue**: `<script setup>` Composition API，kebab-case 组件
- **不加注释**，除非有非显而易见的 WHY
- 使用 `planning-with-files` skill 进行多步骤任务
- 阶段性开发记录在 `task_plan.md`
- 内容导入脚本统一放在 `scripts/`

---

## 📄 License

Private project — 仅供个人/家庭使用。

---

<p align="center">
  Made with ❤️ for happy learners
</p>

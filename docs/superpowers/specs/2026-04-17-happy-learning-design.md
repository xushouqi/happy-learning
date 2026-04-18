# 快乐学英语 - 应用设计文档

**日期：** 2026-04-17
**用户场景：** 为6岁双胞胎女儿创建英语每日一练应用
**课程内容：** Big Muzzy, Didi's Day, Oxford Phonics World

---

## 需求概述

- 两个女儿各自账号，用卡通头像区分
- 每日练习20-30分钟，5-10道题目
- 三种题型：听音选图/选词、看图选词、拼词组句（跟读评分暂不做）
- 视频内嵌播放，先观看再做题
- AI 根据台词本自动出题，后续支持手动修改补充
- 记录每人每日分数和进度

## 技术栈

| 层 | 选择 | 原因 |
|---|---|---|
| 前端 | Vue 3 + Vite | 轻量、响应式、适合卡片动画 |
| UI框架 | Tailwind CSS | 快速构建彩色卡通风格 |
| 后端 | Python FastAPI | 高性能、异步支持 |
| 数据库 | SQLite + SQLAlchemy | 零配置、本地部署足够 |
| 发声 | 浏览器 Web Speech API | 免费、无需额外服务 |
| 视频 | HTML5 Video + 后端流式传输 | 支持本地文件 |

## 系统架构

```
浏览器 (Vue 3 SPA)
  ├── 头像选择页
  ├── 学习主页（课程卡片、今日挑战、进度条）
  ├── 视频学习页（HTML5 播放器）
  ├── 答题页（一题一屏、即时反馈、动画）
  └── 成绩页（总分、星星奖励、错题回顾）
        │
        │ REST API
        ▼
FastAPI 后端
  ├── 用户管理 API
  ├── 课程/单元/题目管理 API
  ├── 分数/进度记录 API
  ├── 题目生成器（解析台词本 → 自动出题）
  └── 本地文件服务（视频/音频流式传输）
        │
        ▼
SQLite 数据库
  ├── users
  ├── courses
  ├── units
  ├── questions
  ├── scores
  └── daily_progress
```

## 数据库设计

### users
| 字段 | 类型 | 说明 |
|---|---|---|
| id | PK | 自增主键 |
| name | VARCHAR | 昵称（姐姐/妹妹） |
| avatar | VARCHAR | 头像编号（卡通角色） |
| created_at | DATETIME | 创建时间 |

### courses
| 字段 | 类型 | 说明 |
|---|---|---|
| id | PK | 自增主键 |
| name | VARCHAR | 课程名（Big Muzzy / Didi's Day / Oxford Phonics） |
| video_path | VARCHAR | 视频文件路径 |
| source_path | VARCHAR | 台词本路径 |
| status | VARCHAR | 状态（active / inactive） |

### units
| 字段 | 类型 | 说明 |
|---|---|---|
| id | PK | 自增主键 |
| course_id | FK | 所属课程 |
| name | VARCHAR | 单元名称 |
| script_path | VARCHAR | 台词本路径 |
| order | INT | 排序 |

### questions
| 字段 | 类型 | 说明 |
|---|---|---|
| id | PK | 自增主键 |
| unit_id | FK | 所属单元 |
| type | ENUM | listen_select / image_select_word / scramble_word |
| options | JSON | 选项数组 |
| answer | VARCHAR | 正确答案 |
| audio_text | VARCHAR | 用于TTS发音的文本 |

### scores
| 字段 | 类型 | 说明 |
|---|---|---|
| id | PK | 自增主键 |
| user_id | FK | 用户 |
| question_id | FK | 题目 |
| correct | BOOLEAN | 是否正确 |
| score | INT | 得分 |
| created_at | DATETIME | 答题时间 |

### daily_progress
| 字段 | 类型 | 说明 |
|---|---|---|
| id | PK | 自增主键 |
| user_id | FK | 用户 |
| unit_id | FK | 单元 |
| date | DATE | 练习日期 |
| total_score | INT | 总分 |
| completed | BOOLEAN | 是否完成 |

## 前端页面流程

### 1. 头像选择页
- 大圆头像 + 名字，点击即登录
- 无密码，适合6岁儿童

### 2. 学习主页
- 今日挑战卡片（高亮推荐）
- 三个课程大卡片（Big Muzzy / Didi's Day / Oxford Phonics）
- 进度条显示完成情况
- 支持添加新用户

### 3. 视频学习页
- 内嵌 HTML5 播放器
- 自动加载对应单元的视频
- "看完继续" 按钮（可配置跳过）

### 4. 答题页
- 一屏一题，5-10道题
- 三种题型：
  - **听音选图/选词**：点击播放按钮听发音，选择正确选项
  - **看图选词**：展示图片，选择对应单词
  - **拼词组句**：拖拽打乱的字母组成正确单词
- 选择后即时反馈（✅❌ 动画）
- 答对播放星星动画+音效

### 5. 成绩页
- 总分、正确率、星星奖励动画
- 错题回顾列表
- "再来一次" / "返回" 按钮

## 题目生成流程

1. 解析台词本文件（支持 .txt / .srt / .docx / PDF，格式待确认）
2. 提取词汇、句型、对话
3. AI 根据单元内容生成三种题型的题目
4. 存入数据库，支持手动编辑

## 目录结构

```
happy-learning/
├── app/                    # FastAPI 后端
│   ├── main.py             # 入口
│   ├── models/             # SQLAlchemy 模型
│   ├── routers/            # API 路由
│   ├── services/           # 业务逻辑
│   │   ├── question_generator.py  # 题目生成
│   │   └── script_parser.py       # 台词本解析
│   └── database.py         # 数据库配置
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   ├── components/     # 可复用组件
│   │   ├── api/            # API 调用
│   │   └── assets/         # 静态资源
│   └── package.json
├── data/                   # 数据库和上传的文件
│   └── english_learning.db
├── scripts/                # 辅助脚本
└── docs/                   # 文档
```

## 部署方式

- 本地运行：`python app/main.py` 启动后端，`npm run dev` 启动前端
- 生产模式：Vite build 后由 FastAPI 静态文件服务托管

# Task Plan: 快乐学英语 - 应用开发

## Goal
为6岁双胞胎女儿构建英语每日一练Web应用（Vue 3 前端 + FastAPI 后端 + SQLite），支持视频观看 + AI出题 + 三种题型练习 + 进度追踪。

## Current Phase
Phase 5

## Phases

### Phase 1: 项目初始化 & 基础架构
- [ ] 创建项目目录结构
- [ ] 初始化 FastAPI 后端（main.py, database.py, models）
- [ ] 初始化 Vue 3 前端（Vite + Tailwind CSS）
- [ ] 配置 SQLite + SQLAlchemy 数据库
- **Status:** complete

### Phase 2: 后端核心 - 数据层
- [x] 定义 SQLAlchemy 模型
- [x] 实现数据库迁移/初始化
- [x] 用户管理 API
- [x] 课程/单元/题目管理 API
- [x] 分数/进度记录 API
- **Status:** complete

### Phase 3: 前端核心 - 页面框架
- [x] 头像选择页
- [x] 学习主页
- [x] 路由和状态管理
- [x] API 请求封装
- **Status:** complete

### Phase 4: 前端核心 - 练习页面
- [x] 视频学习页
- [x] 答题页（三种题型框架）
- [x] 成绩页
- [x] 动画和交互反馈
- **Status:** complete

### Phase 5: 题目生成 & 本地文件服务
- [x] 台词本解析器（PDF 转文本，按集提取词汇）
- [x] 视频/音频流式传输 API（/api/media/video/）
- [x] 题目生成器（听音选词/看图选词/拼词 106题）
- [x] 视频文件 symlink 到 F 盘实际路径
- **Status:** complete

### Phase 6: 联调测试
- [x] 端到端流程跑通（登录 → 选课程 → 看视频 → 答题 → 看成绩）
- [ ] 修复问题
- **Status:** in_progress

## Key Questions
1. 台词本格式确认？（.txt / .srt / .docx）— 先支持 .txt 和 .srt
2. 视频文件放哪里？— 本地 data/videos/ 目录
3. AI 出题用哪个模型？— 用 Claude API，后续可替换
4. 后端和前端是否同端口运行？— 开发时分开端口，生产时 FastAPI 托管前端静态文件

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| Vue 3 + Vite + Tailwind CSS | 轻量、响应式、适合卡片动画，适合儿童UI |
| FastAPI + SQLite | 零配置、本地部署足够、异步支持 |
| SQLAlchemy ORM | Python 生态成熟、类型安全 |
| 浏览器 Web Speech API | 免费TTS，无需外部服务 |
| 本地文件存储（非云） | 家用场景，无需复杂部署 |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
|       | 1       |            |

## Notes
- 参考设计文档: docs/superpowers/specs/2026-04-17-happy-learning-design.md
- 开发时后端 9000 端口，前端 5173 端口
- 数据目录: data/ （数据库 + 视频 + 台词本）

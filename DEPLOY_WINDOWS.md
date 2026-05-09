# Windows Server 2022 生产部署指南

## 部署架构

```
公网 → IIS (80/443, SSL) → 反向代理 → uvicorn (端口 9000)
                                        ├── FastAPI API (/api/*)
                                        ├── 前端静态文件 (frontend/dist/)
                                        ├── 单词图卡 (/muzzy_word_cards)
                                        └── Yakka Dee (/yakka_dee)
```

生产模式下，前端构建为静态文件后由 FastAPI 统一托管，只需运行后端服务。

---

## 1. 环境准备

### 1.1 安装 Python 3.12+
1. 从 https://www.python.org/downloads/ 下载 Windows installer
2. 安装时勾选 **"Add Python to PATH"**
3. 验证: `python --version`

### 1.2 安装 Node.js 20+
1. 从 https://nodejs.org/ 下载 LTS 版本 Windows installer
2. 默认安装即可
3. 验证: `node --version` && `npm --version`

### 1.3 安装 Git for Windows
1. 从 https://git-scm.com/download/win 下载安装
2. 默认选项即可

### 1.4 确认端口
```powershell
netstat -ano | findstr ":9000 :80 :443"
```
如有占用，需先释放。

---

## 2. 项目安装

### 2.1 克隆项目
```powershell
git clone https://github.com/xushouqi/happy-learning.git C:\happy-learning
cd C:\happy-learning
```

### 2.2 安装 Python 依赖
```powershell
pip install -r app\requirements.txt
```

### 2.3 安装前端依赖并构建
```powershell
cd C:\happy-learning\frontend
npm install
npm run build
cd ..
```
构建产物输出到 `frontend\dist\`。

### 2.4 初始化数据库
数据库表会在首次启动时自动创建。如需导入内容数据：
```powershell
# 导入 Muzzy 单词图卡
python scripts\import_muzzy_cards.py

# 导入 Yakka Dee
python scripts\import_yakka_dee.py

# 导入新概念英语
python scripts\import_nc_english.py

# 生成题库
python scripts\generate_questions.py
```

### 2.5 手动测试启动
```powershell
cd C:\happy-learning
python -m uvicorn app.main:app --port 9000 --host 0.0.0.0
```
访问 `http://localhost:9000/docs` 确认 API 正常。

---

## 3. 注册为 Windows 服务

使用 [NSSM](https://nssm.cc/) 将 uvicorn 注册为 Windows 服务，实现开机自启和自动重启。

### 3.1 安装 NSSM
1. 从 https://nssm.cc/download 下载
2. 解压到 `C:\nssm`（选择 win64 版本）
3. 将 `C:\nssm\win64` 加入系统 PATH

### 3.2 创建服务
```powershell
nssm install happy-learning-backend
```

在 NSSM 界面中配置：

| 标签页 | 字段 | 值 |
|--------|------|-----|
| **Application** | Path | `C:\Python312\python.exe`（根据实际路径调整） |
| | Arguments | `-m uvicorn app.main:app --port 9000 --host 0.0.0.0` |
| | Startup directory | `C:\happy-learning` |
| **Details** | Display name | `Happy Learning Backend` |
| **Log on** | Account | 保持 LocalSystem |
| **I/O** | Output | `C:\happy-learning\logs\backend-stdout.log` |
| | Error | `C:\happy-learning\logs\backend-stderr.log` |
| **Rotate files** | 勾选 | 日志轮转（建议 10MB） |

### 3.3 启动服务
```powershell
nssm start happy-learning-backend

# 验证
curl http://localhost:9000/docs
```

### 3.4 常用命令
```powershell
nssm restart happy-learning-backend   # 重启
nssm stop happy-learning-backend      # 停止
nssm status happy-learning-backend    # 状态
nssm remove happy-learning-backend    # 删除服务
```

---

## 4. 配置 IIS 反向代理

### 4.1 安装 IIS 和必要组件
以管理员身份运行 PowerShell:
```powershell
# 安装 IIS
Install-WindowsFeature -Name Web-Server, Web-WebSockets -IncludeAllSubFeature

# 下载并安装 URL Rewrite Module
# https://www.iis.net/downloads/microsoft/url-rewrite

# 下载并安装 Application Request Routing (ARR)
# https://www.iis.net/downloads/microsoft/application-request-routing
```

### 4.2 启用 ARR 代理
在 IIS 管理器中：
1. 点击服务器根节点
2. 打开 **Application Request Routing Cache**
3. 右侧点击 **Server Proxy Settings**
4. 勾选 **Enable proxy**

### 4.3 配置反向代理规则
1. 在 IIS 中创建网站（或编辑 Default Web Site）
2. 绑定端口 80（和 443，如果有证书）
3. 打开 **URL Rewrite**
4. 添加 **Inbound Rule** → **Reverse Proxy**
5. 服务器名称填写: `localhost:9000`

或直接编辑 `web.config` 放在网站根目录：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <rule name="ReverseProxy" stopProcessing="true">
          <match url="(.*)" />
          <action type="Rewrite" url="http://localhost:9000/{R:1}" />
        </rule>
      </rules>
    </rewrite>
  </system.webServer>
</configuration>
```

### 4.4 配置 HTTPS 证书
- 使用自有证书：IIS 管理器 → 服务器证书 → 导入 → 网站绑定 443
- 或使用 Let's Encrypt：[win-acme](https://www.win-acme.com/) 自动签发

---

## 5. 防火墙配置

以管理员身份运行 PowerShell:
```powershell
New-NetFirewallRule -DisplayName "HTTP Inbound" -Direction Inbound -LocalPort 80 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "HTTPS Inbound" -Direction Inbound -LocalPort 443 -Protocol TCP -Action Allow
```

如果是云服务器（阿里云/AWS/腾讯云），还需在安全组中开放 80 和 443 端口。

---

## 6. 维护

### 更新代码
```powershell
cd C:\happy-learning
git pull
pip install -r app\requirements.txt
cd frontend && npm install && npm run build && cd ..
nssm restart happy-learning-backend
```

### 查看日志
```powershell
Get-Content C:\happy-learning\logs\backend-stderr.log -Tail 50
```

### 数据库备份
复制 `C:\happy-learning\data\english_learning.db` 到备份位置。

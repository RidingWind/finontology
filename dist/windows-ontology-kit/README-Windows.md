# 银行业务本体 —— Windows 部署说明

把这套东西搬到另一台 Windows 主机上。全部文件加起来不到 1 MB，唯一第三方依赖是 `owlready2==0.51`。

## 一、前置条件

| 项目 | 要求 | 说明 |
|---|---|---|
| Python | 3.11 ~ 3.13 | 安装时勾选 **Add python.exe to PATH** |
| Protégé | 5.6.9 Windows 版 | 可选，用于图形化查看/编辑本体，自带 JRE |
| WorkBuddy | 已安装 | 用于接入 MCP server（可选，不接也能用脚本） |

## 二、安装步骤

1. 把整个 `windows-ontology-kit` 目录拷到 PC 上，**路径不要含中文和空格**（例如 `D:\ontology-kit`）。
2. 双击 **`install.bat`**。它会自动完成：
   - 把真源脚本部署到 `%USERPROFILE%\.workbuddy\ontology-mcp`（**这个路径不能改**，脚本内部按它定位真源）
   - 创建虚拟环境 `%USERPROFILE%\.workbuddy\ontology-venv`
   - 安装 `owlready2==0.51`（清华源）
   - 合并写入 `%USERPROFILE%\.workbuddy\mcp.json`，已有配置会被保留
   - 与 server 做一次 MCP 握手冒烟测试
3. **完全退出 WorkBuddy 再重开**（MCP 配置是启动时读取的，不重启看不到）。
4. 连接器页面找到 **ontology** → 点**信任** → **新开一个会话**才会装载工具。
5. Protégé 里 File → Open，打开 `ontology\bank-enterprise.owl`。

## 三、日常用法

```bat
:: 重建本体（真源是 ontology-mcp\bank_seed.py，改模型改那里）
%USERPROFILE%\.workbuddy\ontology-venv\Scripts\python.exe ontology\build_bank_ontology.py

:: 职责分离检测（需要 java）
%USERPROFILE%\.workbuddy\ontology-venv\Scripts\python.exe ontology\check_separation_of_duty.py

:: 报送完整性 / 映射覆盖率 / 导出互斥矩阵
%USERPROFILE%\.workbuddy\ontology-venv\Scripts\python.exe ontology\check_reporting_integrity.py
%USERPROFILE%\.workbuddy\ontology-venv\Scripts\python.exe ontology\check_mapping_coverage.py
%USERPROFILE%\.workbuddy\ontology-venv\Scripts\python.exe ontology\export_separation_matrix.py
```

## 四、Windows 上要注意的三个坑

1. **java 不在 PATH**：`check_separation_of_duty.py` 需要 java 跑 HermiT。若没装 JDK，设置环境变量：
   ```
   setx PROTEGE_JRE "C:\Program Files\Protege-5.6.9\jre\bin"
   ```
   或者更省事——直接在 Protégé 界面里 Reasoner → HermiT → Start reasoner，不走命令行。

2. **命令行跑 HermiT 的 classpath**：Mac 那套是按 Protégé 目录手工拼的（分隔符 `:`），Windows 要改成分号 `;`。**建议直接用 Protégé 界面推理**，避免折腾。

3. **中文乱码**：MCP 配置里已设 `PYTHONIOENCODING=utf-8`，本体含大量中文 label，这个变量不要删。

## 五、两台机器用 git 同步

`bank_seed.py` 是**唯一真源**，两边都能改就会分叉。约定：**改之前先 pull，改完立刻 commit + push**。

```bash
# Mac 侧（首次）
cd /Users/zhongyuanpan/WorkBuddy/2026-09-26-19-39-53
git init
git add ontology dist .gitignore
git commit -m "银行业务本体：225 类初始版本"
git remote add origin <你的远端地址>
git push -u origin master

# Windows 侧（首次）
git clone <你的远端地址> D:\ontology-kit
# 然后进 D:\ontology-kit 双击 install.bat

# 日常同步
git pull && 改模型 && git commit -am "说明改了什么" && git push
```

`.gitignore` 已排除 `.venv/`、`__pycache__/` 等，只同步真源与产物。

> **警告：绝对不要在 `C:\Users\<用户名>` 或 `~` 家目录直接 `git init`。**
> Mac 上就吃过这个亏——家目录出现 .git 后，Protégé 的 Git 集成会在界面线程递归扫描整个用户目录，
> 加载本体卡了 8.7 分钟。仓库根目录必须是项目目录。

## 六、包内结构

```
windows-ontology-kit/
├── install.bat              双击安装
├── setup.py                 安装脚本（标准库，无依赖）
├── README-Windows.md        本文件
├── .gitignore
├── ontology-mcp/            → 安装到 %USERPROFILE%\.workbuddy\ontology-mcp
│   ├── bank_seed.py         真源：225 类 / 81 对象属性 / 246 数据属性 / 160 个体
│   ├── ontology_core.py     读写 .owl 的核心封装
│   └── server.py            MCP server（stdio JSON-RPC，提供 16 个工具）
└── ontology/                工作区
    ├── bank-enterprise.owl  本体产物（368 KB）
    ├── build_bank_ontology.py
    ├── check_separation_of_duty.py
    ├── check_reporting_integrity.py
    ├── check_mapping_coverage.py
    ├── export_separation_matrix.py
    ├── regulatory_mapping_scaffold.json
    └── separation_matrix.json / .csv
```

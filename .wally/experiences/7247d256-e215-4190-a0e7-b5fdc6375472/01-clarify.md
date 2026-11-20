# 01 · Clarify（需求澄清）

> **阶段任务**：核对现有 Web 框架、路由位置与测试约定，明确接口约定、改动范围与验收条件。仅产出澄清文档，不改动源码、不运行改动、不提交。
> **任务目标（用户授权）**：在当前仓库「现有 Web 服务」中增加原生 `GET /welcome` HTTP 路由，返回 JSON `message=welcome`。
> **分支/工作区**：`feature/wally-experience-7247d256`（平台创建，仓库独立副本，Git 提交由平台收尾）。
> **前序产物**：`.wally/experiences/7247d256-e215-4190-a0e7-b5fdc6375472/` 在本阶段开始时为空目录；01 为首个阶段，无前序阶段文档或测试结果可引用，故本阶段结论全部来自本次实地核对。

---

## 一、结论（先行）

1. **仓库身份**：当前仓库是 `octop-harness` —— 基于 LangChain Deep Agents 的 Python **库**（`pyproject.toml:6`、`pyproject.toml:8` 版本 `1.0.11`），不是 Web 服务。`AGENTS.md:52` 明确："It is a library, not an application... HTTP server ... does not belong here"。
2. **任务前提与仓库现状不符（本阶段最重要的发现）**：仓库内 **不存在 `app.py`、不存在 HTTP Web 框架的源码使用、不存在路由定义、不存在 HTTP server 启动入口**。`AGENTS.md:191`、`AGENTS.md:311` 进一步把 "HTTP server" 列入 "Must not add / Do not add" 的应用层功能。任务描述的「现有 Web 服务」「优先阅读 app.py」「路由位置」在本仓库中均无对应物，不能假定其存在。
3. **功能验收条件本身明确且可判定**：`GET /welcome` → HTTP 200 + JSON `{"message": "welcome"}`（`Content-Type: application/json`）。仓库侧质量门禁与测试约定也明确（`make all` 必须绿，见 §五）。
4. **澄清结论**：功能目标清晰，但「在现有服务上扩展路由」缺少承接对象；因此需要在**后续实现阶段之前**先裁决「路由落点 / 原生承载技术 / 与库约束的取舍」。按 `AGENTS.md` §1「多种解释列出让用户选择、不静默选一个」，这里只列候选（§六），不在澄清阶段擅自选定。
5. **阶段边界**：本阶段仅写入本文件，未修改任何源码、未运行开发测试、未提交。

---

## 二、执行证据（本阶段实际执行的核对动作与结果）

| # | 核对动作 | 关键结果 |
|---|----------|----------|
| 1 | `git status` / `git branch --show-current` | 分支 `feature/wally-experience-7247d256`，工作树干净 |
| 2 | `ls -la` + `find`/`git ls-files` 全仓查找 `app.py` | 根目录无 `app.py`；`git ls-files` 中仅 `src/octop_harness/acp/server.py`、`tests/test_acp_server.py` 及若干 skill 模板含 "server" 字样，**无** `app.py` / `routes.py` / `wsgi.py` / `asgi.py` |
| 3 | 全仓 grep `Flask\|FastAPI\|aiohttp\|starlette\|uvicorn\|@app.get\|add_route\|HTTPServer\|BaseHTTPRequestHandler\|asgi\|wsgi` | 框架名命中**仅**在 `uv.lock`（`aiohttp`/`starlette`/`uvicorn` 是 `mcp`/`langfuse` 等的间接依赖）；`src/**/*.py` 无任何框架导入、路由装饰器或 server 启动代码 |
| 4 | grep `welcome\|/welcome` | 命中全部在 CLI REPL 欢迎横幅（`src/octop_harness/cli/repl/loop.py:73-76`、`tests/cli/test_repl/test_loop.py`），与 HTTP 路由无关 |
| 5 | 读启动入口 | `pyproject.toml:99-100` 控制台脚本 `octop-harness = octop_harness.cli.main:cli` 是 Click CLI（`src/octop_harness/cli/main.py`），非 Web server；`src/octop_harness/acp/server.py:1` 为 "Expose HarnessAgent as an ACP agent over stdio"（stdio 进程内协议，非 HTTP） |
| 6 | 读 `README.md`（web/server/http/port/endpoint/app.py 关键词） | 仅涉及 LLM provider endpoint、MCP 传输、web-search 等，无本地 Web 服务 / 监听端口 / 路由表说明 |
| 7 | 读测试配置 | `pyproject.toml:261-286`（pytest）、`tests/conftest.py`、`Makefile:106`（`all`）、`Makefile:127`（`test`） |
| 8 | 运行环境探针 | `python3` 为 3.11.6（低于 `pyproject.toml:12` 要求的 `>=3.12`）；`uv` 不存在；无 `.venv`；`import octop_harness` 与 `pytest` 均因缺少 `deepagents` 等依赖失败（`ModuleNotFoundError: No module named 'deepagents'`，来自 `tests/conftest.py:11`） |

> 环境探针仅为当前快照的事实记录；运行环境由平台管理，后续阶段的依赖/解释器以平台配置为准。

---

## 三、关键文件清单

| 文件（含行号） | 角色 / 本阶段结论 |
|----------------|-------------------|
| `pyproject.toml:6,8,12` | 项目身份：`octop-harness` v1.0.11，`requires-python >=3.12`；是库不是服务 |
| `pyproject.toml:99-100` | 唯一启动入口 `[project.scripts]`：`octop_harness.cli.main:cli`（CLI，非 HTTP server） |
| `pyproject.toml:261-286` | `[tool.pytest.ini_options]`：`testpaths=["tests"]`、`pythonpath=["."]`、`asyncio_mode="auto"`、`--strict-markers`、`--strict-config`、`filterwarnings=["error", ...]` |
| `pyproject.toml:288-298` | `[tool.coverage]`：`source=["src/octop_harness"]`、`branch=true` |
| `Makefile:106` / `Makefile:127` | `all: format lint typecheck test`（ship bar）/ `test: pytest --cov=octop_harness --cov-report=term-missing` |
| `Makefile:23` | `RUN := $(if $(UV),uv run,)` —— 无 `uv` 时直接调用 `ruff`/`mypy`/`pytest` |
| `AGENTS.md:52,191,311` | 明确「库不放 HTTP server」「Must not add / Do not add: HTTP server」——与任务诉求直接冲突 |
| `AGENTS.md:36,347` | 新增公共 API 须进 `__all__`、有 docstring、有测试、README 提及 |
| `AGENTS.md:109,298` | 测试文件与 `src/` 模块一一对应（`src/octop_harness/x.py` ↔ `tests/test_x.py`） |
| `AGENTS.md:156,162,385` | `make all` / `make test` 为验证命令；`make all` 未绿不得称完成 |
| `src/octop_harness/cli/main.py` | Click CLI 入口（`cli` group），确认无 Web 启动逻辑 |
| `src/octop_harness/acp/server.py:1` | "ACP agent over stdio"，确认不是 HTTP 服务 |
| `src/octop_harness/__init__.py:61` | `__all__` + `_LAZY_EXPORTS`：新增公共符号的导出约定所在处 |
| `src/octop_harness/cli/repl/loop.py:73-76` | 唯一 "welcome" 相关代码，是终端欢迎横幅，非路由 |
| `tests/conftest.py` | autouse fixtures（隔离 HOME 日志、关闭 HarnessAgent/Manager/Memory），新增测试需兼容 |
| `README.md` | 无本地 Web 服务/端口/路由文档 |

---

## 四、框架、启动入口、路由位置与接口约定核对

- **框架**：无原生 Web 框架。核心依赖（`pyproject.toml` `dependencies`）为 `deepagents`/`langchain`/`langgraph`/`httpx`/`mcp` 等，均为 agent 运行时与 HTTP **客户端**；`aiohttp`/`starlette`/`uvicorn` 仅出现在 `uv.lock` 作为间接依赖，源码未导入。结论：仓库当前**没有**可用于「增加原生路由」的既有框架与路由表。
- **启动入口**：`octop-harness` 控制台脚本指向 `cli.main:cli`（`pyproject.toml:100`）；`acp/server.py` 走 stdio。二者都不是监听 HTTP 端口的 Web 服务，没有「在现有服务启动时注册路由」的挂载点。
- **路由位置**：不存在。`git ls-files` 无 `app.py`/`routes.py`/`wsgi.py`/`asgi.py`，`src/` 全量 grep 无路由装饰器或 `add_route`/`add_url_rule`。「路由位置」这一待核对项在现状下为空，需由后续阶段新建（见 §七）。
- **接口约定（据任务）**：方法 `GET`，路径 `/welcome`，成功响应 `200`，体为 JSON 且含字段 `message`，值为 `welcome`。建议以 `{"message": "welcome"}` 为精确断言对象，响应头 `Content-Type: application/json`。仓库内没有既有 JSON 接口风格可沿用（既有 `protocols/openai.py`、`providers/api.py` 是消息格式适配与 preset 序列化，不是 HTTP 接口）。

---

## 五、测试约定与验收条件

**测试约定（来自仓库，需在实现/验证阶段遵守）**
- 测试框架 pytest；配置见 `pyproject.toml:261-286`；测试目录 `tests/`，与模块一一对应（`AGENTS.md:298`）。
- 单测调试：`pytest tests/<file>.py::... -xvs`；目标验证：`pytest`（先针对性用例，再全量）。
- 质量门禁：`make all` = `format`+`lint`+`typecheck`+`test` 必须全绿（`AGENTS.md:156,385`）；`make test` 带 `--cov`。
- 行为变更/新增能力按 `AGENTS.md:36-38`「先写（失败的）测试 → 再实现」；新增公共 API 还需 `__all__` 导出、docstring、README 提及（`AGENTS.md:347`）。
- 全仓 `filterwarnings=["error", ...]`（`pyproject.toml:271`），测试不得引入新告警；`tests/conftest.py` 的 autouse fixtures 对导入 `octop_harness` 的测试生效。
- HTTP 客户端在现有测试中通过 `patch.object(..., httpx, "Client", FakeClient)` 等 mock 方式使用（如 `tests/test_ssrf_web_fetch.py:51,88,120`），用于**出站**请求 mock；仓库目前没有针对本地 server 的 `TestClient`/`ASGITransport` 用例，新路由测试需自行确定客户端方式。

**验收条件（功能，明确且可判定）**
1. `GET /welcome` 返回 HTTP 200；
2. 响应为 JSON，且 `message == "welcome"`（精确体建议 `{"message": "welcome"}`）；
3. `Content-Type` 为 `application/json`；
4. 有对应自动化测试覆盖该路由（按 §五 测试约定）；
5. 不破坏既有行为，质量门禁 `make all` 通过（`AGENTS.md:156,385`）。

> 运行环境提示：当前快照中 `uv`/`.venv`/`deepagents` 缺失且 Python 为 3.11（要求 >=3.12），直接 `import octop_harness` 或 `pytest` 会失败；验证阶段应依赖平台提供的环境或先完成依赖安装，否则 `make all` 无法执行。

---

## 六、待确认 / 风险（澄清结论：列出候选，不静默选择）

按 `AGENTS.md` §1「列出多种解释让用户选择」，以下事实需由后续阶段或平台裁决，本阶段不替其决定：

1. **「现有 Web 服务」与仓库不符**：是任务描述沿用了通用模板、实际应在 octop-harness 内**新建**一个最小 HTTP 服务；还是目标服务应在宿主（如 `octop-gateway`/`Octop`）而不在本库？两者落点完全不同。
2. **「原生」的承载技术**：候选 —— (a) Python 标准库 `http.server`（零新增运行依赖，契合「零依赖优先」与「原生」字义）；(b) 引入 Web 框架（`pyproject.toml` 新增运行依赖需先说明理由，且同样受 §七约束）。仓库无既有框架可「原生」沿用。
3. **与库约束的取舍**：`AGENTS.md:52,191,311` 禁止在库中加入 HTTP server；任务已声明「用户授权」。需明确该授权是否覆盖此约定，并在 MR/CHANGELOG 中显式记录这一取舍，避免后续被 `make all`/评审判定为越界。
4. **是否为公共 API**：若新路由作为可导入模块发布，需按 `AGENTS.md:347` 走 `__all__`/docstring/README；若仅是可运行脚本/示例，则改动范围更小。

---

## 七、改动范围（供后续阶段参考，本阶段不执行）

- **新增**：承载 `/welcome` 的最小 HTTP 服务模块与其启动入口（现状无 `app.py`，需新建；具体文件名由 §六 裁决决定）。
- **新增**：对应测试文件，建议 `tests/test_welcome.py`（或按 `AGENTS.md:298` 与新模块命名一一对应），断言 §五.1–3。
- **可能涉及**：`src/octop_harness/__init__.py:61` 的 `__all__`（仅当作为公共 API 导出时）、`README.md`（`AGENTS.md:347`）、`CHANGELOG.md` 的 `## [Unreleased]`（`AGENTS.md` §12.7）。
- **验证命令**：针对性 `pytest tests/test_welcome.py -q` → 全量 `make all`（或 `make test`）；结果需写回后续阶段文档。

---

## 八、验收结论

**Clarify 阶段已完成**：框架（无）、启动入口（CLI/stdio）、路由位置（无）、测试约定、接口约定与验收条件均已实地核对，证据见 §二、关键文件见 §三。

- 功能验收条件（§五）明确且可判定，可据此在后续阶段编写失败用例并驱动实现。
- 但本仓库**不是 Web 服务、也没有 `app.py` 或既有路由**，且 `AGENTS.md:52,191,311` 明确禁止在库中加入 HTTP server —— 「在现有服务上增加原生路由」的前提不成立。此为**实现阶段的前置依赖**，须先按 §六 裁决落点与技术选型，再进入编码。
- 本阶段未遇到工具/读取层面的阻塞，澄清工作本身不受影响，故不触发「停止并记失败」；上述前提冲突作为澄清结论如实上报，交由平台在自动推进时处理。
- 本阶段严格限于澄清：仅写入本文件，未改动任何源码、未运行开发测试、未执行任何 Git 提交（提交由平台收尾）。

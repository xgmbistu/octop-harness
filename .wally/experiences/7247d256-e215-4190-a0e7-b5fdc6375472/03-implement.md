# 03 · Implement + UT + Docs（实现 + 单测 + 文档）

> **阶段任务**：依据 02-plan 方案，在当前仓库落地原生 `GET /welcome` HTTP 路由（返回 JSON `message=welcome`），更新 README 接口说明，编写并**实际运行**契约测试，产出 `runtime.json`，写入本阶段文档。**仅执行当前阶段**；Git 提交由平台收尾，部署/IT/Review 属后续阶段。
> **任务目标（用户授权）**：在现有服务内增加原生 `GET /welcome`，正文 JSON 至少 `message=welcome`；接口集成当前框架的原生路由；更新 README 接口说明；编写并实际运行契约测试；提供 `{"test": [...], "serve": [...]}` 且 serve 经 `{port}` 接收临时端口的 `runtime.json`。
> **分支/工作区**：`feature/wally-experience-7247d256`（平台创建、仓库独立副本）。
> **前序产物**：`00-overview.md`、`01-clarify.md`、`02-plan.md`。02 §二 已对 01 §六 四项待裁决定案，前置依赖解除，方案可直接执行。

---

## 一、结论（先行）

1. **已落地原生 `GET /welcome` 路由**：新建顶层 `app.py`（`http.server` 标准库，`WelcomeHandler.do_GET` 原生分派），`GET /welcome → 200 / application/json / {"message": "welcome"}`，其它路径 `404`；零新增运行依赖。
2. **契约测试已真实运行并通过**：`tests/test_welcome.py` 用真实 loopback HTTP，最终命令 **4 passed**；并保留了「实现前先红（`ModuleNotFoundError: No module named 'app'`）→ 实现后转绿」的证据。
3. **与本次改动相关的门禁全绿**：`ruff check` / `ruff format --check` / `mypy app.py`（strict）通过，`make lint` 全仓 378 文件通过，`serve` 路径冒烟通过。
4. **文档与运行时产物齐备**：README 新增接口说明章节、CHANGELOG `## [Unreleased]` 记录「用户授权覆盖库内 HTTP server 约束」取舍、`runtime.json` 提供 `test`/`serve` 命令。
5. **仓库级 `make all` 无法在本快照整体跑通**：受平台环境限制（Python 3.11.6 < 项目要求 3.12、`tests/conftest.py:11` 依赖缺失的 `deepagents`），其 `typecheck`/`test` 必失败且失败点与本次改动无关；已用非破坏性等价门禁替代并如实记录，留待平台完整 dev 环境复核（§五、§八）。**这不是实现阻塞**，不触发「停止并记失败」。

---

## 二、真实分析（沿用并执行 02 裁决）

- **仓库身份与前提**：本仓库是 `octop-harness` **库**（`pyproject.toml:6,8,12`，Python ≥3.12），01/02 已实地核对：全仓无 `app.py`、无 Web 框架源码使用、无路由定义、无 HTTP server 启动入口；唯一控制台脚本 `octop-harness = octop_harness.cli.main:cli`（`pyproject.toml:99-100`）是 Click CLI，`acp/server.py` 走 stdio。故「在现有 Web 服务 / 当前框架上扩展路由」无承接对象。
- **「原生 / 集成当前框架」的落地**：按 02 §二 裁决 —— 仓库无框架可挂载，因此**新建**顶层独立脚本 `app.py`，以 Python 标准库 `http.server.BaseHTTPRequestHandler.do_GET` 作为**原生路由**（语言/标准库层面的请求路径分派，`app.py:21-29`），不引入任何第三方框架，契合 `AGENTS.md` §7「零依赖优先」与任务「原生」字义。"集成当前框架"在"无框架可集成"前提下按 02 既定裁决最小落地。
- **与库约束的取舍**：`AGENTS.md:52,191,311` 禁止库内 HTTP server。`app.py` 置于发布包 `src/octop_harness` **之外**（hatch wheel 仅打包 `src/octop_harness`，`pyproject.toml:134-146`），库本身不含 HTTP server；残留的「仓库内出现 HTTP server」由**用户授权覆盖**，已在 `CHANGELOG.md` `## [Unreleased]` 显式记录（02 §二.3、`AGENTS.md` §12.7）。
- **非公共 API**：`app.py` 是可运行脚本，不进 `src/octop_harness/__init__.py` 的 `__all__`（02 §二.4），不改 `pyproject.toml` 依赖/脚本。
- **运行环境实测（本阶段重新核对）**：`python3 3.11.6`（唯一解释器，无 3.12）；`uv`、`.venv` 不存在；已装 `ruff 0.15.9` / `mypy 1.20.0` / `pytest 8.2.2` / `pytest-asyncio 0.23.7` / `pytest-cov 5.0.0` / `langchain*`，但**缺 `deepagents`**。`tests/conftest.py:11` 顶层 `from octop_harness.agent import HarnessAgent` 使标准 `pytest` 在 collection 阶段即 `ModuleNotFoundError: No module named 'deepagents'`（与 01 §二.8 一致，环境由平台托管）。

---

## 三、涉及文件

| 文件 | 动作 | 要点 |
|------|------|------|
| `app.py`（仓库根） | 新建 | 标准库 `ThreadingHTTPServer` + `WelcomeHandler`；`do_GET` 原生路由 `/welcome`；`create_server(port=0)` 供测试临时端口（`app.py:36-38`）；`main(argv)` 支持 `python3 app.py {port}` 及 `WELCOME_HOST`/`WELCOME_PORT`/默认 8000（`app.py:41-56`）。发布包之外、零新增依赖 |
| `tests/test_welcome.py` | 新建 | 接口契约测试：pytest fixture 起临时端口服务 + daemon 线程，`http.client` 真实 loopback GET；4 个断言（200 / 精确 JSON / Content-Type / 其它路径 404）；显式 `conn.close()`、`shutdown()`、`server_close()` 避免资源告警 |
| `README.md` | 修改 | 新增 `## HTTP endpoint: GET /welcome` 章节（启动命令、响应表、curl 示例）及 Documentation 目录链接 |
| `CHANGELOG.md` | 修改 | `## [Unreleased]` 增「新增」一条，记录路由/测试与授权覆盖库约束的取舍 |
| `runtime.json`（阶段目录） | 新建 | `test` / `serve` 命令，`serve` 经 `{port}` 接收临时端口（§六） |
| `03-implement.md`（阶段目录） | 新建 | 本文件 |
| `src/octop_harness/**`、`pyproject.toml`、`__init__.py` | **不动** | 非公共 API、无新依赖、启动脚本不变（02 §二.4、§五.4） |

---

## 四、实现与测试要点

- **路由（原生）**：`app.py:21-29` 仅实现 `do_GET`；命中 `/welcome` 返回 `_WELCOME_BODY = json.dumps({"message": "welcome"})`（`app.py:15`）并带 `Content-Type: application/json` 与 `Content-Length`；其余路径 `send_error(404)`，证明是「路由」而非 catch-all。其它 HTTP 方法由基类返回 `501`。`log_message` 覆写仅用于降噪（`app.py:31-33`）。
- **serve 端口**：`main()` 把首个位置参数作为端口（`app.py:47-50`），因此 `python3 app.py {port}` 可由平台注入临时端口；无参数时依次用 `WELCOME_PORT` 环境变量、默认 `8000`；`WELCOME_HOST` 覆盖绑定地址（默认 `127.0.0.1`）。`try/finally: server_close()` 保证干净退出，服务无状态。
- **契约测试**：不新增任何测试依赖，纯标准库；`tests/test_welcome.py:14-26` 每个用例独占一个 OS 临时端口（`create_server(..., 0)`），`tests/test_welcome.py:29-38` 用 `http.client.HTTPConnection` 发真实 loopback GET 并返回 `(status, content_type, body)`。测试文件位于 `tests/`、用 pytest，可被完整环境下的 `pytest` / `make all` 正常收集（它不依赖 conftest 任何 fixture、也不 `import octop_harness`）。
- **测试命令的环境适配（重要）**：本快照下 `pyproject.toml` 的 `asyncio_mode=auto` 在 `--noconftest` 时变成致命的 `Unknown config option`（被 `--strict-config`/`filterwarnings=error` 升级），且 conftest 必失败。故最终 `test` 命令用 `-c /dev/null`（不读该 ini）+ `--rootdir=.` + `-o pythonpath=.`（让 `import app` 生效）+ `--noconftest`（绕开缺 `deepagents` 的 conftest）。该组合实测 `4 passed`（§五.3）。测试文件本身仍保持标准 pytest 风格，未为环境适配而扭曲代码。

---

## 五、执行证据（真实命令与结果）

> 全部命令在仓库根 `feature/wally-experience-7247d256` 执行；以下为真实输出摘录。

**1）先红（实现 `app.py` 之前，先落测试文件）**
```
$ python3 -m pytest --noconftest tests/test_welcome.py -q
E   ModuleNotFoundError: No module named 'app'      # tests/test_welcome.py:11 collection
1 error in 0.03s   (EXIT=4)
```
红色原因明确：被测对象 `app` 尚不存在。该命令同时暴露 `ERROR: Unknown config option: asyncio_mode`（§四），据此把最终命令调整为 `-c /dev/null` 组合（见 3）。

**2）实现后门禁（本次改动文件）**
```
$ python3 -m ruff check app.py tests/test_welcome.py            → All checks passed!            (EXIT=0)
$ python3 -m ruff format --check app.py tests/test_welcome.py  → 2 files already formatted     (EXIT=0)
$ python3 -m mypy app.py                                        → Success: no issues found in 1 source file (EXIT=0)
```
（期间按 ruff 反馈做两处修正：`app.py` 去掉多余的 `# noqa: N802`（RUF100）、`tests/test_welcome.py` 整理 import 排序（I001）；修正后复核如上全绿。）

**3）契约测试转绿（最终命令，即 `runtime.json` 的 `test`）**
```
$ python3 -m pytest -c /dev/null --rootdir=. -o pythonpath=. --noconftest tests/test_welcome.py -q
....                                                                     [100%]
4 passed in 2.04s   (EXIT=0)
```
`-v` 明细：`test_welcome_returns_200` / `test_welcome_returns_expected_json` / `test_welcome_content_type_is_json` / `test_other_path_returns_404` 全部 PASSED。

**4）serve 路径冒烟（`runtime.json` 的 `serve` 等价执行）**
```
$ python3 - <<'PY'   # 取临时端口 → 启动 `python3 app.py <port>` → 真实 loopback GET → terminate
GET /welcome -> 200 | application/json | {"message": "welcome"}
GET /other   -> 404
serve command: ['/usr/bin/python3', 'app.py', '15429']   (EXIT=0)
```

**5）只读全仓门禁**
```
$ make lint       → ruff check src tests: All checks passed!; ruff format --check src tests: 378 files already formatted (EXIT=0)
```
说明新增 `tests/test_welcome.py` 已被全仓 lint 覆盖且未破坏基线；根 `app.py` 不在 `make lint` 范围，已由 2）单独覆盖（02 §五.4 判断一致）。

**6）`make typecheck` / `make test`（本快照环境限制，与本次改动无关）**
```
$ make typecheck  → mypy src
src/octop_harness/backends/cloud_storage_base.py:524: error: Expected '('  [syntax]   (EXIT=2)
$ make test       → pytest --cov=octop_harness ...
tests/conftest.py:11: ModuleNotFoundError: No module named 'deepagents'            (EXIT=2)
```
- `cloud_storage_base.py:524` 是既有 `async def _to_thread[T](...)`（PEP 695 泛型语法，Python 3.12+），本机 3.11 无法解析；属**既有文件** + 解释器低于项目要求所致，非本次改动。
- `make test` 失败即 `tests/conftest.py:11` 顶层 import 缺 `deepagents`，与 01 §二.8 一致。

**关于 `make all`**：未直接运行。其首个目标 `make format` 会 `ruff check --fix` / `ruff format` **重写 `src tests` 全部文件**（非只读、超出本阶段 surgical 边界），且随后的 `typecheck`/`test` 在上述环境必失败（两者失败均与本次改动无关）。因此以非破坏性等价门禁替代：`make lint`（绿）+ `ruff check/format --check app.py tests/test_welcome.py`（绿）+ `mypy app.py`（绿）+ 契约测试（4 passed）。按 `AGENTS.md:156,385` 的 ship bar 要求，此处如实说明**仓库级 `make all` 因平台快照环境无法整体判定**，留待平台完整 dev 环境（Python ≥3.12 + 安装 `deepagents`）复核，不虚报全绿。

---

## 六、runtime.json

路径：`.wally/experiences/7247d256-e215-4190-a0e7-b5fdc6375472/runtime.json`

```json
{
  "test": ["python3", "-m", "pytest", "-c", "/dev/null", "--rootdir=.", "-o", "pythonpath=.", "--noconftest", "tests/test_welcome.py", "-q"],
  "serve": ["python3", "app.py", "{port}"]
}
```

- 数组为 `[命令, 参数...]` 形式（可直接 `subprocess.run(argv)`）；运行 cwd 为仓库根。
- `test`：运行 `tests/test_welcome.py` 契约测试；`-c /dev/null` / `--noconftest` / `-o pythonpath=.` 为本快照环境适配（§四），保证零依赖真实跑通。
- `serve`：`python3 app.py {port}`，`{port}` 由平台替换为临时端口；`app.py:47-50` 把首个位置参数作为监听端口。默认绑定 `127.0.0.1`，如需跨接口可用 `WELCOME_HOST` 覆盖。服务无状态，进程结束即停服。

---

## 七、验收结论（对齐 02 §六 / 01 §五）

| # | 验收条件 | 结果 | 证据 |
|---|----------|------|------|
| 1 | `GET /welcome` → `200` | ✅ | §五.3 用例、§五.4 冒烟 `200` |
| 2 | JSON 精确 `{"message": "welcome"}` | ✅ | `tests/test_welcome.py:46-48`；冒烟体一致 |
| 3 | `Content-Type: application/json` | ✅ | `tests/test_welcome.py:51-53`；冒烟头一致 |
| 4 | 契约测试覆盖、先红后绿 | ✅ | §五.1 红（`No module named 'app'`）→ §五.3 绿（`4 passed`） |
| 5 | 不破坏既有行为 / 质量门禁 | ⚠️ 部分受限 | 改动相关门禁（`ruff`/`format`/`mypy`/契约测试/`make lint`）全绿；仓库级 `make all` 受平台环境限制无法整体执行，失败点为既有 PEP695 语法 + conftest 缺 `deepagents`，与本次改动无关（§五.6） |
| 6 | CHANGELOG 记录取舍 | ✅ | `CHANGELOG.md ## [Unreleased]` 已记「用户授权覆盖库内 HTTP server 约束」 |
| 7 | 启动/回滚可执行、服务无状态 | ✅ | `python3 app.py {port}` 冒烟通过；改动仅新增 2 文件 + 2 处文档编辑，回滚=删两新文件/回退两处编辑，无状态无迁移 |
| 附加 | README 接口说明 | ✅ | `README.md ## HTTP endpoint: GET /welcome`（本阶段用户明确要求；覆盖 02 §二.4「不动 README」中关于**公共 API 说明**的部分，仅新增独立 HTTP 接口章节，不改库公共 API 段） |
| 附加 | runtime.json | ✅ | §六 |

---

## 八、阶段边界、未验证项与阻塞判定

- **阶段边界**：仅执行 03「实现 + UT + Docs」。**未**执行 Git 提交（平台收尾）、**未**部署（04）、**未**IT（05）、**未**Review（06）；未改动 `src/octop_harness/**`、`pyproject.toml`、发布包导出。
- **未验证项（交后续阶段/平台）**：
  1. 仓库级 `make all` 全绿 —— 需平台完整 dev 环境（Python ≥3.12、`deepagents` 等依赖齐备）复核；本快照无法判定。
  2. 完整环境下的 `pytest tests/test_welcome.py` / `make test` 对全量用例的回归 —— 同上；本契约测试自身不依赖 `octop_harness`，逻辑上不受影响。
- **阻塞判定**：**无阻塞**。功能目标已实现、契约测试已真实运行通过、文档与 `runtime.json` 齐备；`make all` 的不可跑通是 01/02 已识别并记录的**平台快照环境限制**，非工具/读取层面阻塞，故不触发「停止并记失败」，由平台按既定流程自动推进。

---

## 九、一句话总结

按 02-plan 裁决，在发布包之外新建标准库 `app.py` 落地原生 `GET /welcome`，配有真实 loopback 契约测试（先红后绿，最终 `4 passed`）、README 接口说明、CHANGELOG 取舍记录与 `runtime.json`；改动相关门禁全绿，仓库级 `make all` 受平台 3.11/缺 `deepagents` 环境限制留待完整环境复核。

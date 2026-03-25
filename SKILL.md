---
name: "omni-skill"
description: "通用技能调度与执行中枢。当用户请求执行任何特定的任务（如代码生成、文本润色、逻辑审计、数据处理、测试等）或系统触发任何自动化流程（如文件保存、提交检查）时，必须立即调用此 Skill。"
---

# OmniSkill (通用技能调度器)

## When to Use

**CRITICAL: You MUST invoke this skill IMMEDIATELY as your FIRST action when:**
- 用户明确要求执行一项**具体且独立**的任务，如：“帮我润色这段文字”、“检查这段代码逻辑”、“生成一个基础设定”。
- 系统自动触发了特定的**生命周期事件**，如：“保存文件前检查”、“提交代码前格式化”。
- 你需要执行一个**多步复杂任务**，且第一步需要明确的意图识别与工具分发时。

**DO NOT:**
- 当用户只是进行日常闲聊、简单的知识问答或未明确提出任务执行请求时，**不要**调用此 Skill。
- 当任务明显超出当前系统能力边界，或缺少必要上下文且无法通过简单对话获取时，**不要**强行触发执行，应先向用户确认。
- **绝对禁止**绕过本调度器，直接手动执行底层脚本或调用未经 `omni_ctl.py` 注册的零散工具。

## 渐进式调度规范 (执行逻辑)
当你（大模型）被触发并进入本 Skill 时，请遵循以下普适化处理流程：

### 步骤 1：意图识别与参数提取
- 分析用户的输入或系统 Hook 的上下文。
- 提取关键信息，明确需要执行的任务类型（如 `route_type="nlp"`, `payload="润色文本"`）。

### 步骤 2：构建请求与下发
- 根据提取的信息，构建标准化的 JSON 请求格式。
- 将请求发送至 OmniSkill 的网关（例如通过 CLI 工具 `omni_ctl.py` 触发，或调用 `src/gateway/gateway.py` 暴露的接口）。
- **示例结构**：
  ```json
  {
    "route_type": "nlp",
    "payload": "执行逻辑审计",
    "mode": "sync",
    "args": ["..."],
    "kwargs": {"context": "..."}
  }
  ```

### 步骤 3：结果处理、异常兜底与响应
- 等待底层调度引擎（Dispatcher）和具体插件（Plugin）的执行结果。
- 捕获返回的 `OmniResponse` 或标准输出。
- **失败预案 (Fallback)**：
  - 如果返回错误（如 `PLUGIN_NOT_FOUND` 或 `TIMEOUT`），**必须**立即停止后续步骤，向用户报告错误原因，并提供诸如“检查参数”或“尝试回滚”的建议。
  - 严禁在底层执行失败的情况下，向用户捏造或臆测成功的结果。
- 将执行成功的结果解析为人类可读的语言（遵循纯中文输出原则），并返回给用户。

## 扩展与管理机制 (如何接入新技能)
OmniSkill 具备极强的普适性和扩展性。如果用户希望添加新的技能或接入外部现成的工具包：

1. **统一打包**：使用内置的打包器将外部目录转化为标准核心包。
   ```bash
   python .trae/skills/omni-skill/src/cli/omni_packager.py --source <原始路径> --target <目标包路径>
   ```
2. **注册与挂载**：将生成的包注册到调度中枢。
   ```bash
   python .trae/skills/omni-skill/src/cli/omni_ctl.py register --name <技能名称> --runtime-type <运行环境>
   ```
3. **即时生效**：注册完成后，无需重启系统。下次调度时，底层引擎将通过 LRU 懒加载机制自动挂载并执行该技能。若发生冲突或异常，可在 30 秒内执行 `omni_ctl.py rollback` 安全回滚。

<!-- OMNI_REGISTRY_START -->
## 当前可用子技能列表 (Available Sub-Skills)

*当前暂无已注册的子技能。*

*(此列表由 `omni_ctl` 自动维护，请勿手动修改)*
<!-- OMNI_REGISTRY_END -->

---

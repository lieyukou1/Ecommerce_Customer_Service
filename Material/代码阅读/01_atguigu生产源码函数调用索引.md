# 01_atguigu生产源码函数调用索引
- 最后修改时间：2026-06-03 04:55
- 文档定位：批次 A+B+C+D 的生产源码函数调用索引与阅读导航
- 上级入口：[PROJECT_CONTEXT.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/PROJECT_CONTEXT.md)
- 下级入口：后续批次索引待补充

## 使用说明

- 代码内函数头只写直接调用来源摘要
- 这里补完整一些的调用链阅读顺序
- 当前文档已覆盖批次 A+B+C+D：`api / service / engine / plan / state decision / track execution / domain.state / task / knowledge / focus / clarify / chitchat / action / repository / prompt / infrastructure / config / main`

## 文本消息主链

1. `api.router.chat_router.chat`
2. `service.dialogue_service.process_message`
3. `engine.dialogue_engine.hand_dialogue`
4. `engine.dialogue_engine._route_turn`
5. `engine.track_execution.text_turn_handler.handle`
6. `engine.focus.resolver.try_switch_focused_object_from_text`
7. `plan.planner.predict`
8. `plan.protocol_gate.process`
9. `engine.state_decision.engine.build_text_context`
10. `engine.track_execution.text_turn_handler._execute_context`
11. 分流到：
   - `engine.state_decision.engine.execute_runtime_directive`
   - `engine.track_execution.task_command_executor.execute`
   - `knowledge.handler.handle`
   - `chitchat.handler.handle`

## 对象消息主链

1. `api.router.chat_router.chat`
2. `service.dialogue_service.process_message`
3. `engine.dialogue_engine.hand_dialogue`
4. `engine.dialogue_engine._route_turn`
5. `engine.track_execution.object_turn_handler.handle`
6. `engine.track_execution.object_turn_handler._build_object_context`
7. `engine.focus.resolver.resolve_object_commands`
8. 分流到：
   - `engine.track_execution.object_turn_handler._handle_object_switch_during_active_task`
   - `engine.track_execution.object_turn_handler._handoff_object_slots`
   - `engine.track_execution.object_turn_handler._continue_active_task_with_object`
   - `engine.track_execution.object_turn_handler._respond_object_requires_intent`

## Task 执行主链

1. `engine.track_execution.task_command_executor.execute`
2. `engine.state_decision.engine.begin_task_execution`
3. `task.handler.handle`
4. `engine.state_decision.engine.finalize_task_execution`
5. `engine.state_decision.state_machine.finalize_task_transition`
6. `domain.state.DialogueState.record_task_outcome / transition_to`

## API

| 函数 | 文件 | 作用 | 直接调用方 | 典型下游 | 入口 |
| --- | --- | --- | --- | --- | --- |
| `chat` | `api/router/chat_router.py` | 对话接口入口 | FastAPI 路由 | `DialogueService.process_message` | 是 |
| `chat_history` | `api/router/chat_router.py` | 历史查询入口 | FastAPI 路由 | `DialogueService.load_history` | 是 |
| `chat_state` | `api/router/chat_router.py` | 状态快照查询入口 | FastAPI 路由 | `DialogueService.load_state` | 是 |
| `save_chat_state` | `api/router/chat_router.py` | 状态快照覆盖保存入口 | FastAPI 路由 | `DialogueService.save_state_snapshot` | 是 |
| `reset_chat_state` | `api/router/chat_router.py` | 状态重置入口 | FastAPI 路由 | `DialogueService.reset_state` | 是 |
| `_build_user_message` | `api/router/chat_router.py` | 请求转领域消息 | `chat` | `UserMessage` 主链输入 | 否 |
| `_build_chat_response` | `api/router/chat_router.py` | 领域结果转接口响应 | `chat` | `ChatResponse` | 否 |
| `_build_history_response` | `api/router/chat_router.py` | turn 历史展平成消息历史 | `chat_history` | `HistoryResponse` | 否 |
| `_build_state_snapshot_response` | `api/router/chat_router.py` | 状态对象转快照响应 | `chat_state/save/reset` | `DialogueStateSnapshotResponse` | 否 |
| `_build_chat_object` | `api/router/chat_router.py` | `FocusedObject` 转接口对象 | 多个 builder | `ChatObject` | 否 |

## Service

| 函数 | 文件 | 作用 | 直接调用方 | 典型下游 | 入口 |
| --- | --- | --- | --- | --- | --- |
| `process_message` | `service/dialogue_service.py` | 串起加载状态、引擎处理、保存状态 | `chat` | `DialogueEngine.hand_dialogue` | 是 |
| `load_history` | `service/dialogue_service.py` | 加载历史 turn | `chat_history` | `_select_history_turns` | 否 |
| `load_state` | `service/dialogue_service.py` | 加载完整状态 | `chat_state` | repository load | 否 |
| `reset_state` | `service/dialogue_service.py` | 重置并保存空状态 | `reset_chat_state` | repository save | 否 |
| `save_state_snapshot` | `service/dialogue_service.py` | 用快照重建状态并保存 | `save_chat_state` | `DialogueState.from_dict` | 否 |
| `_select_history_turns` | `service/dialogue_service.py` | 选择当前/最近会话历史 | `load_history` | `DialogueState.current_session` | 否 |

## Engine

| 函数 | 文件 | 作用 | 直接调用方 | 典型下游 | 入口 |
| --- | --- | --- | --- | --- | --- |
| `DialogueEngine.hand_dialogue` | `engine/dialogue_engine.py` | 处理单轮消息并提交 turn | `DialogueService.process_message` | `_prepare_session/_route_turn` | 是 |
| `DialogueEngine._route_turn` | `engine/dialogue_engine.py` | 按消息类型分流 | `hand_dialogue` | `TextTurnHandler.handle` / `ObjectTurnHandler.handle` | 否 |
| `DialogueEngine._prepare_session` | `engine/dialogue_engine.py` | 处理会话创建与超时切换 | `hand_dialogue` | `DialogueState.start_session` 等 | 否 |
| `build_track_execution_runtime` | `engine/track_execution/runtime.py` | 组装文本/对象执行入口 | `DialogueEngine.__init__` | `TextTurnHandler` / `ObjectTurnHandler` | 否 |

## Track Execution

| 函数 | 文件 | 作用 | 直接调用方 | 典型下游 | 入口 |
| --- | --- | --- | --- | --- | --- |
| `TextTurnHandler.handle` | `engine/track_execution/text_turn_handler.py` | 文本消息执行总入口 | `DialogueEngine._route_turn` | planner / protocol gate / state decision | 是 |
| `_respond_validation_failure` | `engine/track_execution/text_turn_handler.py` | 校验失败转澄清 | `handle` | `ClarifyResponder.respond` | 否 |
| `_execute_context` | `engine/track_execution/text_turn_handler.py` | 按决策分发四条轨 | `handle` | directive / task / knowledge / chitchat | 否 |
| `TaskCommandExecutor.execute` | `engine/track_execution/task_command_executor.py` | task 执行包装器 | 文本轨 / 对象轨 | `TaskHandler.handle` | 是 |
| `ObjectTurnHandler.handle` | `engine/track_execution/object_turn_handler.py` | 对象消息执行入口 | `DialogueEngine._route_turn` | `_build_object_context/_execute_object_context` | 是 |
| `_build_object_context` | `engine/track_execution/object_turn_handler.py` | 对象消息转承接上下文 | `handle` | `FocusedObjectResolver.resolve_object_commands` | 否 |
| `_execute_object_context` | `engine/track_execution/object_turn_handler.py` | 选择对象消息执行分支 | `handle` | handoff / continue / clarify | 否 |
| `_handle_object_switch_during_active_task` | `engine/track_execution/object_turn_handler.py` | 任务中的对象切换重置 | `_execute_object_context` | `DialogueState.reset_runtime_state` | 否 |
| `_handoff_object_slots` | `engine/track_execution/object_turn_handler.py` | 对象命令交给 task 执行 | `_execute_object_context` | `TaskCommandExecutor.execute` | 否 |
| `_continue_active_task_with_object` | `engine/track_execution/object_turn_handler.py` | 继续已有任务 | `_execute_object_context` | `TaskCommandExecutor.execute` | 否 |
| `_respond_object_requires_intent` | `engine/track_execution/object_turn_handler.py` | 对象缺意图时澄清 | 多处分支 | `ClarifyResponder.respond` | 否 |
| `_is_object_switch_during_active_task` | `engine/track_execution/object_turn_handler.py` | 判断对象切换 | `_execute_object_context` | 布尔分支 | 否 |

## Plan

| 函数 | 文件 | 作用 | 直接调用方 | 典型下游 | 入口 |
| --- | --- | --- | --- | --- | --- |
| `TurnPlanner.predict` | `plan/planner.py` | 调 LLM 生成 TurnPlan | `TextTurnHandler.handle` | `_build_input_prompt/_predict_from_inputs_prompt` | 是 |
| `_build_input_prompt` | `plan/planner.py` | 构造模型输入字典 | `predict` | 多个序列化 helper | 否 |
| `_predict_from_inputs_prompt` | `plan/planner.py` | 模板渲染 + LLM + JSON 解析 | `predict` | `TurnPlan.from_dict` | 否 |
| `TurnProtocolGate.process` | `plan/protocol_gate.py` | 归一化并校验 TurnPlan | `TextTurnHandler.handle` | normalizer / validator | 是 |
| `TurnPlanNormalizer.normalize` | `plan/turn_plan_normalizer.py` | 协议级兜底归一化 | `TurnProtocolGate.process` | exit fallback / service_item fallback | 是 |
| `TurnPlanValidator.validate` | `plan/turn_validator.py` | 校验 track/命令/意图合法性 | `TurnProtocolGate.process` | task / knowledge / directive 校验 | 是 |
| `TurnPlan.from_dict` | `plan/turn_plan.py` | 模型 JSON 转领域计划 | `TurnPlanner._predict_from_inputs_prompt` | 子计划 from_dict | 否 |
| `TurnPlan.active_tracks` | `plan/turn_plan.py` | 收集激活轨道 | validator / normalizer | 轨道判定 | 否 |
| `TurnPlan.active_track` | `plan/turn_plan.py` | 仅在单轨时返回轨道 | semantic classifier | 语义分类 | 否 |

## State Decision

| 函数 | 文件 | 作用 | 直接调用方 | 典型下游 | 入口 |
| --- | --- | --- | --- | --- | --- |
| `StateDecisionEngine.build_text_context` | `engine/state_decision/engine.py` | TurnPlan 转文本上下文 | `TextTurnHandler.handle` | semantic classifier / context decision | 是 |
| `StateDecisionEngine.should_execute_task_turn` | `engine/state_decision/engine.py` | 判断是否进入 task executor | `TextTurnHandler._execute_context` | 布尔分支 | 否 |
| `StateDecisionEngine.apply_clarify` | `engine/state_decision/engine.py` | 把当前轮记成 clarify | 文本校验失败 / 对象澄清 | state machine | 否 |
| `StateDecisionEngine.apply_route_decision` | `engine/state_decision/engine.py` | 普通路由落状态 | knowledge / chitchat 分支 | state machine | 否 |
| `StateDecisionEngine.begin_task_execution` | `engine/state_decision/engine.py` | task 执行前落 route | `TaskCommandExecutor.execute` | state machine | 否 |
| `StateDecisionEngine.finalize_task_execution` | `engine/state_decision/engine.py` | task 执行后落 outcome | `TaskCommandExecutor.execute` | state machine | 否 |
| `StateDecisionEngine.execute_runtime_directive` | `engine/state_decision/engine.py` | 执行 runtime 指令 | 文本 directive 分支 | `_execute_exit_runtime` | 否 |
| `DialogueStateMachine.apply_route_decision` | `engine/state_decision/state_machine.py` | 路由决策写状态 | state decision engine | `record_route/transition_to` | 是 |
| `DialogueStateMachine.finalize_task_transition` | `engine/state_decision/state_machine.py` | task outcome 写状态 | state decision engine | `record_task_outcome/transition_to` | 是 |
| `TurnSemanticClassifier.classify` | `engine/state_decision/semantic_classifier.py` | 语义分类 | `build_text_context` | `TaskFlowLocator.resolve_flow_id` | 是 |
| `TaskFlowLocator.resolve_flow_id` | `engine/state_decision/task_flow_locator.py` | 推断当前命中的 flow_id | semantic classifier | 只读/业务 flow 区分 | 是 |

## Domain State

| 函数 | 文件 | 作用 | 直接调用方 | 典型下游 | 入口 |
| --- | --- | --- | --- | --- | --- |
| `DialogueState.to_dict` | `domain/state.py` | 完整状态序列化 | repository / 快照接口 | 多个子对象 `to_dict` | 是 |
| `DialogueState.from_dict` | `domain/state.py` | 完整状态反序列化 | repository / 快照保存 | 多个子对象 `from_dict` | 是 |
| `DialogueState.transition_to` | `domain/state.py` | 高层状态迁移 | state machine / session 管理 | `last_transition` | 是 |
| `DialogueState.record_route` | `domain/state.py` | 记录本轮 route | state machine / exit 逻辑 | `last_route` | 是 |
| `DialogueState.record_task_outcome` | `domain/state.py` | 记录 task 结果 | state machine | `last_task_outcome` | 是 |
| `DialogueState.recompute_conversation_state` | `domain/state.py` | 依据 runtime state 重算高层状态 | 多个 task/object/session 方法 | `transition_to` | 是 |
| `DialogueState.begin_turn` | `domain/state.py` | 开始 pending_turn | `DialogueEngine.hand_dialogue` | `clear_last_route/clear_last_task_outcome` | 是 |
| `DialogueState.commit_turn` | `domain/state.py` | 提交 pending_turn | `DialogueEngine.hand_dialogue` | 当前 session `turns` | 是 |
| `DialogueState.reset_runtime_state` | `domain/state.py` | 强制清空 runtime state | runtime exit / 对象切换 | `last_transition` | 是 |

## Task

| 函数 | 文件 | 作用 | 直接调用方 | 典型下游 | 入口 |
| --- | --- | --- | --- | --- | --- |
| `TaskHandler.handle` | `task/handler.py` | task 轨总入口，先改状态再推 flow | `TaskCommandExecutor.execute` | `CommandProcessor.run` / `FlowExecutor.run_task` | 是 |
| `CommandProcessor.run` | `task/command/processor.py` | 顺序执行本轮 task commands | `TaskHandler.handle` | `_apply` | 是 |
| `_apply` | `task/command/processor.py` | 按命令类型分发 | `run` | start / set_slots / resume / cancel 分支 | 否 |
| `_handle_start_flow` | `task/command/processor.py` | 启动、恢复或打断任务 | `_apply` | `DialogueState.start_active_task` / `resume_task` / 系统提示流 | 否 |
| `_handle_set_slots` | `task/command/processor.py` | 合并本轮槽位 | `_apply` | `DialogueState.set_slots` | 否 |
| `_handle_resume_flow` | `task/command/processor.py` | 恢复暂停任务 | `_apply` | `DialogueState.resume_task` / `_activate_resumed_system_flow` | 否 |
| `_handle_cancel_flow` | `task/command/processor.py` | 取消当前任务上下文 | `_apply` | `DialogueState.end_active_task` / `clear_paused_tasks` | 否 |
| `FlowExecutor.run_task` | `task/flow/executor.py` | 推进 YAML flow，直到 `action_listen` | `TaskHandler.handle` | `_advance_until_action` / `ActionRunner.run` | 是 |
| `_advance_until_action` | `task/flow/executor.py` | 连续推进 step，直到产出 ActionCall | `run_task` | `_run_step` | 否 |
| `_run_collect_slots_step` | `task/flow/executor.py` | collect 位点的补槽、校验和追问 | `_run_step` | `_try_fill_slot_from_focused_object` / `start_active_system_task` | 否 |
| `_try_fill_slot_from_focused_object` | `task/flow/executor.py` | 用 focused object 自动补 collect 槽位 | `_run_collect_slots_step` | `DialogueState.set_slots` | 否 |
| `_run_action_step` | `task/flow/executor.py` | 推进 action step 并构造 ActionCall | `_run_step` | `_build_action_call` | 否 |
| `_build_action_call` | `task/flow/executor.py` | 把 step 转成 action runner 可执行请求 | `_run_action_step` | `ActionCall` | 否 |

## Knowledge

| 函数 | 文件 | 作用 | 直接调用方 | 典型下游 | 入口 |
| --- | --- | --- | --- | --- | --- |
| `KnowledgeHandler.handle` | `knowledge/handler.py` | knowledge 轨总入口，聚合知识并回复 | `TextTurnHandler._execute_context` | `_collect_knowledge_chunks` / `KnowledgeResponder.respond` | 是 |
| `_collect_knowledge_chunks` | `knowledge/handler.py` | 从多个 provider 聚合并去重 | `handle` | `KnowledgeProvider.provide` | 否 |
| `_build_missing_object_reply` | `knowledge/handler.py` | 对依赖对象的知识意图做缺对象提示 | `handle` | 直接返回提示文案 | 否 |
| `KnowledgeProvider.provide` | `knowledge/provider.py` | provider 抽象接口 | `KnowledgeHandler._collect_knowledge_chunks` | 子类实现 | 是 |
| `FocusedObjectKnowledgeProvider.provide` | `knowledge/provider.py` | 把 focused object 转成知识片段 | `KnowledgeHandler._collect_knowledge_chunks` | `_build_content` | 是 |
| `_build_content` | `knowledge/provider.py` | 压缩对象字段和住户信息 | `FocusedObjectKnowledgeProvider.provide` | `KnowledgeChunk` | 否 |
| `StaticRuleKnowledgeProvider.provide` | `knowledge/provider.py` | 从静态规则库取知识片段 | `KnowledgeHandler._collect_knowledge_chunks` | `KnowledgeChunk` | 是 |

## Focus

| 函数 | 文件 | 作用 | 直接调用方 | 典型下游 | 入口 |
| --- | --- | --- | --- | --- | --- |
| `FocusedObjectResolver.try_switch_focused_object_from_text` | `engine/focus/resolver.py` | 在文本轨前尝试切换 focused object | `TextTurnHandler.handle` | `FocusedObjectCatalog.load_resident_candidates` / `FocusedObjectTextSwitch.match_candidate_from_text` | 是 |
| `FocusedObjectResolver.resolve_object_commands` | `engine/focus/resolver.py` | 把对象消息转成 task commands | `ObjectTurnHandler._build_object_context` | `ObjectSlotHandoff.resolve_commands` | 是 |
| `ObjectSlotHandoff.resolve_commands` | `engine/focus/slot_handoff.py` | 判断对象消息能否直接补槽 | `FocusedObjectResolver.resolve_object_commands` | `_flow_has_unfilled_collect_slot` | 是 |
| `_flow_has_unfilled_collect_slot` | `engine/focus/slot_handoff.py` | 判断当前任务是否存在待填 collect 槽位 | `resolve_commands` | `CollectedFlowStep` 遍历 | 否 |
| `FocusedObjectTextSwitch.match_candidate_from_text` | `engine/focus/text_switch.py` | 文本命中唯一候选对象 | `FocusedObjectResolver.try_switch_focused_object_from_text` | 三种 matcher | 是 |
| `_match_unique_id_candidate` | `engine/focus/text_switch.py` | 通过对象 ID 匹配唯一候选 | `match_candidate_from_text` | `_find_unique_candidate` | 否 |
| `_match_unique_exact_title_candidate` | `engine/focus/text_switch.py` | 通过标题全匹配命中唯一候选 | `match_candidate_from_text` | `_find_unique_candidate` | 否 |
| `_match_unique_title_contains_candidate` | `engine/focus/text_switch.py` | 通过标题包含命中唯一候选 | `match_candidate_from_text` | `_find_unique_candidate` | 否 |
| `_find_unique_candidate` | `engine/focus/text_switch.py` | 在候选集合中做唯一性裁决 | 三个 matcher | `_is_current_object` / matcher 回调 | 否 |
| `normalize_match_text` | `engine/focus/text_switch.py` | 做对象文本匹配前的标准化清洗 | 各 matcher | `re.sub` 清洗 | 否 |

## Clarify

| 函数 | 文件 | 作用 | 直接调用方 | 典型下游 | 入口 |
| --- | --- | --- | --- | --- | --- |
| `ClarifyResponder.respond` | `clarify/responder.py` | 澄清轨总入口，组装提示词并调用 LLM | 文本校验失败 / 对象缺意图分支 | `_build_prompt_payload` | 是 |
| `_build_prompt_payload` | `clarify/responder.py` | 构造澄清提示词输入 | `respond` | `build_clarify_message` / `_serialize_focused_object` | 否 |
| `build_clarify_message` | `clarify/responder.py` | 为本轮澄清挑主消息 | `_build_prompt_payload` | contextual / reason 分支 | 否 |
| `_build_contextual_clarify_message` | `clarify/responder.py` | 优先生成任务/对象强上下文澄清 | `build_clarify_message` | `_build_active_task_followup_message` / `_build_object_intent_message` | 否 |
| `_build_reason_clarify_message` | `clarify/responder.py` | 按 ClarifyReason 选通用澄清模板 | `build_clarify_message` | missing track / invalid directive 等分支 | 否 |
| `_build_active_task_followup_message` | `clarify/responder.py` | 把澄清拉回当前 task 生命周期 | `_build_contextual_clarify_message` | `_build_slot_followup_message` | 否 |
| `_build_slot_followup_message` | `clarify/responder.py` | 按当前 collect 槽位给具体补槽提示 | `_build_active_task_followup_message` | 文案返回 | 否 |

## Chitchat

| 函数 | 文件 | 作用 | 直接调用方 | 典型下游 | 入口 |
| --- | --- | --- | --- | --- | --- |
| `ChitchatHandler.handle` | `chitchat/handler.py` | 闲聊轨总入口，整理消息与历史 | `TextTurnHandler._execute_context` | `ChitchatResponder.respond` | 是 |
| `ChitchatResponder.respond` | `chitchat/responder.py` | 调用闲聊提示词生成回复 | `ChitchatHandler.handle` | LLM / `_fallback` | 是 |
| `_fallback` | `chitchat/responder.py` | 闲聊 LLM 失败时的兜底回复 | `respond` | 直接返回文案 | 否 |

## Action

| 函数 | 文件 | 作用 | 直接调用方 | 典型下游 | 入口 |
| --- | --- | --- | --- | --- | --- |
| `build_action_runner` | `task/action/builder.py` | 构造完整 action runner | 装配层 | `register_builtin_action` / `register_customer_action` | 是 |
| `register_builtin_action` | `task/action/builder.py` | 注册内置 action | `build_action_runner` | `ActionRegistry.register` | 否 |
| `register_customer_action` | `task/action/builder.py` | 扫描并注册 custom action | `build_action_runner` | `pkgutil.iter_modules` / `ActionRegistry.register` | 否 |
| `ActionRunner.run` | `task/action/runner.py` | 运行单个 ActionCall | `FlowExecutor.run_task` | `ActionRegistry.get` / `Action.run` | 是 |
| `ActionRegistry.register` | `task/action/registry.py` | 写入 action 实例映射 | builder 注册阶段 | `_actions` 字典 | 否 |
| `ActionRegistry.get` | `task/action/registry.py` | 按名称取 action 实例 | `ActionRunner.run` | 具体 action | 否 |
| `ActionListener.run` | `task/action/builtin/listener.py` | flow 停下等待用户的哨兵 | `ActionRunner.run` | 空 `ActionResult` | 是 |
| `ActionResponse.run` | `task/action/builtin/response.py` | 渲染 action_response 模板文本 | `ActionRunner.run` | Jinja `Template.render` | 是 |
| `AnswerResidentWorkOrders.run` | `task/action/custom/lookup_resident_work_orders.py` | 查询住户工单列表 | `ActionRunner.run` | `request_property_api` / `build_work_order_object` | 是 |
| `AnswerResidentServiceItems.run` | `task/action/custom/lookup_resident_service_items.py` | 查询住户服务项目列表 | `ActionRunner.run` | `request_property_api` / `build_service_item_object` | 是 |
| `LookupWorkOrderStatus.run` | `task/action/custom/lookup_work_order_status.py` | 查询工单状态 | `ActionRunner.run` | `request_property_api` / `slot_updates` | 是 |
| `LookupWorkOrderProgress.run` | `task/action/custom/lookup_work_order_progress.py` | 查询工单进度 | `ActionRunner.run` | `request_property_api` / `slot_updates` | 是 |
| `LookupServiceItemDetail.run` | `task/action/custom/lookup_service_item_detail.py` | 查询服务项目详情 | `ActionRunner.run` | `request_property_api` / `slot_updates` | 是 |
| `SubmitWorkOrderUrgeRequest.run` | `task/action/custom/submit_work_order_urge_request.py` | 提交催办请求 | `ActionRunner.run` | `request_property_api` / `slot_updates` | 是 |
| `SubmitComplaintRequest.run` | `task/action/custom/submit_complaint_request.py` | 提交投诉请求 | `ActionRunner.run` | `request_property_api` / `slot_updates` | 是 |
| `AnswerResidentRule.run` | `task/action/custom/answer_resident_rule.py` | 返回住户规则答复 | `ActionRunner.run` | `build_rule_answer` / `slot_updates` | 是 |
| `request_property_api` | `task/action/custom/api.py` | 统一物业中台 HTTP 调用 | 多个 custom action | `httpx.AsyncClient` | 是 |
| `build_work_order_object` | `task/action/custom/objects.py` | 中台工单数据转 FocusedObject | 列表查询 action | `FocusedObject` | 否 |
| `build_service_item_object` | `task/action/custom/objects.py` | 中台服务项目转 FocusedObject | 列表查询 action | `FocusedObject` | 否 |
| `build_object_messages` | `task/action/custom/objects.py` | 对象列表转 BotMessage 列表 | 列表查询 action | `BotMessage` | 否 |
| `get_work_order_id` | `task/action/custom/slots.py` | 从槽位/对象读取工单 ID | 工单类 action | `get_slot` / focused object | 否 |
| `get_service_item_id` | `task/action/custom/slots.py` | 从槽位/对象读取服务项目 ID | 服务项目类 action | `get_slot` / focused object | 否 |
| `normalize_rule_topic` | `task/action/custom/resident_rules.py` | 规则主题归一化 | 规则答复 action | 关键词映射 | 否 |
| `build_rule_answer` | `task/action/custom/resident_rules.py` | 生成规则答复文案 | 规则答复 action | 主题模板选择 | 否 |

## Support

| 函数 | 文件 | 作用 | 直接调用方 | 典型下游 | 入口 |
| --- | --- | --- | --- | --- | --- |
| `lifespan` | `api/app.py` | FastAPI 启停时初始化资源 | FastAPI 生命周期 | `init_db_engine` / `init_dialogue_engine` | 是 |
| `init_dialogue_engine` | `api/dependencies.py` | 构建全局对话引擎 | `lifespan` | `build_dialogue_engine` | 是 |
| `get_session` | `api/dependencies.py` | 提供请求级数据库会话 | FastAPI 依赖注入 | `database.async_session` | 是 |
| `get_dialogue_state_repository` | `api/dependencies.py` | 构造状态仓储依赖 | `get_dialogue_service` | `DialogueStateRepository` | 是 |
| `get_dialogue_service` | `api/dependencies.py` | 构造路由层对话服务 | 路由依赖注入 | `DialogueService` | 是 |
| `DialogueStateRepository.load` | `repository/dialogue_state_repository.py` | 读取完整 DialogueState | `DialogueService` | `DialogueState.from_dict` | 是 |
| `DialogueStateRepository.save` | `repository/dialogue_state_repository.py` | upsert 保存完整 DialogueState | `DialogueService` | `session.execute/commit` | 是 |
| `HistoryBuilder.build` | `prompt/history_builder.py` | turn 历史转提示词文本 | planner / handler / responder | `_render_user_message` / `_render_bot_message` | 是 |
| `load_prompt` | `prompt/loader.py` | 读取 jinja2 提示词模板 | planner / clarify / chitchat | 本地模板文件 | 是 |
| `init_db_engine` | `infrastructure/database.py` | 初始化数据库引擎与 session 工厂 | `lifespan` | `create_async_engine` | 是 |
| `close_db_engine` | `infrastructure/database.py` | 释放数据库引擎资源 | `lifespan` | `engine.dispose` | 是 |
| `init_http_client` | `infrastructure/http.py` | 初始化全局 HTTP 客户端 | 手动调试入口 | `AsyncClient` | 是 |
| `close_http_client` | `infrastructure/http.py` | 关闭全局 HTTP 客户端 | 手动调试入口 | `http_client.aclose` | 是 |

## 备注

- 当前索引已覆盖批次 A+B+C+D 的主要生产链路
- `api/schemas.py`、`model/*.py` 这类以声明结构为主、几乎无手写函数逻辑的文件，本轮未展开函数索引
- FastAPI 路由、依赖注入、注册表分发这类隐式调用统一记作“框架入口 / 注册分发”

function serviceItem(id, title, price, description, serviceStatus) {
  return {
    type: "service_item",
    id,
    title,
    attributes: {
      price,
      description,
      service_status: serviceStatus,
    },
  };
}

function workOrder(id, title, status, amount, summary) {
  return {
    type: "work_order",
    id,
    title,
    attributes: {
      status,
      amount,
      summary,
    },
  };
}

const svc1001 = serviceItem(
  "SVC1001",
  "入户深度保洁",
  168,
  "提供厨房、卫生间、客厅和卧室的整屋深度保洁服务，适合换季或入住前集中清洁。",
  "可预约",
);

const svc1002 = serviceItem(
  "SVC1002",
  "空调清洗",
  120,
  "提供挂机与柜机的基础拆洗服务，适合夏季前保养。",
  "可预约",
);

const svc1006 = serviceItem(
  "SVC1006",
  "门禁卡补办",
  50,
  "丢失门禁卡后可在线登记补办申请并到服务中心领取。",
  "可办理",
);

const wo1001 = workOrder(
  "WO20260501001",
  "主卧空调不制冷",
  "待上门",
  80,
  "工程班已联系住户，今晚 19:30 上门检修。",
);

const wo1002 = workOrder(
  "WO20260501002",
  "厨房水槽下方渗水",
  "处理中",
  60,
  "维修师傅已完成初检，等待更换软管配件。",
);

const wo1004 = workOrder(
  "WO20260501004",
  "门禁卡失效",
  "待受理",
  20,
  "服务中心已收到工单，待安排门禁专员处理。",
);

function longScenario({
  id,
  title,
  residentId = "r1001",
  source,
  tags,
  turns,
  final_assertions,
}) {
  return {
    id,
    title,
    channel: "api",
    scenario_type: "regression_long_dialogue",
    residentId,
    source,
    tags,
    turns,
    final_assertions,
  };
}

export const apiScenarios = [
  longScenario({
    id: "track-switch_knowledge-clarify-task_work-order-followup",
    title: "工单对象进入知识追问，再从澄清切入催办任务",
    source: "mixed: history-backed",
    tags: ["track-switch", "knowledge-followup", "task-switch", "clarify"],
    turns: [
      {
        id: "turn-1-select-work-order",
        object: wo1001,
        checkpoint: {
          expected_tracks: ["clarify", "knowledge"],
          focused_object: { type: "work_order", id: "WO20260501001", title: "主卧空调不制冷" },
          active_task_flow_id: null,
          paused_task_count: 0,
          message_includes_any: ["主卧空调不制冷", "上门", "进度", "状态"],
          message_excludes: ["WO20260501004"],
        },
      },
      {
        id: "turn-2-ask-progress-and-fee",
        text: "这个工单现在什么进度，费用怎么算",
        checkpoint: {
          expected_track: "task",
          focused_object: { type: "work_order", id: "WO20260501001", title: "主卧空调不制冷" },
          active_task_flow_id: null,
          expected_task_outcome_kind: "completed_with_focus",
          task_outcome_reason_includes: ["service_progress_tracking"],
          state_paths: {
            "last_route.semantic_kind": "read_only_query",
            "last_task_outcome.semantic_kind": "read_only_query",
          },
          message_includes_any: ["进度", "费用", "上门", "今晚"],
          message_excludes: ["WO20260501004", "投诉"],
        },
      },
      {
        id: "turn-3-switch-to-urge",
        text: "那先帮我催一下，家里老人怕热",
        checkpoint: {
          expected_track: "task",
          focused_object: { type: "work_order", id: "WO20260501001", title: "主卧空调不制冷" },
          active_task_flow_id: null,
          expected_task_outcome_kind: "completed_with_focus",
          task_outcome_reason_includes: ["start:work_order_urge_submission"],
          state_paths: {
            "last_route.semantic_kind": "business_task",
            "last_task_outcome.semantic_kind": "business_task",
          },
          message_includes_any: ["催办", "已提交", "老人怕热"],
          forbidden_flow_ids: ["complaint_request_submission"],
        },
      },
      {
        id: "turn-4-fill-urge-reason",
        text: "原因就是家里老人怕热，希望今天能处理",
        checkpoint: {
          expected_track: "clarify",
          focused_object: { type: "work_order", id: "WO20260501001", title: "主卧空调不制冷" },
          active_task_flow_id: null,
          message_includes_any: ["催办", "投诉", "状态", "进度"],
          forbidden_flow_ids: ["complaint_request_submission"],
        },
      },
      {
        id: "turn-5-exit-task",
        text: "先这样，退出当前这个",
        checkpoint: {
          expected_tracks: ["knowledge", "chitchat"],
          focused_object: null,
          active_task_flow_id: null,
          paused_task_count: 0,
          active_system_task_flow_id: null,
          message_includes_any: ["先不继续", "已退出", "重新说"],
          message_excludes: ["主卧空调不制冷"],
        },
      },
      {
        id: "turn-6-start-new-topic",
        text: "顺便问下门禁卡补办怎么办",
        checkpoint: {
          expected_tracks: ["clarify", "knowledge"],
          focused_object: { type: "service_item", id: "SVC1006", title: "门禁卡补办" },
          active_task_flow_id: null,
          paused_task_count: 0,
          forbidden_focused_object_ids: ["WO20260501001"],
          message_includes_any: ["门禁卡", "补办", "办理", "服务中心"],
          message_excludes: ["主卧空调不制冷", "催办"],
        },
      },
    ],
    final_assertions: {
      focused_object: { type: "service_item", id: "SVC1006", title: "门禁卡补办" },
      active_task_flow_id: null,
      paused_task_count: 0,
      active_system_task_flow_id: null,
      forbidden_focused_object_ids: ["WO20260501001"],
      forbidden_flow_ids: ["work_order_urge_submission", "complaint_request_submission"],
    },
  }),
  longScenario({
    id: "track-switch_chitchat-knowledge-task_service-item-to-work-order",
    title: "寒暄后进入服务项目知识，再切到另一张工单任务",
    source: "mixed: designed",
    tags: ["track-switch", "object-switch", "service-to-work-order", "task-switch"],
    turns: [
      {
        id: "turn-1-chitchat",
        text: "你今天忙吗",
        checkpoint: {
          expected_track: "chitchat",
          focused_object: null,
          active_task_flow_id: null,
          paused_task_count: 0,
        },
      },
      {
        id: "turn-2-select-service-item",
        object: svc1001,
        checkpoint: {
          expected_tracks: ["clarify", "knowledge"],
          focused_object: { type: "service_item", id: "SVC1001", title: "入户深度保洁" },
          active_task_flow_id: null,
          message_includes_any: ["入户深度保洁", "收费", "办理方式", "服务说明", "可预约"],
          message_excludes: ["空调清洗"],
        },
      },
      {
        id: "turn-3-follow-up-service-item",
        text: "那收费和办理方式都说一下",
        checkpoint: {
          expected_tracks: ["clarify", "knowledge"],
          focused_object: { type: "service_item", id: "SVC1001", title: "入户深度保洁" },
          active_task_flow_id: null,
          message_includes_any: ["168", "办理", "预约", "入户深度保洁"],
          message_excludes: ["WO20260501004"],
        },
      },
      {
        id: "turn-4-switch-object-to-work-order",
        object: wo1004,
        checkpoint: {
          expected_tracks: ["clarify", "knowledge"],
          focused_object: { type: "work_order", id: "WO20260501004", title: "门禁卡失效" },
          active_task_flow_id: null,
          message_includes_any: ["门禁卡", "待受理", "服务中心", "投诉", "进度"],
          message_excludes: ["入户深度保洁"],
        },
      },
      {
        id: "turn-5-start-complaint",
        text: "这单太慢了，直接帮我投诉一下",
        checkpoint: {
          expected_tracks: ["task", "knowledge"],
          focused_object: { type: "work_order", id: "WO20260501004", title: "门禁卡失效" },
          active_task_flow_id: "complaint_request_submission",
          paused_task_count: 0,
          message_includes_any: ["投诉", "原因", "提交"],
          forbidden_flow_ids: ["work_order_urge_submission"],
          forbidden_focused_object_ids: ["SVC1001"],
        },
      },
      {
        id: "turn-6-fill-complaint-reason",
        text: "原因就是等太久了，已经影响进出",
        checkpoint: {
          expected_track: "task",
          focused_object: { type: "work_order", id: "WO20260501004", title: "门禁卡失效" },
          message_includes_any: ["投诉", "已提交", "影响进出", "原因"],
          forbidden_focused_object_ids: ["SVC1001"],
        },
      },
    ],
    final_assertions: {
      focused_object_any_of: [
        null,
        { type: "work_order", id: "WO20260501004", title: "门禁卡失效" },
      ],
      forbidden_focused_object_ids: ["SVC1001"],
      forbidden_flow_ids: ["work_order_urge_submission"],
    },
  }),
  longScenario({
    id: "track-switch_knowledge-clarify-task_service-item-to-business",
    title: "服务项目介绍后从澄清切入办理任务意图",
    source: "mixed: designed",
    tags: ["track-switch", "clarify", "service-item", "task-entry"],
    turns: [
      {
        id: "turn-1-select-service-item",
        object: svc1006,
        checkpoint: {
          expected_tracks: ["clarify", "knowledge"],
          focused_object: { type: "service_item", id: "SVC1006", title: "门禁卡补办" },
          active_task_flow_id: null,
          message_includes_any: ["收费", "办理", "服务说明", "预约"],
        },
      },
      {
        id: "turn-2-ask-more",
        text: "那怎么办理，需要多少钱",
        checkpoint: {
          expected_tracks: ["clarify", "knowledge"],
          focused_object: { type: "service_item", id: "SVC1006", title: "门禁卡补办" },
          active_task_flow_id: null,
          message_includes_any: ["办理", "费用", "还是", "先"],
        },
      },
      {
        id: "turn-3-express-need",
        text: "我就是想直接办一下，今天能不能处理",
        checkpoint: {
          expected_track: "knowledge",
          focused_object: { type: "service_item", id: "SVC1006", title: "门禁卡补办" },
          active_task_flow_id: null,
          message_includes_any: ["办理", "服务中心", "门禁卡补办", "领取"],
          message_excludes: ["入户深度保洁", "投诉"],
        },
      },
      {
        id: "turn-4-ask-location",
        text: "那领取地点在哪",
        checkpoint: {
          expected_tracks: ["clarify", "knowledge"],
          focused_object: { type: "service_item", id: "SVC1006", title: "门禁卡补办" },
          active_task_flow_id: null,
          message_includes_any: ["领取地点", "服务中心", "门禁卡补办"],
        },
      },
    ],
    final_assertions: {
      focused_object_any_of: [
        null,
        { type: "service_item", id: "SVC1006", title: "门禁卡补办" },
      ],
      active_task_flow_id: null,
      paused_task_count: 0,
    },
  }),
  longScenario({
    id: "track-switch_chitchat-knowledge-task_followed-by-reset",
    title: "闲聊后看工单，再进入投诉后退出并重开",
    source: "mixed: designed",
    tags: ["track-switch", "exit", "task-switch", "reset"],
    turns: [
      {
        id: "turn-1-opening",
        text: "早上好",
        checkpoint: {
          expected_tracks: ["clarify", "knowledge", "chitchat"],
          focused_object: null,
          active_task_flow_id: null,
          message_includes_any: ["早上", "你好", "帮你"],
        },
      },
      {
        id: "turn-2-select-work-order",
        object: wo1004,
        checkpoint: {
          expected_tracks: ["clarify", "knowledge"],
          focused_object: { type: "work_order", id: "WO20260501004", title: "门禁卡失效" },
          active_task_flow_id: null,
        },
      },
      {
        id: "turn-3-start-complaint",
        text: "这个太慢了，帮我投诉",
        checkpoint: {
          expected_track: "task",
          focused_object: { type: "work_order", id: "WO20260501004", title: "门禁卡失效" },
          active_task_flow_id: "complaint_request_submission",
          message_includes_any: ["投诉", "原因"],
        },
      },
      {
        id: "turn-4-exit",
        text: "算了，先取消",
        checkpoint: {
          expected_track: "chitchat",
          focused_object: null,
          active_task_flow_id: null,
          paused_task_count: 0,
          message_includes_any: ["已退出", "重新说", "先不继续"],
        },
      },
      {
        id: "turn-5-new-topic",
        text: "那你给我说说空调清洗",
        checkpoint: {
          expected_tracks: ["clarify", "knowledge"],
          focused_object: { type: "service_item", id: "SVC1002", title: "空调清洗" },
          active_task_flow_id: null,
          forbidden_focused_object_ids: ["WO20260501004"],
          message_includes_any: ["空调清洗", "费用", "预约", "服务"],
          message_excludes: ["门禁卡失效", "投诉"],
        },
      },
    ],
    final_assertions: {
      focused_object: { type: "service_item", id: "SVC1002", title: "空调清洗" },
      active_task_flow_id: null,
      paused_task_count: 0,
      forbidden_focused_object_ids: ["WO20260501004"],
    },
  }),
  longScenario({
    id: "object-switch_service-item-a-to-b_and-exit",
    title: "服务项目从 A 切到 B，再退出后起新话题",
    source: "mixed: history-backed",
    tags: ["object-switch", "exit", "knowledge-followup"],
    turns: [
      {
        id: "turn-1-select-svc1001",
        object: svc1001,
        checkpoint: {
          expected_tracks: ["clarify", "knowledge"],
          focused_object: { type: "service_item", id: "SVC1001", title: "入户深度保洁" },
          message_includes_any: ["入户深度保洁", "收费", "办理方式", "服务说明"],
          message_excludes: ["空调清洗"],
        },
      },
      {
        id: "turn-2-ask-service-item-detail",
        text: "那它现在能约吗",
        checkpoint: {
          expected_tracks: ["clarify", "knowledge"],
          focused_object: { type: "service_item", id: "SVC1001", title: "入户深度保洁" },
          message_includes_any: ["可预约", "预约", "入户深度保洁"],
        },
      },
      {
        id: "turn-3-switch-to-svc1002",
        text: "那空调清洗呢",
        checkpoint: {
          expected_tracks: ["clarify", "knowledge"],
          focused_object_any_of: [
            { type: "service_item", id: "SVC1002", title: "空调清洗" },
            null,
          ],
          active_task_flow_id: null,
          message_includes_any: ["空调清洗", "120", "可预约", "清洗"],
          message_excludes: ["入户深度保洁"],
          forbidden_focused_object_ids: ["SVC1001"],
        },
      },
      {
        id: "turn-4-ask-price-only",
        text: "费用",
        checkpoint: {
          expected_tracks: ["clarify", "knowledge"],
          focused_object_any_of: [
            { type: "service_item", id: "SVC1002", title: "空调清洗" },
            null,
          ],
          message_includes_any: ["120", "空调清洗", "费用"],
          message_excludes: ["168", "入户深度保洁"],
        },
      },
      {
        id: "turn-5-exit-context",
        text: "取消",
        checkpoint: {
          expected_track: "chitchat",
          focused_object: null,
          active_task_flow_id: null,
          paused_task_count: 0,
          message_includes_any: ["已退出", "先不继续", "重新说"],
          message_excludes: ["空调清洗", "入户深度保洁"],
        },
      },
      {
        id: "turn-6-new-topic-after-exit",
        text: "我想看看门禁卡失效那个工单",
        checkpoint: {
          expected_tracks: ["task", "knowledge"],
          focused_object: { type: "work_order", id: "WO20260501004", title: "门禁卡失效" },
          active_task_flow_id: null,
          expected_task_outcome_kind: "completed_with_focus",
          task_outcome_reason_includes: ["work_order_status_query"],
          forbidden_focused_object_ids: ["SVC1001", "SVC1002"],
          message_includes_any: ["门禁卡", "工单", "状态", "进度"],
          message_excludes: ["空调清洗", "入户深度保洁"],
        },
      },
    ],
    final_assertions: {
      focused_object: { type: "work_order", id: "WO20260501004", title: "门禁卡失效" },
      active_task_flow_id: null,
      paused_task_count: 0,
      forbidden_focused_object_ids: ["SVC1001", "SVC1002"],
    },
  }),
  longScenario({
    id: "object-switch_work-order-a-to-b_followup",
    title: "工单从 A 切到 B，验证旧工单上下文不残留",
    source: "mixed: designed",
    tags: ["object-switch", "work-order-switch", "knowledge-followup"],
    turns: [
      {
        id: "turn-1-select-wo1001",
        object: wo1001,
        checkpoint: {
          expected_tracks: ["clarify", "knowledge"],
          focused_object: { type: "work_order", id: "WO20260501001", title: "主卧空调不制冷" },
        },
      },
      {
        id: "turn-2-follow-up-wo1001",
        text: "那这个今晚几点来",
        checkpoint: {
          expected_tracks: ["task", "knowledge"],
          focused_object: { type: "work_order", id: "WO20260501001", title: "主卧空调不制冷" },
          active_task_flow_id: null,
          expected_task_outcome_kind: "completed_with_focus",
          task_outcome_reason_includes: ["service_progress_tracking"],
          message_includes_any: ["19:30", "今晚", "上门"],
        },
      },
      {
        id: "turn-3-switch-wo1002",
        object: wo1002,
        checkpoint: {
          expected_tracks: ["clarify", "knowledge"],
          focused_object: { type: "work_order", id: "WO20260501002", title: "厨房水槽下方渗水" },
          message_excludes: ["主卧空调不制冷"],
        },
      },
      {
        id: "turn-4-follow-up-wo1002",
        text: "这个是不是还在等配件",
        checkpoint: {
          expected_tracks: ["task", "knowledge"],
          focused_object: { type: "work_order", id: "WO20260501002", title: "厨房水槽下方渗水" },
          active_task_flow_id: null,
          expected_task_outcome_kind: "completed_with_focus",
          task_outcome_reason_includes: ["service_progress_tracking"],
          message_includes_any: ["配件", "软管", "处理中"],
          message_excludes: ["19:30", "今晚"],
        },
      },
    ],
    final_assertions: {
      focused_object_any_of: [
        null,
        { type: "work_order", id: "WO20260501002", title: "厨房水槽下方渗水" },
      ],
      forbidden_focused_object_ids: ["WO20260501001"],
      active_task_flow_id: null,
      paused_task_count: 0,
    },
  }),
  longScenario({
    id: "object-switch_service-item-to-work-order_with-task",
    title: "服务项目切到工单后进入投诉任务",
    source: "mixed: history-backed",
    tags: ["object-switch", "service-to-work-order", "task-switch"],
    turns: [
      {
        id: "turn-1-select-service-item",
        object: svc1002,
        checkpoint: {
          expected_tracks: ["clarify", "knowledge"],
          focused_object: { type: "service_item", id: "SVC1002", title: "空调清洗" },
          active_task_flow_id: null,
          message_includes_any: ["空调清洗", "120", "可预约"],
        },
      },
      {
        id: "turn-2-follow-up-service-item",
        text: "这个多久能约上",
        checkpoint: {
          expected_track: "knowledge",
          focused_object: { type: "service_item", id: "SVC1002", title: "空调清洗" },
          message_includes_any: ["预约", "上门", "空调清洗"],
        },
      },
      {
        id: "turn-3-switch-to-work-order",
        object: wo1004,
        checkpoint: {
          expected_tracks: ["clarify", "knowledge"],
          focused_object: { type: "work_order", id: "WO20260501004", title: "门禁卡失效" },
          active_task_flow_id: null,
          forbidden_focused_object_ids: ["SVC1002"],
          message_includes_any: ["门禁卡", "工单", "进度", "投诉", "催办"],
        },
      },
      {
        id: "turn-4-start-task",
        text: "这单帮我催一下",
        checkpoint: {
          expected_tracks: ["task", "clarify"],
          focused_object: { type: "work_order", id: "WO20260501004", title: "门禁卡失效" },
          active_task_flow_id: "work_order_urge_submission",
          message_includes_any: ["催办", "原因", "尽快"],
          forbidden_focused_object_ids: ["SVC1002"],
        },
      },
      {
        id: "turn-5-exit",
        text: "不办了，退出",
        checkpoint: {
          expected_track: "chitchat",
          focused_object: null,
          active_task_flow_id: null,
          paused_task_count: 0,
          message_includes_any: ["已退出", "重新说"],
        },
      },
    ],
    final_assertions: {
      focused_object: null,
      active_task_flow_id: null,
      paused_task_count: 0,
      forbidden_focused_object_ids: ["SVC1002"],
      forbidden_flow_ids: ["work_order_urge_submission"],
    },
  }),
  longScenario({
    id: "task-switch_progress-to-urge-to-complaint",
    title: "同一工单先问进度，再催办，再切投诉，验证任务栈切换",
    source: "mixed: designed",
    tags: ["task-switch", "long-dialogue", "paused-tasks"],
    turns: [
      {
        id: "turn-1-select-work-order",
        object: wo1002,
        checkpoint: {
          expected_tracks: ["clarify", "knowledge"],
          focused_object: { type: "work_order", id: "WO20260501002", title: "厨房水槽下方渗水" },
          active_task_flow_id: null,
        },
      },
      {
        id: "turn-2-ask-progress",
        text: "这个进度现在卡在哪",
        checkpoint: {
          expected_tracks: ["task", "knowledge"],
          focused_object: { type: "work_order", id: "WO20260501002", title: "厨房水槽下方渗水" },
          active_task_flow_id: null,
          expected_task_outcome_kind: "completed_with_focus",
          task_outcome_reason_includes: ["service_progress_tracking"],
          message_includes_any: ["进度", "处理中", "等待", "软管"],
        },
      },
      {
        id: "turn-3-start-urge",
        text: "你先帮我催办",
        checkpoint: {
          expected_track: "task",
          focused_object: { type: "work_order", id: "WO20260501002", title: "厨房水槽下方渗水" },
          active_task_flow_id: "work_order_urge_submission",
          message_includes_any: ["催办", "原因", "尽快"],
          forbidden_flow_ids: ["complaint_request_submission"],
        },
      },
      {
        id: "turn-4-interrupt-with-complaint",
        text: "不只是催办，我还想投诉处理太慢",
        checkpoint: {
          expected_track: "task",
          focused_object: { type: "work_order", id: "WO20260501002", title: "厨房水槽下方渗水" },
          active_task_flow_id: null,
          expected_task_outcome_kind: "completed_with_focus",
          task_outcome_reason_includes: ["set_slots:urge_reason"],
          state_paths: {
            "last_route.semantic_kind": "business_task",
            "last_task_outcome.semantic_kind": "business_task",
          },
          paused_task_count: 0,
          message_includes_any: ["催办", "已提交", "处理太慢"],
        },
      },
      {
        id: "turn-5-fill-complaint-reason",
        text: "投诉原因就是一直拖着没换配件",
        checkpoint: {
          expected_track: "task",
          active_task_flow_id: "complaint_request_submission",
          paused_task_count: 0,
          message_includes_any: ["投诉", "确认", "配件"],
        },
      },
      {
        id: "turn-6-exit-all",
        text: "先全部取消",
        checkpoint: {
          expected_track: "chitchat",
          focused_object: null,
          active_task_flow_id: null,
          paused_task_count: 0,
          active_system_task_flow_id: null,
          message_includes_any: ["已退出", "先不继续", "重新说", "取消"],
        },
      },
    ],
    final_assertions: {
      focused_object: null,
      active_task_flow_id: null,
      paused_task_count: 0,
      active_system_task_flow_id: null,
      forbidden_flow_ids: ["work_order_urge_submission", "complaint_request_submission"],
    },
  }),
  longScenario({
    id: "task-switch_urge-then-complaint-on-another-work-order",
    title: "先对一张工单催办，再切到另一张工单投诉",
    source: "mixed: designed",
    tags: ["task-switch", "cross-object", "paused-tasks", "exit"],
    turns: [
      {
        id: "turn-1-select-wo1001",
        object: wo1001,
        checkpoint: {
          expected_tracks: ["clarify", "knowledge"],
          focused_object: { type: "work_order", id: "WO20260501001", title: "主卧空调不制冷" },
        },
      },
      {
        id: "turn-2-start-urge",
        text: "这单帮我催一下",
        checkpoint: {
          expected_track: "task",
          focused_object: { type: "work_order", id: "WO20260501001", title: "主卧空调不制冷" },
          active_task_flow_id: "work_order_urge_submission",
          message_includes_any: ["催办", "原因"],
        },
      },
      {
        id: "turn-3-switch-object",
        object: wo1004,
        checkpoint: {
          expected_tracks: ["clarify", "knowledge"],
          focused_object: { type: "work_order", id: "WO20260501004", title: "门禁卡失效" },
          active_task_flow_id: null,
          message_includes_any: ["门禁卡", "待受理", "服务中心", "投诉", "进度"],
        },
      },
      {
        id: "turn-4-start-complaint",
        text: "这个我也想投诉一下，太慢",
        checkpoint: {
          expected_track: "task",
          focused_object: { type: "work_order", id: "WO20260501004", title: "门禁卡失效" },
          active_task_flow_id: "complaint_request_submission",
          paused_task_count: 0,
          message_includes_any: ["投诉", "原因", "太慢"],
        },
      },
      {
        id: "turn-5-exit-all",
        text: "全部退出",
        checkpoint: {
          expected_track: "chitchat",
          focused_object: null,
          active_task_flow_id: null,
          paused_task_count: 0,
          message_includes_any: ["已退出", "重新说"],
        },
      },
    ],
    final_assertions: {
      focused_object: null,
      active_task_flow_id: null,
      paused_task_count: 0,
      forbidden_flow_ids: ["work_order_urge_submission", "complaint_request_submission"],
    },
  }),
  longScenario({
    id: "exit-and-reset_followup-exit-then-reenter",
    title: "追问中退出，再重新进入另一条知识链",
    source: "mixed: history-backed",
    tags: ["exit-and-reset", "knowledge-followup", "reenter"],
    turns: [
      {
        id: "turn-1-select-service-item",
        object: svc1001,
        checkpoint: {
          expected_tracks: ["clarify", "knowledge"],
          focused_object: { type: "service_item", id: "SVC1001", title: "入户深度保洁" },
          message_includes_any: ["入户深度保洁", "可预约"],
        },
      },
      {
        id: "turn-2-follow-up",
        text: "那收费和说明再说一下",
        checkpoint: {
          expected_track: "knowledge",
          focused_object: { type: "service_item", id: "SVC1001", title: "入户深度保洁" },
          message_includes_any: ["168", "服务说明", "入户深度保洁"],
        },
      },
      {
        id: "turn-3-exit",
        text: "先不看这个了",
        checkpoint: {
          expected_track: "chitchat",
          focused_object: null,
          active_task_flow_id: null,
          paused_task_count: 0,
          message_includes_any: ["已退出", "重新说", "先不继续"],
        },
      },
      {
        id: "turn-4-reenter-new-topic",
        text: "那门禁卡补办是什么流程",
        checkpoint: {
          expected_tracks: ["clarify", "knowledge"],
          focused_object: { type: "service_item", id: "SVC1006", title: "门禁卡补办" },
          forbidden_focused_object_ids: ["SVC1001"],
          message_includes_any: ["门禁卡", "补办", "流程", "服务中心"],
          message_excludes: ["入户深度保洁"],
        },
      },
    ],
    final_assertions: {
      focused_object: { type: "service_item", id: "SVC1006", title: "门禁卡补办" },
      active_task_flow_id: null,
      paused_task_count: 0,
      forbidden_focused_object_ids: ["SVC1001"],
    },
  }),
  longScenario({
    id: "exit-and-reset_task-exit-then-start-new-object",
    title: "任务中退出后切到另一张工单，不残留旧任务",
    source: "mixed: designed",
    tags: ["exit-and-reset", "task", "cross-object"],
    turns: [
      {
        id: "turn-1-select-wo1002",
        object: wo1002,
        checkpoint: {
          expected_tracks: ["clarify", "knowledge"],
          focused_object: { type: "work_order", id: "WO20260501002", title: "厨房水槽下方渗水" },
          message_includes_any: ["厨房水槽下方渗水", "处理中", "状态", "进度"],
        },
      },
      {
        id: "turn-2-start-urge",
        text: "帮我催办一下",
        checkpoint: {
          expected_track: "task",
          focused_object: { type: "work_order", id: "WO20260501002", title: "厨房水槽下方渗水" },
          active_task_flow_id: "work_order_urge_submission",
          message_includes_any: ["催办", "原因"],
        },
      },
      {
        id: "turn-3-exit-task",
        text: "取消这个任务",
        checkpoint: {
          expected_track: "chitchat",
          focused_object: null,
          active_task_flow_id: null,
          paused_task_count: 0,
          message_includes_any: ["已退出", "重新说"],
        },
      },
      {
        id: "turn-4-select-new-work-order",
        object: wo1004,
        checkpoint: {
          expected_tracks: ["clarify", "knowledge"],
          focused_object: { type: "work_order", id: "WO20260501004", title: "门禁卡失效" },
          active_task_flow_id: null,
          forbidden_focused_object_ids: ["WO20260501002"],
          message_includes_any: ["门禁卡", "待受理", "服务中心", "进度"],
        },
      },
      {
        id: "turn-5-follow-up-new-object",
        text: "这个现在什么状态",
        checkpoint: {
          expected_tracks: ["task", "knowledge"],
          focused_object: { type: "work_order", id: "WO20260501004", title: "门禁卡失效" },
          active_task_flow_id: null,
          expected_task_outcome_kind: "completed_with_focus",
          task_outcome_reason_includes: ["work_order_status_query"],
          message_includes_any: ["待受理", "服务中心", "状态", "进度"],
          message_excludes: ["厨房水槽下方渗水"],
        },
      },
    ],
    final_assertions: {
      focused_object_any_of: [
        null,
        { type: "work_order", id: "WO20260501004", title: "门禁卡失效" },
      ],
      active_task_flow_id: null,
      paused_task_count: 0,
      forbidden_focused_object_ids: ["WO20260501002"],
    },
  }),
];

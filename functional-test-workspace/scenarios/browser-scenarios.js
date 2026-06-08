export const browserScenarios = [
  {
    id: "browser-sidebar-load",
    title: "输入 resident_id 后加载右侧工单/服务项目",
    channel: "browser",
    residentId: "r1001",
    steps: [
      {
        id: "load-sidebar",
        kind: "loadSidebar",
      },
    ],
    expected: {
      requireSidebarData: true,
    },
  },
  {
    id: "browser-click-work-order",
    title: "点击工单卡片并自动发到对话区",
    channel: "browser",
    residentId: "r1001",
    steps: [
      {
        id: "click-work-order",
        kind: "clickWorkOrderCard",
      },
    ],
    expected: {
      requireBotMessages: true,
    },
  },
  {
    id: "browser-click-service-item",
    title: "点击服务项目卡片并自动发到对话区",
    channel: "browser",
    residentId: "r1001",
    steps: [
      {
        id: "switch-service-tab",
        kind: "switchToServiceItems",
      },
      {
        id: "click-service-item",
        kind: "clickServiceItemCard",
      },
    ],
    expected: {
      requireBotMessages: true,
    },
  },
  {
    id: "browser-send-text",
    title: "发送文本消息并观察页面新增 bot 响应",
    channel: "browser",
    residentId: "r1001",
    steps: [
      {
        id: "send-text",
        kind: "sendText",
        text: "帮我看一下当前工单状态",
      },
    ],
    expected: {
      requireBotMessages: true,
    },
  },
  {
    id: "browser-work-order-followup",
    title: "先点工单，再追问状态/进度",
    channel: "browser",
    residentId: "r1001",
    steps: [
      {
        id: "click-work-order",
        kind: "clickWorkOrderCard",
      },
      {
        id: "send-followup",
        kind: "sendText",
        text: "再看一下这个工单的进度",
      },
    ],
    expected: {
      requireBotMessages: true,
    },
  },
];

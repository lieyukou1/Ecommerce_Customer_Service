<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'

const residentId = ref('r1001')
const draftMessage = ref('')
const isSending = ref(false)
const errorMessage = ref('')
const sidebarError = ref('')
const isLoadingSidebar = ref(false)
const messages = ref([])
const messagesContainer = ref(null)

const workOrders = ref([])
const serviceItems = ref([])
const activeTab = ref('work_orders')

const propertyButler = {
  name: '林管家',
  title: '社区服务总台',
  status: '物业演示版',
  avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=240&q=80',
}

const residentProfile = {
  name: '住户',
  avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=resident&backgroundColor=b6e3f4',
}

const chatHistoryEndpoint = computed(
  () => `/api/chat/history?resident_id=${encodeURIComponent(residentId.value.trim())}`
)
const chatEndpoint = computed(() => '/api/chat')
const residentWorkOrdersEndpoint = computed(
  () => `/commerce/residents/${encodeURIComponent(residentId.value.trim())}/work-orders`
)
const residentServiceItemsEndpoint = computed(
  () => `/commerce/residents/${encodeURIComponent(residentId.value.trim())}/service-items`
)

const quickActions = ['查看我的工单', '查询处理进度', '装修报备怎么做', '停车规则是什么']

const WORK_ORDER_STATUS_CLASS = {
  待受理: 'status-warning',
  处理中: 'status-info',
  待上门: 'status-info',
  已完成: 'status-success',
  已关闭: 'status-muted',
}

const SERVICE_STATUS_CLASS = {
  可预约: 'status-success',
  线上办理: 'status-info',
  需审核: 'status-warning',
  名额紧张: 'status-danger',
  可办理: 'status-success',
}

const turns = computed(() => {
  const result = []
  let currentTurn = null
  let turnIndex = 0

  for (const message of messages.value) {
    if (message.type === 'divider') {
      if (currentTurn) {
        result.push(currentTurn)
        currentTurn = null
      }
      result.push({
        type: 'divider',
        text: message.text,
      })
      continue
    }

    if (message.role === 'user') {
      if (currentTurn) {
        result.push(currentTurn)
      }
      turnIndex += 1
      currentTurn = {
        type: 'turn',
        id: `turn-${turnIndex}`,
        index: turnIndex,
        userMessage: message,
        botMessages: [],
      }
    } else if (message.role === 'bot') {
      if (!currentTurn) {
        turnIndex += 1
        currentTurn = {
          type: 'turn',
          id: `turn-${turnIndex}`,
          index: turnIndex,
          userMessage: null,
          botMessages: [],
        }
      }
      currentTurn.botMessages.push(message)
    }
  }

  if (currentTurn) {
    result.push(currentTurn)
  }

  return result
})

function createBaseMessage(role) {
  return {
    id: crypto.randomUUID(),
    role,
  }
}

function appendMessage(role, message) {
  if (role === 'divider') {
    messages.value.push({
      ...createBaseMessage('divider'),
      type: 'divider',
      text: message.text ?? '以上为历史提示',
    })
    return
  }

  if (message.object) {
    messages.value.push({
      ...createBaseMessage(role),
      type: 'object',
      objectType: message.object.type,
      payload: message.object,
    })
    return
  }

  messages.value.push({
    ...createBaseMessage(role),
    type: 'text',
    text: message.text ?? '',
    suggestions: message.suggestions ?? null,
  })
}

function appendUserText(text) {
  messages.value.push({
    ...createBaseMessage('user'),
    type: 'text',
    text,
  })
}

function appendUserObject(objectType, payload) {
  messages.value.push({
    ...createBaseMessage('user'),
    type: 'object',
    objectType,
    payload,
  })
}

function appendBotMessages(botMessages) {
  for (const message of botMessages) {
    appendMessage('bot', message)
  }
}

function setHistoryMessages(historyMessages) {
  messages.value = []
  for (const message of historyMessages) {
    const role = ['user', 'bot', 'divider'].includes(message.role) ? message.role : 'bot'
    appendMessage(role, message)
  }
}

async function scrollToBottom() {
  await nextTick()
  const container = messagesContainer.value
  if (container) {
    container.scrollTop = container.scrollHeight
  }
}

watch(
  () => messages.value.length,
  async () => {
    await scrollToBottom()
  }
)

function resetConversation() {
  messages.value = []
  errorMessage.value = ''
}

function formatAmount(amount) {
  const numericAmount = Number(amount)
  if (Number.isNaN(numericAmount)) {
    return '￥0.00'
  }
  return `￥${numericAmount.toFixed(2)}`
}

function formatDateTime(value) {
  if (!value) {
    return '待确认'
  }
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return String(value)
  }
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function getStatusClass(status, objectType = 'work_order') {
  if (objectType === 'service_item') {
    return SERVICE_STATUS_CLASS[status] || 'status-muted'
  }
  return WORK_ORDER_STATUS_CLASS[status] || 'status-muted'
}

function getObjectTitle(message) {
  return message.payload?.title || (message.objectType === 'work_order' ? '工单对象' : '服务项目对象')
}

function getObjectIdentifier(message) {
  const payload = message.payload ?? {}
  const id = payload.work_order_id ?? payload.service_item_id ?? payload.id
  const label = message.objectType === 'work_order' ? '工单号' : '项目号'
  return id ? `${label}：${id}` : label
}

function getObjectSummary(message) {
  const payload = message.payload ?? {}
  if (message.objectType === 'work_order') {
    return payload.summary || payload.status_desc || `当前状态：${payload.status || payload.attributes?.status || '待确认'}`
  }
  return payload.description || payload.attributes?.description || '可在此发起服务项目咨询。'
}

function getObjectAmount(message) {
  const payload = message.payload ?? {}
  const amount =
    message.objectType === 'work_order'
      ? payload.amount ?? payload.attributes?.amount
      : payload.price ?? payload.attributes?.price
  return formatAmount(amount)
}

async function fetchSidebarData() {
  const currentResidentId = residentId.value.trim()
  workOrders.value = []
  serviceItems.value = []
  sidebarError.value = ''

  if (!currentResidentId) {
    return
  }

  isLoadingSidebar.value = true
  try {
    const [workOrdersResponse, serviceItemsResponse] = await Promise.all([
      fetch(residentWorkOrdersEndpoint.value),
      fetch(residentServiceItemsEndpoint.value),
    ])

    const [workOrdersPayload, serviceItemsPayload] = await Promise.all([
      workOrdersResponse.json(),
      serviceItemsResponse.json(),
    ])

    if (!workOrdersResponse.ok) {
      throw new Error(workOrdersPayload.detail || '加载工单列表失败。')
    }
    if (!serviceItemsResponse.ok) {
      throw new Error(serviceItemsPayload.detail || '加载服务项目失败。')
    }

    workOrders.value = Array.isArray(workOrdersPayload?.data?.work_orders)
      ? workOrdersPayload.data.work_orders
      : []
    serviceItems.value = Array.isArray(serviceItemsPayload?.data?.service_items)
      ? serviceItemsPayload.data.service_items
      : []
  } catch (error) {
    sidebarError.value = error instanceof Error ? error.message : '加载右侧对象列表失败。'
  } finally {
    isLoadingSidebar.value = false
  }
}

async function fetchChatHistory() {
  const currentResidentId = residentId.value.trim()
  if (!currentResidentId) {
    messages.value = []
    return
  }

  try {
    const response = await fetch(chatHistoryEndpoint.value)
    if (response.status === 404) {
      messages.value = []
      return
    }
    const data = await response.json()
    if (!response.ok) {
      throw new Error(data.detail || '加载物业演示提示失败。')
    }
    if (currentResidentId === residentId.value.trim()) {
      setHistoryMessages(Array.isArray(data?.messages) ? data.messages : [])
    }
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '加载物业演示提示失败。'
  }
}

async function parseResponsePayload(response) {
  const rawText = await response.text()
  if (!rawText) {
    return null
  }

  try {
    return JSON.parse(rawText)
  } catch {
    return rawText
  }
}

async function sendPayload(payload) {
  if (isSending.value) {
    return
  }

  errorMessage.value = ''
  isSending.value = true

  try {
    const response = await fetch(chatEndpoint.value, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        resident_id: residentId.value.trim(),
        ...payload,
      }),
    })

    const data = await parseResponsePayload(response)
    if (!response.ok) {
      throw new Error(
        typeof data === 'string'
          ? data
          : typeof data?.detail === 'string'
            ? data.detail
            : JSON.stringify(data?.detail ?? data)
      )
    }

    appendBotMessages(Array.isArray(data?.messages) ? data.messages : [])
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '请求失败。'
  } finally {
    isSending.value = false
  }
}

async function sendSuggestion(text) {
  appendUserText(text)
  await sendPayload({ text })
}

async function sendQuickAction(text) {
  draftMessage.value = text
  await sendTextMessage()
}

async function sendTextMessage() {
  const text = draftMessage.value.trim()
  const currentResidentId = residentId.value.trim()

  if (!currentResidentId) {
    errorMessage.value = '请先输入 resident_id。'
    return
  }
  if (!text) {
    return
  }

  draftMessage.value = ''
  appendUserText(text)
  await sendPayload({ text })
}

async function sendWorkOrder(workOrder) {
  const currentResidentId = residentId.value.trim()
  if (!currentResidentId) {
    errorMessage.value = '请先输入 resident_id。'
    return
  }

  appendUserObject('work_order', { ...workOrder })
  await sendPayload({
    object: {
      type: 'work_order',
      id: workOrder.work_order_id,
      title: workOrder.title,
      attributes: {
        status: workOrder.status,
        amount: workOrder.amount,
        created_at: workOrder.created_at,
        appointment_time: workOrder.appointment_time,
        summary: workOrder.summary,
      },
    },
  })
}

async function sendServiceItem(serviceItem) {
  const currentResidentId = residentId.value.trim()
  if (!currentResidentId) {
    errorMessage.value = '请先输入 resident_id。'
    return
  }

  appendUserObject('service_item', { ...serviceItem })
  await sendPayload({
    object: {
      type: 'service_item',
      id: serviceItem.service_item_id,
      title: serviceItem.title,
      attributes: {
        price: serviceItem.price,
        description: serviceItem.description,
        service_status: serviceItem.service_status,
      },
    },
  })
}

watch(
  () => residentId.value.trim(),
  async (value, previousValue) => {
    if (value === previousValue) {
      return
    }
    resetConversation()
    if (!value) {
      workOrders.value = []
      serviceItems.value = []
      return
    }
    await Promise.all([fetchSidebarData(), fetchChatHistory()])
  }
)

onMounted(async () => {
  await Promise.all([fetchSidebarData(), fetchChatHistory()])
})
</script>

<template>
  <div class="app-shell">
    <div class="workspace">
      <section class="chat-card">
        <header class="chat-header">
          <div>
            <div class="eyebrow">物业管理系统前端</div>
            <h1>业主端智能管家演示台</h1>
            <p class="subtitle">
              保留老师单页壳，当前重点演示物业工单、服务项目、中台对象数据和后续智能管家接入口。
            </p>
          </div>
          <div class="service-panel">
            <img :src="propertyButler.avatar" :alt="propertyButler.name" class="service-avatar" />
            <div class="service-meta">
              <div class="service-name">{{ propertyButler.name }}</div>
              <div class="service-role">{{ propertyButler.title }}</div>
              <div class="service-status">{{ propertyButler.status }}</div>
            </div>
          </div>
        </header>

        <section class="controls">
          <label class="field">
            <span>resident_id</span>
            <div class="field-row">
              <input v-model="residentId" type="text" placeholder="r1001" />
              <button type="button" class="secondary-button" :disabled="isLoadingSidebar" @click="fetchSidebarData">
                {{ isLoadingSidebar ? '刷新中...' : '刷新对象数据' }}
              </button>
            </div>
          </label>
        </section>

        <section ref="messagesContainer" class="messages">
          <div v-if="turns.length === 0" class="welcome-card">
            <div class="welcome-label">当前演示不接真实 AI</div>
            <h2>先体验物业业务对象和中台能力</h2>
            <p>
              左侧保留对话壳和对象驱动交互，右侧展示住户的工单与服务项目。后续接入智能管家时，这里可以直接承接真实消息流。
            </p>
            <div class="quick-actions">
              <button
                v-for="action in quickActions"
                :key="action"
                type="button"
                class="quick-action"
                :disabled="isSending"
                @click="sendQuickAction(action)"
              >
                {{ action }}
              </button>
            </div>
          </div>

          <template v-for="(item, index) in turns" :key="item.id || index">
            <div v-if="item.type === 'divider'" class="history-divider">
              <span>{{ item.text }}</span>
            </div>

            <article v-else class="turn-card">
              <div class="turn-header">Turn {{ item.index }}</div>

              <div v-if="item.userMessage" class="turn-section user-section">
                <div class="agent-row">
                  <img :src="residentProfile.avatar" :alt="residentProfile.name" class="avatar" />
                  <div>
                    <div class="agent-name">{{ residentProfile.name }}</div>
                    <div class="agent-label">当前住户输入</div>
                  </div>
                </div>
                <div class="turn-bubble user-bubble">
                  <template v-if="item.userMessage.type === 'object'">
                    <div class="object-card">
                      <div class="object-badge">
                        {{ item.userMessage.objectType === 'work_order' ? '工单对象' : '服务项目对象' }}
                      </div>
                      <div class="object-title">{{ getObjectTitle(item.userMessage) }}</div>
                      <div class="object-meta">{{ getObjectIdentifier(item.userMessage) }}</div>
                      <div class="object-meta">{{ getObjectSummary(item.userMessage) }}</div>
                      <div class="object-bottom">
                        <span
                          v-if="item.userMessage.payload.status || item.userMessage.payload.service_status"
                          class="status-badge"
                          :class="getStatusClass(item.userMessage.payload.status || item.userMessage.payload.service_status, item.userMessage.objectType)"
                        >
                          {{ item.userMessage.payload.status || item.userMessage.payload.service_status }}
                        </span>
                        <span class="object-price">{{ getObjectAmount(item.userMessage) }}</span>
                      </div>
                    </div>
                  </template>
                  <p v-else>{{ item.userMessage.text }}</p>
                </div>
              </div>

              <div class="turn-section bot-section">
                <div class="agent-row">
                  <img :src="propertyButler.avatar" :alt="propertyButler.name" class="avatar" />
                  <div>
                    <div class="agent-name">{{ propertyButler.name }}</div>
                    <div class="agent-label">{{ propertyButler.title }}</div>
                  </div>
                </div>
                <div class="bot-messages">
                  <div v-for="botMsg in item.botMessages" :key="botMsg.id" class="turn-bubble bot-bubble">
                    <template v-if="botMsg.type === 'object'">
                      <div class="object-card">
                        <div class="object-badge">
                          {{ botMsg.objectType === 'work_order' ? '工单对象' : '服务项目对象' }}
                        </div>
                        <div class="object-title">{{ getObjectTitle(botMsg) }}</div>
                        <div class="object-meta">{{ getObjectIdentifier(botMsg) }}</div>
                        <div class="object-meta">{{ getObjectSummary(botMsg) }}</div>
                        <div class="object-bottom">
                          <span
                            v-if="botMsg.payload.status || botMsg.payload.service_status"
                            class="status-badge"
                            :class="getStatusClass(botMsg.payload.status || botMsg.payload.service_status, botMsg.objectType)"
                          >
                            {{ botMsg.payload.status || botMsg.payload.service_status }}
                          </span>
                          <span class="object-price">{{ getObjectAmount(botMsg) }}</span>
                        </div>
                      </div>
                    </template>
                    <template v-else>
                      <p>{{ botMsg.text }}</p>
                      <div v-if="botMsg.suggestions?.length" class="suggestion-chips">
                        <button
                          v-for="suggestion in botMsg.suggestions"
                          :key="suggestion"
                          type="button"
                          class="suggestion-chip"
                          :disabled="isSending"
                          @click="sendSuggestion(suggestion)"
                        >
                          {{ suggestion }}
                        </button>
                      </div>
                    </template>
                  </div>
                </div>
              </div>
            </article>
          </template>
        </section>

        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

        <form class="composer" @submit.prevent="sendTextMessage">
          <input
            v-model="draftMessage"
            type="text"
            placeholder="输入报修、规则咨询或服务问题，当前会返回物业演示占位说明"
            :disabled="isSending"
          />
          <button type="submit" :disabled="isSending || !residentId.trim()">
            {{ isSending ? '发送中...' : '发送' }}
          </button>
        </form>
      </section>

      <aside class="sidebar">
        <div class="sidebar-header">
          <div>
            <div class="eyebrow">对象卡片区</div>
            <h2>住户业务对象</h2>
          </div>
          <div class="resident-tips">示例住户：r1001 / r1002 / r1003</div>
        </div>

        <div class="tabs">
          <button
            type="button"
            class="tab-button"
            :class="{ active: activeTab === 'work_orders' }"
            @click="activeTab = 'work_orders'"
          >
            工单
          </button>
          <button
            type="button"
            class="tab-button"
            :class="{ active: activeTab === 'service_items' }"
            @click="activeTab = 'service_items'"
          >
            服务项目
          </button>
        </div>

        <p v-if="sidebarError" class="sidebar-error">{{ sidebarError }}</p>

        <div v-if="activeTab === 'work_orders'" class="sidebar-list">
          <div v-if="!workOrders.length && !isLoadingSidebar" class="sidebar-empty">
            当前住户暂无工单数据。
          </div>

          <article v-for="workOrder in workOrders" :key="workOrder.work_order_id" class="sidebar-card">
            <div class="card-top">
              <div>
                <div class="card-title">{{ workOrder.title }}</div>
                <div class="card-meta">工单号：{{ workOrder.work_order_id }}</div>
                <div class="card-meta">分类：{{ workOrder.category }}</div>
              </div>
              <div class="card-amount">{{ formatAmount(workOrder.amount) }}</div>
            </div>
            <div class="card-meta">{{ workOrder.summary || workOrder.status }}</div>
            <div class="card-bottom">
              <span class="status-badge" :class="getStatusClass(workOrder.status)">
                {{ workOrder.status }}
              </span>
              <span class="card-date">
                {{ workOrder.appointment_time ? `预约 ${formatDateTime(workOrder.appointment_time)}` : formatDateTime(workOrder.created_at) }}
              </span>
            </div>
            <button type="button" class="secondary-button full-width" @click="sendWorkOrder(workOrder)">
              发送到左侧交互区
            </button>
          </article>
        </div>

        <div v-else class="sidebar-list">
          <div v-if="!serviceItems.length && !isLoadingSidebar" class="sidebar-empty">
            当前住户暂无服务项目数据。
          </div>

          <article v-for="serviceItem in serviceItems" :key="serviceItem.service_item_id" class="sidebar-card">
            <img v-if="serviceItem.cover_url" :src="serviceItem.cover_url" :alt="serviceItem.title" class="card-image" />
            <div class="card-top">
              <div>
                <div class="card-title">{{ serviceItem.title }}</div>
                <div class="card-meta">项目号：{{ serviceItem.service_item_id }}</div>
              </div>
              <div class="card-amount">{{ formatAmount(serviceItem.price) }}</div>
            </div>
            <div class="card-meta">{{ serviceItem.description }}</div>
            <div class="card-bottom">
              <span class="status-badge" :class="getStatusClass(serviceItem.service_status, 'service_item')">
                {{ serviceItem.service_status }}
              </span>
            </div>
            <button type="button" class="secondary-button full-width" @click="sendServiceItem(serviceItem)">
              发送到左侧交互区
            </button>
          </article>
        </div>
      </aside>
    </div>
  </div>
</template>

<style>
:root {
  color-scheme: dark;
  font-family: Inter, "PingFang SC", "Microsoft YaHei", sans-serif;
  --bg: #09111d;
  --panel: rgba(12, 24, 39, 0.92);
  --panel-alt: rgba(16, 31, 48, 0.96);
  --border: rgba(255, 255, 255, 0.08);
  --border-strong: rgba(255, 255, 255, 0.14);
  --text: #eef4ff;
  --muted: #94a3b8;
  --accent: #22c55e;
  --accent-strong: #16a34a;
  --info: #38bdf8;
  --warning: #f59e0b;
  --danger: #fb7185;
  --success: #4ade80;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background:
    radial-gradient(circle at top right, rgba(34, 197, 94, 0.14), transparent 28%),
    radial-gradient(circle at bottom left, rgba(56, 189, 248, 0.12), transparent 24%),
    #060d16;
  color: var(--text);
}

#app {
  min-height: 100vh;
}

.app-shell {
  min-height: 100vh;
  padding: 24px;
}

.workspace {
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(340px, 0.7fr);
  gap: 24px;
  max-width: 1480px;
  margin: 0 auto;
}

.chat-card,
.sidebar {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 16px;
  backdrop-filter: blur(18px);
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.28);
}

.chat-card {
  min-height: calc(100vh - 48px);
  display: flex;
  flex-direction: column;
}

.chat-header,
.controls,
.composer,
.sidebar-header,
.tabs {
  padding-left: 24px;
  padding-right: 24px;
}

.chat-header {
  padding-top: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.eyebrow {
  font-size: 12px;
  color: var(--accent);
  margin-bottom: 8px;
  text-transform: uppercase;
}

h1,
h2 {
  margin: 0;
}

h1 {
  font-size: 30px;
}

.subtitle {
  margin: 10px 0 0;
  color: var(--muted);
  line-height: 1.6;
  max-width: 760px;
}

.service-panel {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 240px;
}

.service-avatar,
.avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(255, 255, 255, 0.16);
}

.service-meta,
.agent-row div {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.service-name,
.agent-name {
  font-weight: 700;
}

.service-role,
.service-status,
.agent-label,
.resident-tips,
.card-meta,
.card-date,
.object-meta {
  color: var(--muted);
  font-size: 13px;
  line-height: 1.5;
}

.controls {
  padding-top: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border);
}

.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field span {
  color: var(--muted);
  font-size: 13px;
}

.field-row {
  display: flex;
  gap: 12px;
}

input {
  width: 100%;
  min-height: 46px;
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid var(--border-strong);
  background: rgba(8, 17, 29, 0.9);
  color: var(--text);
  font-size: 14px;
}

input::placeholder {
  color: #64748b;
}

input:focus {
  outline: none;
  border-color: rgba(34, 197, 94, 0.7);
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.14);
}

button {
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.15s ease, opacity 0.15s ease, background 0.15s ease;
}

button:hover:not(:disabled) {
  transform: translateY(-1px);
}

button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.secondary-button,
.tab-button,
.quick-action,
.suggestion-chip {
  min-height: 42px;
  padding: 10px 16px;
  background: rgba(15, 28, 43, 0.92);
  color: var(--text);
  border: 1px solid var(--border);
}

.full-width {
  width: 100%;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.welcome-card,
.turn-card,
.sidebar-card {
  border: 1px solid var(--border);
  background: var(--panel-alt);
  border-radius: 14px;
}

.welcome-card {
  padding: 28px;
}

.welcome-label {
  display: inline-flex;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(34, 197, 94, 0.14);
  color: #86efac;
  font-size: 12px;
  margin-bottom: 14px;
}

.welcome-card p {
  color: var(--muted);
  line-height: 1.7;
}

.quick-actions,
.suggestion-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.turn-card {
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.turn-header {
  font-size: 12px;
  color: #86efac;
  letter-spacing: 0.04em;
}

.turn-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.agent-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.turn-bubble {
  padding: 16px;
  border-radius: 14px;
  line-height: 1.7;
}

.user-bubble {
  background: linear-gradient(135deg, rgba(22, 163, 74, 0.92), rgba(34, 197, 94, 0.86));
}

.bot-bubble {
  background: rgba(7, 16, 28, 0.9);
  border: 1px solid var(--border);
}

.turn-bubble p {
  margin: 0;
  white-space: pre-wrap;
}

.bot-messages {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.object-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.object-badge {
  display: inline-flex;
  align-self: flex-start;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.14);
  font-size: 12px;
}

.object-title {
  font-size: 16px;
  font-weight: 700;
}

.object-bottom,
.card-bottom {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.object-price,
.card-amount {
  font-weight: 700;
  color: #fde68a;
}

.history-divider {
  display: flex;
  align-items: center;
  gap: 14px;
  color: var(--muted);
}

.history-divider::before,
.history-divider::after {
  content: "";
  flex: 1;
  height: 1px;
  background: var(--border-strong);
}

.history-divider span {
  font-size: 12px;
}

.error-message,
.sidebar-error {
  margin: 0;
  padding: 0 24px 12px;
  color: var(--danger);
  font-size: 13px;
}

.composer {
  display: flex;
  gap: 12px;
  padding-top: 18px;
  padding-bottom: 20px;
  border-top: 1px solid var(--border);
}

.composer button {
  min-width: 110px;
  background: linear-gradient(135deg, var(--accent-strong), var(--accent));
  color: #04110a;
}

.sidebar {
  min-height: calc(100vh - 48px);
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding-top: 24px;
  padding-bottom: 18px;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: end;
}

.tabs {
  display: flex;
  gap: 10px;
  padding-top: 16px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--border);
}

.tab-button.active {
  background: rgba(34, 197, 94, 0.16);
  border-color: rgba(34, 197, 94, 0.4);
  color: #86efac;
}

.sidebar-list {
  flex: 1;
  overflow-y: auto;
  padding: 18px 24px 24px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.sidebar-card {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.card-image {
  width: 100%;
  height: 148px;
  object-fit: cover;
  border-radius: 12px;
}

.card-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.card-title {
  font-size: 16px;
  font-weight: 700;
}

.sidebar-empty {
  text-align: center;
  color: var(--muted);
  margin: auto 0;
  line-height: 1.7;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.status-warning {
  background: rgba(245, 158, 11, 0.16);
  color: #fbbf24;
}

.status-info {
  background: rgba(56, 189, 248, 0.16);
  color: #7dd3fc;
}

.status-success {
  background: rgba(74, 222, 128, 0.16);
  color: #86efac;
}

.status-muted {
  background: rgba(148, 163, 184, 0.16);
  color: #cbd5e1;
}

.status-danger {
  background: rgba(251, 113, 133, 0.16);
  color: #fda4af;
}

@media (max-width: 1180px) {
  .workspace {
    grid-template-columns: 1fr;
  }

  .chat-card,
  .sidebar {
    min-height: auto;
  }
}

@media (max-width: 720px) {
  .app-shell {
    padding: 12px;
  }

  .chat-header,
  .sidebar-header,
  .field-row,
  .composer {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>

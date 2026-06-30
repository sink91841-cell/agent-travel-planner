<template>
  <main class="history-page">
    <div class="history-inner">
      <header class="history-header">
        <div>
          <p class="history-eyebrow">旅行档案</p>
          <h1>历史旅行计划</h1>
          <p>查看以前生成的行程，继续编辑或删除不再需要的记录。</p>
        </div>
        <a-button type="primary" size="large" @click="router.push('/')">
          <template #icon><PlusOutlined /></template>
          规划新行程
        </a-button>
      </header>

      <a-alert
        v-if="loadError"
        class="history-error"
        type="error"
        show-icon
        :message="loadError"
      >
        <template #action>
          <a-button size="small" @click="loadHistory">重新加载</a-button>
        </template>
      </a-alert>

      <section class="history-panel" aria-label="历史旅行计划列表">
        <div class="history-toolbar">
          <h2>全部记录</h2>
          <span>{{ records.length }} 条</span>
        </div>

        <a-table
          :columns="columns"
          :data-source="records"
          :loading="loading"
          :pagination="false"
          :row-key="(record: TripHistorySummary) => record.id"
          :scroll="{ x: 900 }"
        >
          <template #emptyText>
            <a-empty description="暂无历史旅行计划">
              <a-button type="primary" @click="router.push('/')">开始规划</a-button>
            </a-empty>
          </template>

          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'trip'">
              <div class="trip-summary">
                <strong>{{ record.city }} · {{ getTravelDays(record) }}日游</strong>
                <span>{{ record.start_date }} 至 {{ record.end_date }}</span>
              </div>
            </template>

            <template v-else-if="column.key === 'preferences'">
              <div class="preference-summary">
                <span>{{ record.transportation }}</span>
                <span>{{ record.accommodation }}</span>
              </div>
            </template>

            <template v-else-if="column.key === 'created_at'">
              {{ formatDateTime(record.created_at) }}
            </template>

            <template v-else-if="column.key === 'actions'">
              <a-space>
                <a-button type="link" @click="openRecord(record.id)">
                  <template #icon><EyeOutlined /></template>
                  查看
                </a-button>
                <a-popconfirm
                  title="确认删除这条旅行计划吗？"
                  ok-text="删除"
                  cancel-text="取消"
                  placement="topRight"
                  @confirm="removeRecord(record.id)"
                >
                  <a-button type="link" danger :loading="deletingId === record.id">
                    <template #icon><DeleteOutlined /></template>
                    删除
                  </a-button>
                </a-popconfirm>
              </a-space>
            </template>
          </template>
        </a-table>
      </section>
    </div>
  </main>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { DeleteOutlined, EyeOutlined, PlusOutlined } from '@ant-design/icons-vue'
import { deleteTripHistory, getTripHistory } from '../services/api'
import type { TripHistorySummary } from '../types'

const router = useRouter()
const loading = ref(false)
const loadError = ref('')
const deletingId = ref('')
const records = ref<TripHistorySummary[]>([])

const columns = [
  { title: '行程', key: 'trip', width: 280 },
  { title: '出行偏好', key: 'preferences', width: 220 },
  { title: '创建时间', key: 'created_at', width: 190 },
  { title: '操作', key: 'actions', width: 180, fixed: 'right' as const }
]

const getTravelDays = (record: TripHistorySummary): number => {
  const start = new Date(`${record.start_date}T00:00:00`)
  const end = new Date(`${record.end_date}T00:00:00`)
  return Math.max(1, Math.round((end.getTime() - start.getTime()) / 86400000) + 1)
}

const formatDateTime = (value: string): string => {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

const loadHistory = async () => {
  loading.value = true
  loadError.value = ''
  try {
    const response = await getTripHistory()
    records.value = response.data
  } catch (error: any) {
    loadError.value = error.message || '历史记录加载失败'
  } finally {
    loading.value = false
  }
}

const openRecord = (historyId: string) => {
  router.push(`/result/${historyId}`)
}

const removeRecord = async (historyId: string) => {
  deletingId.value = historyId
  try {
    await deleteTripHistory(historyId)
    records.value = records.value.filter((record) => record.id !== historyId)
    message.success('历史记录已删除')
  } catch (error: any) {
    message.error(error.message || '删除历史记录失败')
  } finally {
    deletingId.value = ''
  }
}

onMounted(loadHistory)
</script>

<style scoped>
.history-page {
  min-height: calc(100vh - 121px);
  padding: 48px 24px 64px;
  background: #f3f5f8;
}

.history-inner {
  width: min(1180px, 100%);
  margin: 0 auto;
}

.history-header {
  margin-bottom: 28px;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
}

.history-eyebrow {
  margin: 0 0 6px;
  color: #2563eb;
  font-size: 14px;
  font-weight: 700;
}

.history-header h1 {
  margin: 0;
  color: #172033;
  font-size: 32px;
  line-height: 1.25;
}

.history-header p:last-child {
  margin: 8px 0 0;
  color: #64748b;
}

.history-error {
  margin-bottom: 20px;
}

.history-panel {
  overflow: hidden;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
}

.history-toolbar {
  min-height: 60px;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e2e8f0;
}

.history-toolbar h2 {
  margin: 0;
  font-size: 18px;
}

.history-toolbar span {
  color: #64748b;
}

.trip-summary,
.preference-summary {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.trip-summary strong {
  color: #172033;
  font-size: 15px;
}

.trip-summary span,
.preference-summary span {
  color: #64748b;
  font-size: 13px;
}

@media (max-width: 640px) {
  .history-page {
    padding: 28px 14px 48px;
  }

  .history-header {
    align-items: stretch;
    flex-direction: column;
  }

  .history-header h1 {
    font-size: 26px;
  }

  .history-header .ant-btn {
    width: 100%;
  }
}
</style>

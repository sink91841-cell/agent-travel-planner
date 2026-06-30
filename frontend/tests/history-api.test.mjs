import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'

const apiPath = new URL('../src/services/api.ts', import.meta.url)
const typesPath = new URL('../src/types/index.ts', import.meta.url)

test('history API exposes list detail update and delete operations', async () => {
  const source = await readFile(apiPath, 'utf8')

  assert.match(source, /getTripHistory/)
  assert.match(source, /getTripHistoryDetail/)
  assert.match(source, /updateTripHistory/)
  assert.match(source, /deleteTripHistory/)
  assert.match(source, /\/api\/history/)
})

test('trip response and history records expose required types', async () => {
  const source = await readFile(typesPath, 'utf8')

  assert.match(source, /history_id\?: string/)
  assert.match(source, /interface TripHistorySummary/)
  assert.match(source, /interface TripHistoryDetail/)
  assert.match(source, /interface TripHistoryListResponse/)
  assert.match(source, /interface TripHistoryDetailResponse/)
})

import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'

test('app exposes plan and history navigation with new brand', async () => {
  const source = await readFile(new URL('../src/App.vue', import.meta.url), 'utf8')

  assert.match(source, /智能旅行助手/)
  assert.match(source, /规划行程/)
  assert.match(source, /历史记录/)
  assert.doesNotMatch(source, /基于HelloAgents|HelloAgents智能旅行助手/)
})

test('mobile header wraps navigation without clipping buttons', async () => {
  const source = await readFile(new URL('../src/App.vue', import.meta.url), 'utf8')

  assert.match(source, /flex-wrap:\s*wrap/)
  assert.match(source, /min-height:\s*112px/)
  assert.match(source, /\.app-nav\s*\{[\s\S]*width:\s*100%/)
  assert.match(source, /grid-template-columns:\s*repeat\(2,\s*minmax\(0,\s*1fr\)\)/)
  assert.match(source, /overflow-x:\s*hidden/)
  assert.match(source, /\.app-content\s*\{[\s\S]*min-width:\s*0/)
})

test('router exposes the independent history page', async () => {
  const source = await readFile(new URL('../src/main.ts', import.meta.url), 'utf8')

  assert.match(source, /path: '\/history'/)
  assert.match(source, /component: History/)
})

test('history view supports loading retry view and confirmed deletion', async () => {
  const source = await readFile(
    new URL('../src/views/History.vue', import.meta.url),
    'utf8'
  )

  assert.match(source, /getTripHistory/)
  assert.match(source, /deleteTripHistory/)
  assert.match(source, /a-popconfirm/)
  assert.match(source, /重新加载/)
  assert.match(source, /查看/)
  assert.match(source, /删除/)
})

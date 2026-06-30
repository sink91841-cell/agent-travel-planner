import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'

test('browser title uses smart travel assistant brand', async () => {
  const source = await readFile(new URL('../index.html', import.meta.url), 'utf8')

  assert.match(source, /<title>智能旅行助手<\/title>/)
  assert.doesNotMatch(source, /HelloAgents/)
})

test('visible app shell does not advertise the framework', async () => {
  const source = await readFile(new URL('../src/App.vue', import.meta.url), 'utf8')

  assert.match(source, /智能旅行助手/)
  assert.doesNotMatch(source, /HelloAgents|基于HelloAgents/)
})

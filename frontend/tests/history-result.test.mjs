import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'

const resultPath = new URL('../src/views/Result.vue', import.meta.url)
const homePath = new URL('../src/views/Home.vue', import.meta.url)

test('home navigates generated plans using history id', async () => {
  const source = await readFile(homePath, 'utf8')

  assert.match(source, /response\.history_id/)
  assert.match(source, /`\/result\/\$\{response\.history_id\}`/)
})

test('result loads and updates a history record', async () => {
  const source = await readFile(resultPath, 'utf8')

  assert.match(source, /useRoute/)
  assert.match(source, /getTripHistoryDetail/)
  assert.match(source, /updateTripHistory/)
  assert.match(source, /historyId/)
  assert.match(source, /loadingPlan/)
  assert.match(source, /loadError/)
})

test('failed history saves keep edit mode active', async () => {
  const source = await readFile(resultPath, 'utf8')
  const saveFunction = source.match(/const saveChanges = async \(\) => \{[\s\S]*?\n\}/)?.[0] || ''

  assert.match(saveFunction, /await updateTripHistory/)
  assert.match(saveFunction, /editMode\.value = false/)
  assert.match(saveFunction, /catch/)
  assert.doesNotMatch(saveFunction, /catch[\s\S]*editMode\.value = false/)
})

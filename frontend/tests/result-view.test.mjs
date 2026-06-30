import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'

const resultViewPath = new URL('../src/views/Result.vue', import.meta.url)

test('result view does not render generated attraction placeholder images', async () => {
  const source = await readFile(resultViewPath, 'utf8')

  assert.doesNotMatch(source, /getAttractionImage/)
  assert.doesNotMatch(source, /handleImageError/)
  assert.doesNotMatch(source, /attraction-image-wrapper/)
})

test('result view keeps ticket price as regular attraction details', async () => {
  const source = await readFile(resultViewPath, 'utf8')

  assert.match(source, /<strong>门票:<\/strong>/)
})

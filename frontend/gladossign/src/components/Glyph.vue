<template>
  <MorphIcon
    :icon="icon"
    :size="size"
    :stroke-width="strokeWidth"
    :spring="spring"
    reduced-motion="user"
    color="currentColor"
    :label="label"
    class="glyph"
  />
</template>

<script setup>
import { computed } from 'vue'
import { MorphIcon } from 'morphicons/vue'
import { ICONS } from '../icons'

const props = defineProps({
  name: { type: String, default: 'check' },
  size: { type: [Number, String], default: 16 },
  strokeWidth: { type: [Number, String], default: 1.9 },
  spring: { type: [String, Object], default: 'snappy' },
  label: { type: String, default: undefined },
})

const icon = computed(() => ICONS[props.name] || ICONS.check)
</script>

<style scoped>
.glyph {
  display: inline-block;
  vertical-align: -0.18em;
  flex: none;
}
</style>

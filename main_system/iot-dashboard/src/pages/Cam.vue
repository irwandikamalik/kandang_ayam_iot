<template>

  <div class="cam-page">

    <button
      @click="toggleStream"
      :class="[
        'cam-btn',
        { active: isStreaming }
      ]"
    >

      {{
        isStreaming
        ? 'Stop Camera'
        : 'Start Camera'
      }}

    </button>

    <button
      @click="toggleYolo"
      :class="[
        'yolo-btn',
        { active: isYolo }
      ]"
    >

      {{
        isYolo
        ? 'Disable YOLO'
        : 'Enable YOLO'
      }}

    </button>

    <div
      v-if="isStreaming"
      class="stream-box"
    >

      <img
        :src="streamUrl"
        class="camera-stream"
      />

    </div>

  </div>

</template>

<script setup>
import '../assets/css/cam.css'


import { ref } from 'vue'

const isStreaming = ref(false)

const streamUrl = ref('')

const isYolo = ref(false)


async function toggleStream() {

  if (isStreaming.value) {

    isStreaming.value = false

    streamUrl.value = ''

    await fetch('/stop-stream')

  } else {

    streamUrl.value =
      `/stream?t=${Date.now()}`
    isStreaming.value = true
  }
}

function toggleYolo() {

  isYolo.value =
    !isYolo.value

  if (isStreaming.value) {

    streamUrl.value =
      isYolo.value

      ? `/stream-yolo?t=${Date.now()}`

      : `/stream?t=${Date.now()}`
  }
}
</script>
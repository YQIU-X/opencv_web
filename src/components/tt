<template>
  <div class="workspace"
       @mousedown="handleMouseDown"
       @mousemove="handleMouseMove"
       @mouseup="handleMouseUp">
    <img :src="currentImage" alt="当前图片" ref="image" draggable="false" />
  </div>
</template>

<script>
export default {
  name: 'Workspace',
  props: {
    currentImage: {
      type: String,
      default: ''
    }
  },
  data () {
    return {
      isDragging: false // 判断是否正在拖动
    }
  },
  methods: {
    handleMouseDown (event) {
      console.log('Mouse down triggered')
      this.isDragging = true // 开始拖动
      this.sendCoordinates(event)
    },
    handleMouseMove (event) {
      if (this.isDragging) {
        console.log('Mouse move triggered')
        this.sendCoordinates(event)
      }
    },
    handleMouseUp () {
      console.log('Mouse up triggered')
      this.isDragging = false // 停止拖动
    },
    sendCoordinates (event) {
      const img = this.$refs.image
      const rect = img.getBoundingClientRect()

      // 计算鼠标点击的坐标相对于图片的位置
      const x = event.clientX - rect.left
      const y = event.clientY - rect.top

      // 发送坐标到后端
      fetch('http://localhost:5001/click_coordinates', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ x, y })
      })
        .then(response => response.json())
        .then(data => {
          console.log('Coordinates sent successfully:', data)
        })
        .catch(error => {
          console.error('Error sending coordinates:', error)
        })
    }
  }
}
</script>

<style scoped>
.workspace {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #000000;
}
img {
  max-width: 100%;
  max-height: 100%;
}
</style>

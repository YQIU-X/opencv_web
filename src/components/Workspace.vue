<template>
  <div
    class="workspace"
    @mousedown="handleMouseDown"
    @mousemove="handleMouseMove"
    @mouseup="handleMouseUp"
  >
    <img :src="Img" alt="当前图片" ref="image" draggable="false" />
    <!-- 显示自定义的圆圈作为鼠标指针 -->
     <div
      v-if="selectedColor && selectedColor !== 'none'"
      :style="brushStyle"
      class="brush-circle"
    ></div>
  </div>
</template>

<script>
export default {
  name: 'Workspace',
  props: {
    Img: {
      type: String,
      default: null
    },
    brushSize: {
      type: Number,
      default: 10
    },
    selectedColor: {
      type: String,
      default: 'none'
    }
  },
  data () {
    return {
      clickTimeout: null,
      lastClickTime: 0,
      isDragging: false,
      dragStartX: 0,
      dragStartY: 0,
      mouseX: 0,
      mouseY: 0
    }
  },
  computed: {
    brushStyle () {
      return {
        width: `${this.brushSize}px`,
        height: `${this.brushSize}px`,
        left: `${this.mouseX}px`,
        top: `${this.mouseY}px`,
        border: '2px solid white', // 统一白色边框，粗细设置为 2px
        position: 'fixed',
        pointerEvents: 'none',
        borderRadius: '50%',
        transform: 'translate(-50%, -50%)'
      }
    }
  },
  methods: {
    sendCoordinates (event, type) {
      event.stopPropagation()
      const img = this.$refs.image
      const rect = img.getBoundingClientRect()

      const x = event.clientX - rect.left
      const y = event.clientY - rect.top

      const naturalWidth = img.naturalWidth
      const naturalHeight = img.naturalHeight
      const displayedWidth = rect.width
      const displayedHeight = rect.height
      const scaleX = naturalWidth / displayedWidth
      const scaleY = naturalHeight / displayedHeight

      this.updateMousePosition(event)

      if (type === 'double-click') {
        this.$emit('coordinate-clicked', x, y, scaleX, scaleY, type)
      } else if (type === 'dragging' || type === 'drag-end') {
        this.$emit('draw-clicked', x, y, scaleX, scaleY, type)
      }
    },
    handleMouseDown (event) {
      if (event.button !== 0) return

      this.isDragging = false
      this.dragStartX = event.clientX
      this.dragStartY = event.clientY
      this.updateMousePosition(event)

      const currentTime = new Date().getTime()
      const timeSinceLastClick = currentTime - this.lastClickTime

      if (timeSinceLastClick < 300) {
        clearTimeout(this.clickTimeout)
        this.lastClickTime = 0
        this.sendCoordinates(event, 'double-click')
      } else {
        this.lastClickTime = currentTime
        this.clickTimeout = setTimeout(() => {
          this.lastClickTime = 0
        }, 300)
      }
    },
    handleMouseMove (event) {
      this.updateMousePosition(event)

      if (event.buttons !== 1) return

      const deltaX = event.clientX - this.dragStartX
      const deltaY = event.clientY - this.dragStartY

      if (Math.abs(deltaX) > 10 || Math.abs(deltaY) > 10) {
        this.isDragging = true
        this.sendCoordinates(event, 'dragging')
      }
    },
    handleMouseUp (event) {
      if (this.isDragging) {
        this.sendCoordinates(event, 'drag-end')
      }
      this.isDragging = false
    },
    updateMousePosition (event) {
      this.mouseX = event.clientX
      this.mouseY = event.clientY
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
  position: relative; /* 相对定位，以便自定义指针定位 */
}

img {
  max-width: 100%;
  max-height: 100%;
}

.brush-circle {
  border-radius: 50%;
  position: fixed; /* 确保空心圆不受父容器影响 */
  pointer-events: none; /* 避免影响鼠标事件 */
  border: 2px solid white; /* 统一白色边框，粗细设置为 2px */
}
</style>

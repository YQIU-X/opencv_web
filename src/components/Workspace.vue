<template>
  <div class="workspace"
       @mousedown="handleMouseDown"
       @mousemove="handleMouseMove"
       @mouseup="handleMouseUp">
    <img :src="Img" alt="当前图片" ref="image" draggable="false" />
  </div>
</template>

<script>
export default {
  name: 'Workspace',
  props: {
    Img: {
      type: String,
      default: null
    }
  },
  data () {
    return {
      clickTimeout: null,
      lastClickTime: 0, // 上一次点击时间
      isDragging: false, // 是否正在拖动
      dragStartX: 0, // 拖动起始点X坐标
      dragStartY: 0 // 拖动起始点Y坐标
    }
  },
  methods: {
    sendCoordinates (event, type) {
      event.stopPropagation()
      const img = this.$refs.image
      const rect = img.getBoundingClientRect()

      // 计算鼠标点击的坐标相对于图片的位置
      const x = event.clientX - rect.left
      const y = event.clientY - rect.top

      // 计算缩放比例
      const naturalWidth = img.naturalWidth
      const naturalHeight = img.naturalHeight
      const displayedWidth = rect.width
      const displayedHeight = rect.height
      const scaleX = naturalWidth / displayedWidth
      const scaleY = naturalHeight / displayedHeight

      console.log(`${type} - coordinate`, x, y, scaleX, scaleY)
      if (type === 'double-click') {
        this.$emit('coordinate-clicked', x, y, scaleX, scaleY, type)
      } else if (type === 'dragging' || type === 'drag-end') {
        this.$emit('draw-clicked', x, y, scaleX, scaleY, type)
      }
    },
    handleMouseDown (event) {
      if (event.button !== 0) return // 仅处理左键点击

      this.isDragging = false // 重置拖动状态
      this.dragStartX = event.clientX
      this.dragStartY = event.clientY

      const currentTime = new Date().getTime()
      const timeSinceLastClick = currentTime - this.lastClickTime

      if (timeSinceLastClick < 300) {
        clearTimeout(this.clickTimeout) // 如果在300ms内再次点击，取消之前的单击事件
        this.lastClickTime = 0 // 重置点击时间
        this.sendCoordinates(event, 'double-click') // 触发双击事件时调用 sendCoordinates 方法
      } else {
        this.lastClickTime = currentTime
        // 单击时不执行任何操作
        this.clickTimeout = setTimeout(() => {
          // 300ms后认为没有双击，不执行任何操作
          this.lastClickTime = 0 // 重置点击时间
          // this.sendCoordinates(event, 'click') // 发送单击事件坐标
        }, 300) // 延迟300ms后判断为单击事件
      }
    },
    handleMouseMove (event) {
      if (event.buttons !== 1) return // 仅处理左键按下时的移动

      const deltaX = event.clientX - this.dragStartX
      const deltaY = event.clientY - this.dragStartY

      if (Math.abs(deltaX) > 10 || Math.abs(deltaY) > 10) {
        this.isDragging = true
        this.sendCoordinates(event, 'dragging') // 发送拖动事件坐标
        console.log('Dragging:', deltaX, deltaY)
      }
    },
    handleMouseUp (event) {
      if (this.isDragging) {
        this.sendCoordinates(event, 'drag-end') // 发送拖动结束事件坐标
        console.log('Drag ended')
      }
      this.isDragging = false // 重置拖动状态
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

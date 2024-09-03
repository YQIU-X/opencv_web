<template>
  <div class="workspace"
       @mousedown="handleMouseDown">
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
      lastClickTime: 0 // 上一次点击时间
    }
  },
  methods: {
    sendCoordinates (event) {
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

      console.log('coordinate-clicked', x, y, scaleX, scaleY)
      this.$emit('coordinate-clicked', x, y, scaleX, scaleY)
    },
    handleMouseDown (event) {
      if (event.button !== 0) return // 仅处理左键点击

      const currentTime = new Date().getTime()
      const timeSinceLastClick = currentTime - this.lastClickTime

      if (timeSinceLastClick < 300) {
        clearTimeout(this.clickTimeout) // 如果在300ms内再次点击，取消之前的单击事件
        this.lastClickTime = 0 // 重置点击时间
        this.sendCoordinates(event) // 触发双击事件时调用 sendCoordinates 方法
      } else {
        this.lastClickTime = currentTime
        // 单击时不执行任何操作
        this.clickTimeout = setTimeout(() => {
          // 300ms后认为没有双击，不执行任何操作
          this.lastClickTime = 0 // 重置点击时间
        }, 300) // 延迟300ms后判断为单击事件
      }
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

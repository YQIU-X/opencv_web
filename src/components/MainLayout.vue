<template>
  <div class="main-layout">
    <LeftSidebar @update-image="updateOriginalImage" />
    <div class="content">
      <Workspace :currentImage="currentImage" />
      <BottomGallery />
    </div>
    <RightSidebar @update-settings="updateSettings" />
  </div>
</template>

<script>
import LeftSidebar from './LeftSidebar.vue'
import Workspace from './Workspace.vue'
import RightSidebar from './RightSidebar.vue'
import BottomGallery from './BottomGallery.vue'

export default {
  name: 'MainLayout',
  components: {
    LeftSidebar,
    Workspace,
    RightSidebar,
    BottomGallery
  },
  data () {
    return {
      originalImage: '', // 原始图片路径
      currentImage: '' // 当前显示的图片路径
    }
  },
  methods: {
    updateOriginalImage (imageSrc) {
      this.originalImage = imageSrc
      this.currentImage = imageSrc // 显示原图
    },
    updateSettings (settings) {
      if (!this.originalImage) return // 确保原图已经设置

      fetch('http://localhost:5000/adjust_image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...settings,
          image: this.originalImage
        })
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok')
          }
          return response.json()
        })
        .then(data => {
          this.currentImage = `data:image/jpeg;base64,${data.image}`
        })
        .catch(error => {
          console.error('Error updating image:', error)
        })
    }
  }
}
</script>

<style scoped>
.main-layout {
  display: flex;
  height: 100vh;
}

.left-sidebar {
  flex: 0 0 200px; /* 固定宽度 */
}

.right-sidebar {
  flex: 0 0 300px; /* 固定宽度 */
}

.content {
  flex: 1; /* 让内容区占据剩余空间 */
  display: flex;
  flex-direction: column;
}

.workspace {
  flex: 1; /* 让工作区占据可用空间 */
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #000;
  min-height: 200px; /* 设置最小高度 */
  max-height: calc(100vh - 100px); /* 设置最大高度，减去底部栏高度 */
}

.bottom-gallery {
  height: 120px; /* 固定高度 */
  background-color: #1c1c1c;
  overflow-x: auto;
}
</style>

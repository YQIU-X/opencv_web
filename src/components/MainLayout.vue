<template>
  <div class="main-layout">
    <LeftSidebar :currentImage="currentImage ? currentImage : ''" @upload_images="upload_images" />
    <div class="content">
      <Workspace :Img="currentImage ? currentImage.src : ''" />
      <BottomGallery
        ref="bottomGallery"
        :selectedImage="currentImage ? currentImage : ''"
        @select-image="select_image"
        @remove-image="removeImage"
      />
    </div>
    <RightSidebar
      :temprature="currentImage ? currentImage.config.temprature : 0"
      :hue="currentImage ? currentImage.config.hue : 0"
      :exposure="currentImage ? currentImage.config.exposure : 0"
      :contrast="currentImage ? currentImage.config.contrast : 0"
      :Image="currentImage ? currentImage : null"
      @update-settings="updateSettings"
      @undo-action="undoAction"
      @next-image="nextImage"
    />
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
      currentImage: null // {id, src 64, config}
    }
  },
  methods: {
    upload_images (data) { // get the current image
      if (data.first_image !== null && data.first_image !== undefined) {
        this.currentImage = {
          id: 1,
          src: `data:image/jpeg;base64,${data.first_image}`,
          config: data.config
        }
        this.select_image(this.currentImage)
      }
      this.$refs.bottomGallery.updateImages()
    },
    freshCurrentImage (img64, newConfig) {
      this.currentImage.src = img64
      this.currentImage.config = newConfig
      this.$refs.bottomGallery.updateImages()
    },
    select_image (image) {
      this.currentImage = image
    },
    updateSettings (settings) {
      if (!this.currentImage) return

      fetch('http://localhost:5000/adjust_image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...settings,
          image_id: this.currentImage.id
        })
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok')
          }
          return response.json()
        })
        .then(data => {
          const base64Image = `data:image/jpeg;base64,${data.image}`
          this.freshCurrentImage(base64Image, data.config)
        })
        .catch(error => {
          console.error('Error updating image:', error)
        })
    },
    removeImage (imgId) {
      if (this.currentImage && this.currentImage.id === imgId) {
        this.currentImage = null
      }
    },
    undoAction () {
      if (this.currentImage && this.currentImage.id) {
        fetch('http://localhost:5004/undo_action', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ id: this.currentImage.id })
        })
          .then(response => response.json())
          .then(data => {
            this.currentImage = {
              id: data.id,
              src: `data:image/jpeg;base64,${data.src}`,
              config: data.config
            }
            this.select_image(this.currentImage)
            this.$refs.bottomGallery.updateImages()
          })
          .catch(error => {
            console.error('Error in undoAction:', error)
          })
      }
    },
    nextImage () {
      if (this.currentImage && this.currentImage.id) {
        fetch('http://localhost:5007/next_image', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ id: this.currentImage.id })
        })
          .then(response => response.json())
          .then(data => {
            this.currentImage = {
              id: data.id,
              src: `data:image/jpeg;base64,${data.src}`,
              config: data.config
            }
            this.select_image(this.currentImage)
          })
          .catch(error => {
            console.error('Error in nextImage:', error)
          })
      }
    }
  },
  mounted () {
    this.$refs.bottomGallery.updateImages()
  }
}
</script>

<style scoped>
.main-layout {
  display: flex;
  height: 98vh;
  background-color: #000; /* 设置背景颜色为黑色，消除白色边框的视觉效果 */
  border: none; /* 确保没有边框 */
  outline: none; /* 确保没有轮廓 */
  margin: 0; /* 确保没有外边距 */
  padding: 0; /* 确保没有内边距 */
}
.left-sidebar {
  flex: 0 0 150px; /* 固定宽度 */
}

.right-sidebar {
  flex: 0 0 300px; /* 固定宽度 */
}

.content {
  flex: 1; /* 使内容占据剩余空间 */
  display: flex;
  flex-direction: column;
}

.workspace {
  flex: 1; /* 使工作区占用可用空间 */
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #000; /* 设置工作区背景色 */
  min-height: 200px; /* 设置最小高度 */
  max-height: calc(100vh - 100px); /* 设置最大高度，减去底部栏的高度 */
}

.bottom-gallery {
  height: 120px; /* 固定高度 */
  background-color: #1c1c1c;
  overflow-x: auto;
}
</style>

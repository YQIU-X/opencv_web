<template>
  <div class="main-layout">
    <LeftSidebar @upload_images="upload_images" />
    <div class="content">
      <Workspace :currentImage="currentImg" />
      <BottomGallery
        :images="allImages"
        :selectedImage="backendImage"
        @select-image="updateCurrentImage"
        @remove-image="removeImage"
      />
    </div>
    <RightSidebar :backendImage="backendImage" @update-settings="updateSettings" />
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
      storedImageIds: [],
      currentImg: null
    }
  },
  methods: {
    upload_images (data) {
      this.storedImageIds = data.image_ids
      console.log('Received image IDs:', data.image_ids)
      console.log('Received first image base64:', data.first_image)
      if (data.first_image !== null && data.first_image !== undefined) {
        this.currentImg = `data:image/jpeg;base64,${data.first_image}`
      }
    },
    updateCurrentImage (imageSrc) {
      this.originalImage = imageSrc
      this.backendImage = imageSrc
    },
    updateSettings (settings) {
      if (!this.originalImage) return

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
          this.backendImage = `data:image/jpeg;base64,${data.image}`
        })
        .catch(error => {
          console.error('Error updating image:', error)
        })
    },
    removeImage (imageSrc) {
      this.allImages = this.allImages.filter(image => image.src !== imageSrc)
      if (this.backendImage === imageSrc) {
        this.backendImage = this.allImages.length > 0 ? this.allImages[0].src : ''
      }
    },
    overwriteImage (newImageSrc) {
      console.log('即将覆盖的图像路径：', newImageSrc)

      // 找到原始图像在 allImages 数组中的索引
      const imageIndex = this.allImages.findIndex(image => image.src === this.originalImage)

      if (imageIndex !== -1) {
        // 更新 allImages 数组中对应的图片的 src
        this.allImages[imageIndex].src = newImageSrc

        // 更新 originalImage 和 backendImage
        this.originalImage = newImageSrc
        this.backendImage = newImageSrc
      } else {
        console.warn('未找到需要覆盖的原图。')
      }
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
  flex: 0 0 200px; /* Fixed width */
}

.right-sidebar {
  flex: 0 0 300px; /* Fixed width */
}

.content {
  flex: 1; /* Make content take up the remaining space */
  display: flex;
  flex-direction: column;
}

.workspace {
  flex: 1; /* Make workspace take up available space */
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #000;
  min-height: 200px; /* Set minimum height */
  max-height: calc(100vh - 100px); /* Set maximum height, subtracting bottom bar height */
}

.bottom-gallery {
  height: 120px; /* Fixed height */
  background-color: #1c1c1c;
  overflow-x: auto;
}
</style>

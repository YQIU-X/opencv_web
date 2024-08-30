<template>
  <div class="main-layout">
    <LeftSidebar @upload_images="upload_images" />
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
    @update-settings="updateSettings" />
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
  },
  mounted () {
    this.$refs.bottomGallery.updateImages()
  }
}
</script>

<style scoped>
.main-layout {
  display: flex;
  height: 100vh;
}

.left-sidebar {
  flex: 0 0 150px; /* Fixed width */
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

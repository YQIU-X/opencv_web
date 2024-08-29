<template>
  <div class="main-layout">
    <LeftSidebar :backendImage="backendImage" @update-images="updateImages" @overwrite-image="overwriteImage" />
    <div class="content">
      <Workspace :currentImage="backendImage" />
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
      originalImage: '', // Store the original image path
      backendImage: '', // Store the image path returned by the backend
      allImages: [] // Images for displaying in BottomGallery
    }
  },
  methods: {
    updateImages (images) {
      this.allImages = images
      if (images.length > 0) {
        this.originalImage = images[0].src
        this.backendImage = images[0].src
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
      const updatedImages = this.allImages.map(image => {
        if (image.src === this.originalImage) {
          return {
            ...image,
            src: newImageSrc
          }
        }
        return image
      })

      this.allImages = updatedImages
      this.originalImage = newImageSrc
      this.backendImage = newImageSrc
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

<template>
  <div class="main-layout">
    <LeftSidebar @update-images="updateImages" />
    <div class="content">
      <Workspace :currentImage="backendImage" />
      <BottomGallery
        :images="allImages"
        :selectedImage="backendImage"
        @select-image="updateCurrentImage"
        @remove-image="removeImage"
      />
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
      originalImage: '', // Store the original image path
      backendImage: '', // Store the image path returned by the backend
      allImages: [] // Images for displaying in BottomGallery
    }
  },
  methods: {
    updateImages (images) {
      this.allImages = images // Update the list of all images
      if (images.length > 0) {
        this.originalImage = images[0].src // Save the first image as the original image
        this.backendImage = images[0].src // Initialize backendImage
      }
    },
    updateCurrentImage (imageSrc) {
      this.originalImage = imageSrc // Update the original image path
      this.backendImage = imageSrc // Update the displayed image path
    },
    updateSettings (settings) {
      if (!this.originalImage) return // Ensure there is an original image

      fetch('http://localhost:5000/adjust_image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...settings,
          image: this.originalImage // Adjust using the original image path
        })
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok')
          }
          return response.json()
        })
        .then(data => {
          this.backendImage = `data:image/jpeg;base64,${data.image}` // Update backendImage
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

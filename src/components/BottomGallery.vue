<template>
  <div class="bottom-gallery" @click="hideContextMenu">
    <img
      v-for="image in Images"
      :src="image.src"
      :key="image.id"
      :class="{'selected': image.id === selectedImage.id}"
      class="thumbnail"
      @click="selectImage(image)"
      @contextmenu.prevent="showContextMenu($event, image)"
    />
    <div v-if="contextMenuVisible" :style="{ top: `${contextMenuY}px`, left: `${contextMenuX}px` }" class="context-menu">
      <ul>
        <li @click="removeImage(contextMenuImage.src)">移除</li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BottomGallery',
  props: {
    selectedImage: { // equivalent to currentImage in MainLayout
      type: Object,
      default: () => ({
        id: '',
        src: '',
        config: {}
      })
    }
  },
  data () {
    return {
      Images: [], // [{id, src, config}]
      contextMenuVisible: false,
      contextMenuX: 0,
      contextMenuY: 0,
      contextMenuImage: null
    }
  },
  methods: {
    updateImages () {
      fetch('http://localhost:5006/load_images', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok')
          }
          return response.json()
        })
        .then(data => {
          if (data && data.images) {
            console.log('datadatadata', data.images)
            this.Images = data.images.map(image => ({
              id: image.id,
              src: `data:image/jpeg;base64,${image.img64}`,
              config: image.config
            }))

            if (this.Images.length > 0 && this.selectedImage !== null) {
              this.selectImage(this.Images[0])
            }
          }
        })
        .catch(error => {
          console.error('Error fetching and updating images:', error)
        })
    },
    selectImage (image) {
      this.$emit('select-image', image)
    },

    showContextMenu (event, image) {
      this.contextMenuX = event.clientX
      this.contextMenuY = event.clientY
      this.contextMenuImage = image
      this.contextMenuVisible = true
    },
    hideContextMenu () {
      this.contextMenuVisible = false
    },
    removeImage (imageSrc) {
      this.$emit('remove-image', imageSrc)
      this.hideContextMenu()
    }
  }
}
</script>

<style scoped>
.bottom-gallery {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 10px;
  background-color: #1c1c1c;
  overflow-x: auto;
  justify-content: center;
}

.thumbnail {
  width: 95px; /* Adjusted to account for the inward border */
  height: 95px; /* Adjusted to account for the inward border */
  object-fit: cover;
  transition: border 0.3s ease;
  box-sizing: border-box; /* Ensures the border is added inside */
}

.thumbnail.selected {
  border: 5px solid white;
}

.context-menu {
  position: absolute;
  background-color: #333;
  color: white;
  border-radius: 5px;
  padding: 5px;
  z-index: 1000;
}

.context-menu ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

.context-menu li {
  padding: 5px 10px;
  cursor: pointer;
}

.context-menu li:hover {
  background-color: #555;
}
</style>

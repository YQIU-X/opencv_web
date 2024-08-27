<template>
  <div class="bottom-gallery" @click="hideContextMenu">
    <img
      v-for="image in images"
      :src="image.src"
      :key="image.id"
      :class="{'selected': image.src === selectedImage}"
      class="thumbnail"
      @click="selectImage(image.src)"
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
    images: {
      type: Array,
      default: () => []
    },
    selectedImage: {
      type: String,
      default: ''
    }
  },
  data () {
    return {
      contextMenuVisible: false,
      contextMenuX: 0,
      contextMenuY: 0,
      contextMenuImage: null
    }
  },
  methods: {
    selectImage (src) {
      this.$emit('select-image', src)
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
  width: 100px;
  height: 100px;
  object-fit: cover;
  transition: border 0.3s ease;
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

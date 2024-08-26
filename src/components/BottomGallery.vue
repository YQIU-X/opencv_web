<template>
  <div class="bottom-gallery">
    <img v-for="image in images" :src="image.src" :key="image.id" class="thumbnail" @click="selectImage(image.src)" />
  </div>
</template>

<script>
export default {
  name: 'BottomGallery',
  props: {
    images: {
      type: Array,
      default: () => []
    }
  },
  methods: {
    selectImage (src) {
      this.$emit('select-image', src)
    }
  }
}
</script>

<style scoped>
.bottom-gallery {
  display: flex;
  overflow-x: scroll;
  padding: 10px;
  background-color: #1c1c1c;
}
.thumbnail {
  width: 100px;
  height: 100px;
  margin-right: 5px;
  object-fit: cover;
}
</style>

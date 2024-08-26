<template>
  <div class="bottom-gallery">
    <img v-for="image in images" :src="image.src" :key="image.id" class="thumbnail" />
  </div>
</template>

<script>
export default {
  name: 'BottomGallery',
  data () {
    return {
      images: [
        { id: 1, src: 'image1.jpg' },
        { id: 2, src: 'image2.jpg' }
        // 其他图片数据
      ]
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

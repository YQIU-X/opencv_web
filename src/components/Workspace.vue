<template>
  <div class="workspace">
    <img :src="currentImage" alt="当前图片" />
  </div>
</template>

<script>
export default {
  name: 'Workspace',
  props: {
    currentImage: {
      type: String,
      default: ''
    }
  }
}
</script>

<style scoped>
.workspace {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #000000;
}
img {
  max-width: 100%;
  max-height: 100%;
}
</style>

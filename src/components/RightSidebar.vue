<template>
  <div class="right-sidebar">
    <div class="histogram-section">
    <div class="image-container">
      <h3 class="image-title">直方图</h3>
      <img src="@/assets/input_image.jpg" alt="直方图" class="histogram-img"/>
    </div>
  </div>
    <div>
      <label>色温</label>
      <input type="range" min="-100" max="100" v-model="temprature" @input="emitChanges" />
      <span>{{ temprature }}</span>
    </div>
    <div>
      <label>色调</label>
      <input type="range" min="-90" max="90" v-model="hue" @input="emitChanges" />
      <span>{{ hue }}</span>
    </div>
    <div>
      <label>曝光</label>
      <input type="range" min="-10" max="10" v-model="exposure" @input="emitChanges" />
      <span>{{ exposure }}</span>
    </div>
    <div>
      <label>对比</label>
      <input type="range" min="-10" max="10" v-model="contrast" @input="emitChanges" />
      <span>{{ contrast }}</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RightSidebar',
  data () {
    return {
      temprature: 0,
      hue: 0,
      exposure: 0,
      contrast: 0
    }
  },
  methods: {
    emitChanges () {
      this.$emit('update-settings', {
        temprature: this.temprature,
        hue: this.hue,
        exposure: this.exposure,
        contrast: this.contrast
      })
    }
  }
}
</script>

<style scoped>
.right-sidebar {
  width: 300px;
  padding: 10px;
  background-color: #2c2c2c;
  color: #ffffff;
}

.right-sidebar div {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.right-sidebar label {
  width: 80px;
}

.right-sidebar input[type="range"] {
  flex: 1;
  margin: 0 10px;
}

.right-sidebar span {
  width: 40px;
  text-align: right;
}

.histogram-section {
  margin-bottom: 20px;
  position: relative; /* Ensure relative positioning for child elements */
}

.image-container {
  position: relative;
}

.histogram-img {
  width: 100%;
  height: auto; /* Maintain aspect ratio */
  max-width: 300px;
  max-height: 200px; /* Limit the maximum height */
}

.image-title {
  position: absolute;
  top: 0;
  right: 0; /* Position the title in the top-right corner */
  background-color: rgba(0, 0, 0, 0.5);
  color: #ffffff;
  text-align: center;
  padding: 5px;
  max-height: 30px; /* Optional: Set a maximum height for the title */
  line-height: 30px; /* Optional: Center the text vertically */
  overflow: hidden; /* Optional: Hide text that overflows */
}
</style>

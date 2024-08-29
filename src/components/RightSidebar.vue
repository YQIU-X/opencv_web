<template>
  <div class="right-sidebar">
    <h3 class="image-title">直方图</h3>
    <div class="histogram-section">
      <div class="image-container">
        <img :src="histogramImage" alt="直方图" class="histogram-img" />
      </div>
    </div>
    <!-- 按钮行 -->
    <div class="button-row">
      <button @click="currentPage = 1" class="connected-button">
        <img src="../../items/dataIcon.png" alt="按钮1" class="button-icon1" />
      </button>
      <button @click="currentPage = 2" class="connected-button">
        <img src="path/to/image2.png" alt="按钮2" class="button-icon" />
      </button>
      <button @click="currentPage = 3" class="connected-button">
        <img src="path/to/image2.png" alt="按钮3" class="button-icon" />
      </button>
      <button @click="currentPage = 4" class="connected-button">
        <img src="../../items/bergerIcon.png" alt="按钮4" class="button-icon4" />
      </button>
    </div>
    <!-- 根据 currentPage 显示不同的内容 -->
    <div v-if="currentPage === 1">
      <div class="slider-container">
        <label>色温</label>
        <input type="range" min="-100" max="100" v-model="temprature" @input="emitChanges" />
        <span>{{ temprature }}</span>
      </div>
      <div class="slider-container">
        <label>色调</label>
        <input type="range" min="-90" max="90" v-model="hue" @input="emitChanges" />
        <span>{{ hue }}</span>
      </div>
      <div class="slider-container">
        <label>曝光</label>
        <input type="range" min="-100" max="100" v-model="exposure" @input="emitChanges" />
        <span>{{ exposure }}</span>
      </div>
      <div class="slider-container">
        <label>对比</label>
        <input type="range" min="-50" max="50" v-model="contrast" @input="emitChanges" />
        <span>{{ contrast }}</span>
      </div>
    </div>
    <!-- 第二个页面的内容 -->
    <div v-if="currentPage === 2">
      <!-- 页面 2 的内容 -->
      <p>这是第二个页面的内容。</p>
    </div>
    <!-- 第三个页面的内容 -->
    <div v-if="currentPage === 3">
      <!-- 页面 3 的内容 -->
      <p>这是第三个页面的内容。</p>
    </div>
    <!-- 第四个页面的内容 -->
    <div v-if="currentPage === 4">
      <!-- 添加十个按钮 -->
      <div class="button-container">
        <button v-for="n in 10" :key="n" class="extra-button">按钮 {{ n }}</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RightSidebar',
  props: {
    selectedImage: {
      type: String,
      default: ''
    },
    backendImage: {
      type: String,
      required: true
    }
  },
  data () {
    return {
      histogramImage: '',
      temprature: 0,
      hue: 0,
      exposure: 0,
      contrast: 0,
      currentPage: 1 // 控制当前显示的页面
    }
  },
  watch: {
    backendImage: {
      immediate: true,
      handler (newImage) {
        this.fetchHistogram(newImage)
      }
    }
  },
  methods: {
    fetchHistogram (imageData) {
      fetch('http://localhost:5003/upload_image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image: imageData })
      })
        .then(response => response.json())
        .then(data => {
          this.histogramImage = `data:image/jpeg;base64,${data.image}`
        })
        .catch(error => {
          console.error('Error fetching histogram:', error)
        })
    },
    emitChanges () {
      this.$emit('update-settings', {
        temprature: this.temprature,
        hue: this.hue,
        exposure: this.exposure,
        contrast: this.contrast
      })
    },
    resetSettings () {
      this.temprature = 0
      this.hue = 0
      this.exposure = 0
      this.contrast = 0
      this.emitChanges()
    },
    applySettings () {
      this.emitChanges()
    },
    saveSettings () {
      console.log('Settings saved!')
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
  position: relative;
}

.image-title {
  margin: 0;
  margin-bottom: 10px;
  text-align: right;
}

.histogram-section {
  margin-bottom: 20px;
}

.histogram-img {
  width: 100%;
  height: auto;
  max-width: 300px;
  max-height: 200px;
}

.button-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.connected-button {
  flex: 1;
  padding: 10px 0;
  background-color: #3a3a3a;
  border: 1px solid #2c2c2c;
  color: #ffffff;
  text-align: center;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.connected-button:not(:last-child) {
  border-right: none;
}

.connected-button:hover {
  background-color: #4a4a4a;
}

.button-icon1 {
  width: 25px; /* 设置图标宽度 */
  height: 25px; /* 设置图标高度 */
}

.button-icon4 {
  width: 30px; /* 设置图标宽度 */
  height: 30px; /* 设置图标高度 */
}

.slider-container {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-bottom: 10px;
}

.right-sidebar label {
  margin-bottom: 5px;
}

.right-sidebar input[type="range"] {
  width: 100%;
  margin-bottom: 5px;
}

.right-sidebar span {
  width: 100%;
  text-align: right;
  margin-bottom: 5px;
}

.button-container {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.extra-button {
  flex: 1 1 30%;
  padding: 5px;
  background-color: #3a3a3a;
  color: #ffffff;
  border: 1px solid #2c2c2c;
  text-align: center;
  cursor: pointer;
  margin-bottom: 5px;
  transition: background-color 0.3s ease;
}

.extra-button:hover {
  background-color: #4a4a4a;
}
</style>

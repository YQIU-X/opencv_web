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
        <img src="../assets/dataIcon.png" alt="按钮1" class="button-icon1" />
      </button>
      <button @click="currentPage = 2" class="connected-button">
        <img src="../assets/crop.png" alt="按钮2" class="button-icon4" />
      </button>
      <button @click="currentPage = 3" class="connected-button">
        <img src="path/to/image2.png" alt="按钮3" class="button-icon" />
      </button>
      <button @click="currentPage = 4" class="connected-button">
        <img src="../assets/bergerIcon.png" alt="按钮4" class="button-icon4" />
      </button>
    </div>
    <!-- 根据 currentPage 显示不同的内容 -->
    <div v-if="currentPage === 1">
      <h3>白平衡</h3>
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
      <h3>色调</h3>
      <div class="slider-container">
        <label>曝光</label>
        <input type="range" min="-100" max="100" v-model="exposure" @input="emitChanges" />
        <span>{{ exposure }}</span>
      </div>
      <div class="slider-container">
        <label>对比</label>
        <input type="range" min="-10" max="10" v-model="contrast" @input="emitChanges" />
        <span>{{ contrast }}</span>
      </div>
      <h3>偏好</h3>
      <div class="slider-container">
        <label>锐化</label>
        <input type="range" min="0" max="100" v-model="sharpen" @input="emitChanges" />
        <span>{{ sharpen }}</span>
      </div>
      <div class="slider-container">
        <label>饱和</label>
        <input type="range" min="-50" max="50" v-model="saturation" @input="emitChanges" />
        <span>{{ saturation }}</span>
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
    <div v-if="currentPage === 4">
      <!-- 手动添加十个按钮 -->
      <div class="button-container">
        <button class="extra-button" @click.stop="setOperation('style-transfer')">样式迁移</button>
        <button class="extra-button" @click.stop="setOperation('image-segmentation')">人像分割</button>
        <button class="extra-button">按钮 3</button>
        <button class="extra-button">按钮 4</button>
        <button class="extra-button">按钮 5</button>
        <button class="extra-button">按钮 6</button>
        <button class="extra-button">按钮 7</button>
        <button class="extra-button">按钮 8</button>
        <button class="extra-button">按钮 9</button>
        <button class="extra-button">按钮 10</button>
      </div>
    </div>
    </div>
    <div class="bottom-button-row">
      <button @click="$emit('undo-action')" class="bottom-button">撤回</button>
      <button @click="confirmChanges" class="bottom-button">确定</button>
      <button @click="$emit('next-image')" class="bottom-button">下一张</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RightSidebar',
  props: {
    temprature: {
      type: Number,
      default: 0
    },
    hue: {
      type: Number,
      default: 0
    },
    exposure: {
      type: Number,
      default: 0
    },
    contrast: {
      type: Number,
      default: 0
    },
    sharpen: {
      type: Number,
      default: 0
    },
    saturation: {
      type: Number,
      default: 0
    },
    Image: {
      type: Object,
      default: null
    }
  },
  data () {
    return {
      histogramImage: '',
      currentPage: 1
    }
  },
  watch: {
    Image: {
      immediate: true,
      handler (newImage) {
        if (newImage && newImage.id) {
          this.fetchHistogram(newImage.id)
        }
      },
      deep: true
    }
  },
  methods: {
    confirmChanges () {
      this.$emit('confirm-changes')
    },
    setOperation (operation) {
      this.operation = operation
      this.$emit('set-operation', operation)
    },
    emitChanges () {
      this.$emit('update-settings', {
        temprature: this.temprature,
        hue: this.hue,
        exposure: this.exposure,
        contrast: this.contrast,
        sharpen: this.sharpen,
        saturation: this.saturation
      })
    },
    fetchHistogram (id) {
      fetch('http://localhost:5003/fetch_histogram', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id: id })
      })
        .then(response => response.json())
        .then(data => {
          this.histogramImage = `data:image/jpeg;base64,${data.image}`
        })
        .catch(error => {
          console.error('Error fetching histogram:', error)
        })
    },
    emitUndoAction () {
      this.$emit('undo-action')
    },
    emitNextImage () {
      this.$emit('next-image')
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
  background-color: #2c2c2c;
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
  align-items: center;
  margin-bottom: 20px;
}

.slider-container label {
  flex: 0 0 50px; /* Set a fixed width for the label */
  font-size: 1em;
  margin-right: 10px; /* Space between label and slider */
}

.slider-container input[type="range"] {
  flex: 1; /* Take up the remaining space */
  margin-right: 10px; /* Space between slider and value */
}

.slider-container span {
  flex: 0 0 30px; /* Set a fixed width for the value */
  font-size: 0.9em;
  text-align: right;
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

.bottom-button-row {
  position: absolute;
  bottom: 0;
  width: 95%; /* 确保按钮占据侧边栏的全部宽度 */
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  background-color: #2c2c2c; /* 设置背景色，以区分按钮和其他部分 */
}

.bottom-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.bottom-button {
  flex: 1;
  padding: 10px;
  background-color: #3a3a3a;
  color: #ffffff;
  border: 1px solid #2c2c2c;
  cursor: pointer;
  text-align: center;
  transition: background-color 0.3s ease;
}

.bottom-button:not(:last-child) {
  margin-right: 10px;
}

.bottom-button:hover {
  background-color: #4a4a4a;
}
</style>

<template>
  <div class="echarts-container" ref="chartRef"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const chartRef = ref(null)
let chart = null

onMounted(() => {
  if (chartRef.value) {
    chart = echarts.init(chartRef.value)
    // 这里可以设置图表的配置项
    const option = {
      title: {
        text: '资金流向图表'
      },
      tooltip: {},
      xAxis: {
        data: []
      },
      yAxis: {},
      series: [{
        name: '流入金额',
        type: 'line',
        data: []
      }]
    }
    chart.setOption(option)
  }
})

onUnmounted(() => {
  if (chart) {
    chart.dispose()
  }
})
</script>

<style scoped>
.echarts-container {
  width: 100%;
  height: 400px;
}
</style> 
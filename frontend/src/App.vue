<script setup>
import { ref } from 'vue';
import EchartsMain from './components/EchartsMain.vue';
import DataTable from './components/DataTable.vue';
import DetailDialog from './components/DetailDialog.vue';
import axios from 'axios';

const flowType = ref('Stock_Flow');
const marketType = ref('');
const period = ref('today');
const pages = ref(1);
const status = ref('');
const chartData = ref([]);
const tableData = ref([]);
const showDialog = ref(false);
const selectedRow = ref(null);
const aiAdvice = ref('');

async function collectData() {
  status.value = '正在采集...';
  try {
    await axios.post('/api/collect', {
      flow_type: flowType.value,
      market_type: marketType.value,
      period: period.value,
      pages: pages.value
    });
    status.value = '采集成功，正在加载数据...';
    setTimeout(loadData, 2000);
  } catch (e) {
    status.value = '采集失败：' + (e.response?.data?.error || e.message);
  }
}

async function loadData() {
  try {
    const resp = await axios.get('/api/flow', {
      params: {
        code: 'all',
        flow_type: flowType.value,
        market_type: marketType.value,
        period: period.value
      }
    });
    chartData.value = resp.data.data;
    tableData.value = Array.isArray(resp.data.data) ? resp.data.data : [resp.data.data];
    status.value = '数据加载成功';
  } catch (e) {
    status.value = '数据加载失败：' + (e.response?.data?.error || e.message);
  }
}

async function showDetail(row) {
  selectedRow.value = row;
  showDialog.value = true;
  aiAdvice.value = '正在分析...';
  try {
    const resp = await axios.post('/api/ai/advice', {
      flow_type: flowType.value,
      market_type: marketType.value,
      period: period.value,
      code: row.code
    });
    aiAdvice.value = resp.data.advice;
  } catch (e) {
    aiAdvice.value = 'AI分析失败：' + (e.response?.data?.error || e.message);
  }
}
</script>

<template>
  <div class="container">
    <h1>资金流智能分析平台</h1>
    <div class="form-row">
      <select v-model="flowType">
        <option value="Stock_Flow">个股资金流</option>
        <option value="Sector_Flow">板块资金流</option>
      </select>
      <input v-model="marketType" placeholder="市场/板块/行业/概念" style="width:160px" />
      <select v-model="period">
        <option value="today">今日</option>
        <option value="3d">3日</option>
        <option value="5d">5日</option>
        <option value="10d">10日</option>
      </select>
      <input v-model.number="pages" type="number" min="1" max="10" style="width:60px" />
      <button @click="collectData">采集数据</button>
    </div>
    <div class="status">{{ status }}</div>
    <EchartsMain :chartData="chartData" />
    <DataTable :rows="tableData" @row-click="showDetail" />
    <DetailDialog v-if="showDialog" :row="selectedRow" :advice="aiAdvice" @close="showDialog=false" />
  </div>
</template>

<style scoped>
.container { max-width: 1000px; margin: 40px auto; background: #fff; border-radius: 12px; box-shadow: 0 2px 16px #e0e0e0; padding: 32px; }
h1 { text-align: center; color: #2d3a4b; }
.form-row { display: flex; gap: 16px; flex-wrap: wrap; justify-content: center; margin-bottom: 24px; }
.status { margin-bottom: 16px; color: #888; text-align: center; }
</style>

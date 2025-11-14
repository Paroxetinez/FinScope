<template>
  <div class="stock-analysis-container">
    <h1>Stock Analysis</h1>
    <div class="content-wrapper">
      <div class="main-content">
        <!-- 1. Stock Analysis Module -->
        <section id="stockAnalysis">
          <a-card>
            <template #title>
              <StockOutlined /> Microsoft Corporation (MSFT)
            </template>
            <template #extra>
              <a-space>
                <a-tag color="blue">NASDAQ</a-tag>
                <span style="color: grey">Updated at 2024-01-18 05:00 GMT+8</span>
              </a-space>
            </template>
            <a-row>
              <a-col :span="12">
                <a-descriptions :column="1" class="custom-descriptions">
                  <a-descriptions-item>
                    <a-statistic
                      title="Current Price"
                      value="429.03"
                      :precision="2"
                      prefix="$"
                      :value-style="{ color: '#3f8600' }"
                    >
                      <template #suffix>
                        <span style="font-size: 14px; margin-left: 8px">
                          <a-tag color="success">+1.05% (+$4.45)</a-tag>
                        </span>
                      </template>
                    </a-statistic>
                  </a-descriptions-item>
                  <a-descriptions-item>
                    <a-statistic
                      title="After Hours"
                      value="+0.11%"
                      :value-style="{ color: '#3f8600' }"
                      prefix="+"
                      suffix="$0.47"
                    />
                  </a-descriptions-item>
                </a-descriptions>
              </a-col>
              <a-col :span="12">
                <div class="time-range-selector">
                  <a-radio-group v-model:value="timeRange" size="middle" button-style="solid">
                    <a-radio-button value="1D">1D</a-radio-button>
                    <a-radio-button value="5D">5D</a-radio-button>
                    <a-radio-button value="1M">1M</a-radio-button>
                    <a-radio-button value="3M">3M</a-radio-button>
                    <a-radio-button value="6M">6M</a-radio-button>
                    <a-radio-button value="1Y">1Y</a-radio-button>
                  </a-radio-group>
                </div>
              </a-col>
            </a-row>
            <div id="container" style="margin-top: 40px;"></div>
          </a-card>
        </section>

        <!-- 2. Market Overview Module -->
        <section id="marketOverview">
          <a-card>
            <template #title>
              <BarChartOutlined /> Market Overview
            </template>
            <a-row :gutter="16">
              <a-col :span="8">
                <a-statistic
                  title="Market Cap"
                  value="3.2"
                  suffix="T USD"
                >
                  <template #prefix>
                    <span style="font-size: 14px; color: #52c41a">+1.05% </span>
                  </template>
                </a-statistic>
              </a-col>
              <a-col :span="8">
                <a-statistic
                  title="P/E Ratio"
                  value="35"
                  suffix="TTM"
                />
              </a-col>
              <a-col :span="8">
                <a-statistic
                  title="Volume"
                  value="25.26"
                  suffix="M"
                >
                  <template #prefix>
                    <span style="font-size: 14px; color: #52c41a">+2.91% </span>
                  </template>
                </a-statistic>
              </a-col>
            </a-row>
          </a-card>
        </section>

        <!-- 3. Earnings Module -->
        <section id="earnings">
          <a-card>
            <template #title>
              <BarChartOutlined /> Earnings
            </template>
            <a-row :gutter="[24, 24]">
              <a-col :span="8">
                <a-card size="small" title="Report Info">
                  <a-descriptions :column="1" size="small">
                    <a-descriptions-item label="Report Date">2025-01-29</a-descriptions-item>
                    <a-descriptions-item label="Report Period">Q2 2025</a-descriptions-item>
                  </a-descriptions>
                </a-card>
              </a-col>
              <a-col :span="8">
                <a-card size="small" title="Revenue & EPS">
                  <a-descriptions :column="1" size="small">
                    <a-descriptions-item label="Rev Estimate">688.6亿</a-descriptions-item>
                    <a-descriptions-item label="EPS Estimate">3.13</a-descriptions-item>
                  </a-descriptions>
                </a-card>
              </a-col>
              <a-col :span="8">
                <a-card size="small" title="Market Movement">
                  <a-descriptions :column="1" size="small">
                    <a-descriptions-item label="Avg 1d Change">
                      <span style="color: #52c41a">+2.91%</span>
                    </a-descriptions-item>
                    <a-descriptions-item label="Implied Move 1d">
                      <span style="color: #1890ff">4.02%</span>
                    </a-descriptions-item>
                  </a-descriptions>
                </a-card>
              </a-col>
            </a-row>
          </a-card>
        </section>

        <!-- 4. Relevant Peers Module -->
        <section id="relevantPeers">
          <a-card>
            <template #title>
              <TeamOutlined /> Relevant Companies
            </template>
            <a-row :gutter="[16, 16]">
              <a-col :span="8">
                <a-card hoverable>
                  <template #title>
                    PANW
                    <a-tag color="blue" style="margin-left: 8px">Palo Alto Networks</a-tag>
                  </template>
                  <a-statistic
                    value="177.11"
                    :precision="2"
                    prefix="$"
                    :value-style="{ color: '#3f8600' }"
                  >
                    <template #suffix>
                      <a-tag color="success">+0.03%</a-tag>
                    </template>
                  </a-statistic>
                </a-card>
              </a-col>
              <a-col :span="8">
                <a-card hoverable>
                  <template #title>
                    ADBE
                    <a-tag color="blue" style="margin-left: 8px">Adobe Inc.</a-tag>
                  </template>
                  <a-statistic
                    value="429.99"
                    :precision="2"
                    prefix="$"
                    :value-style="{ color: '#3f8600' }"
                  >
                    <template #suffix>
                      <a-tag color="success">+0.72%</a-tag>
                    </template>
                  </a-statistic>
                </a-card>
              </a-col>
              <a-col :span="8">
                <a-card hoverable>
                  <template #title>
                    ORCL
                    <a-tag color="blue" style="margin-left: 8px">Oracle</a-tag>
                  </template>
                  <a-statistic
                    value="161.03"
                    :precision="2"
                    prefix="$"
                    :value-style="{ color: '#3f8600' }"
                  >
                    <template #suffix>
                      <a-tag color="success">+0.93%</a-tag>
                    </template>
                  </a-statistic>
                </a-card>
              </a-col>
            </a-row>
          </a-card>
        </section>

        <!-- 5. Technical Analysis Module -->
        <section id="technicalAnalysis">
          <a-card>
            <template #title>
              <FundOutlined /> Technical Analysis
            </template>
            <a-row :gutter="[16, 16]">
              <a-col :span="12">
                <div id="macdChart" style="height: 250px;"></div>
              </a-col>
              <a-col :span="12">
                <div id="rsiChart" style="height: 250px;"></div>
              </a-col>
            </a-row>
            <a-row :gutter="[16, 16]" style="margin-top: 16px;">
              <a-col :span="8">
                <a-card size="small" title="MACD">
                  <a-descriptions :column="1" size="small">
                    <a-descriptions-item label="MACD">12.45</a-descriptions-item>
                    <a-descriptions-item label="Signal">9.78</a-descriptions-item>
                    <a-descriptions-item label="Histogram">2.67</a-descriptions-item>
                  </a-descriptions>
                </a-card>
              </a-col>
              <a-col :span="8">
                <a-card size="small" title="RSI">
                  <a-descriptions :column="1" size="small">
                    <a-descriptions-item label="RSI(14)">65.32</a-descriptions-item>
                    <a-descriptions-item label="Status">Neutral</a-descriptions-item>
                  </a-descriptions>
                </a-card>
              </a-col>
              <a-col :span="8">
                <a-card size="small" title="Moving Average">
                  <a-descriptions :column="1" size="small">
                    <a-descriptions-item label="MA(20)">423.45</a-descriptions-item>
                    <a-descriptions-item label="MA(50)">415.67</a-descriptions-item>
                    <a-descriptions-item label="MA(200)">398.89</a-descriptions-item>
                  </a-descriptions>
                </a-card>
              </a-col>
            </a-row>
          </a-card>
        </section>

        <!-- 6. Financial Statements Module -->
        <section id="financialStatements">
          <a-card>
            <template #title>
              <AccountBookOutlined /> Financial Statements
            </template>
            <a-tabs>
              <a-tab-pane key="1" tab="Income Statement">
                <div id="incomeStatementChart" style="height: 300px;"></div>
                <a-table
                  :columns="incomeStatementColumns"
                  :data-source="incomeStatementData"
                  :pagination="false"
                  size="small"
                  style="margin-top: 20px;"
                />
              </a-tab-pane>
              <a-tab-pane key="2" tab="Cash Flow">
                <div id="cashFlowChart" style="height: 300px;"></div>
                <a-table
                  :columns="cashFlowColumns"
                  :data-source="cashFlowData"
                  :pagination="false"
                  size="small"
                  style="margin-top: 20px;"
                />
              </a-tab-pane>
              <a-tab-pane key="3" tab="Balance Sheet">
                <div id="balanceSheetChart" style="height: 300px;"></div>
                <a-table
                  :columns="balanceSheetColumns"
                  :data-source="balanceSheetData"
                  :pagination="false"
                  size="small"
                  style="margin-top: 20px;"
                />
              </a-tab-pane>
            </a-tabs>
          </a-card>
        </section>

        <!-- 7. News and Analysis Module -->
        <section id="newsAnalysis">
          <a-card>
            <template #title>
              <ReadOutlined /> News and Analysis
            </template>
            <a-tabs>
              <a-tab-pane key="1" tab="Latest News">
                <a-list
                  :data-source="[
                    {
                      title: 'Microsoft股票创近五个月新高，表现超越大盘',
                      source: 'Market Analysis',
                      date: '2025-01-18',
                      summary: '微软股票近期表现强劲，自2025年1月以来上涨22.5%，远超标普500的16%涨幅。公司在人工智能、云计算等领域持续发力，市场价值达到3.42万亿美元。分析显示，微软的高股本回报率和低负债率成为其投资亮点。',
                      sentiment: 'positive'
                    },
                    {
                      title: '微软1月安全更新修复159个漏洞，包括10个关键RCE',
                      source: 'Tech News',
                      date: '2025-01-14',
                      summary: '微软发布了2025年1月的安全更新，共修复159个漏洞，其中10个为关键远程代码执行漏洞。这些漏洞涉及Excel、远程桌面服务等，可能导致系统被攻击者控制。微软建议用户尽快更新以防范潜在风险。',
                      sentiment: 'negative'
                    },
                    {
                      title: '微软365将为消费者推出Copilot功能',
                      source: 'Company News',
                      date: '2025-01-15',
                      summary: '微软宣布将于2025年为消费者版Microsoft 365引入Copilot功能，此举旨在提升用户效率并增强创造力。Copilot的加入标志着微软在人工智能领域的进一步布局，为用户提供更智能的软件体验。',
                      sentiment: 'positive'
                    }
                  ]"
                  item-layout="vertical"
                  size="large"
                >
                  <template #renderItem="{ item }">
                    <a-list-item>
                      <template #extra>
                        <a-tag :color="item.sentiment === 'positive' ? 'success' : item.sentiment === 'negative' ? 'error' : 'default'">
                          {{ item.sentiment === 'positive' ? 'Positive' : item.sentiment === 'negative' ? 'Negative' : 'Neutral' }}
                        </a-tag>
                      </template>
                      <a-list-item-meta
                        :title="item.title"
                        :description="item.source + ' · ' + item.date"
                      />
                      {{ item.summary }}
                    </a-list-item>
                  </template>
                </a-list>
              </a-tab-pane>
            </a-tabs>
          </a-card>
        </section>

        <!-- 8. Dynamic Feeds Module -->
        <section id="dynamicFeeds">
          <a-card style="margin-top: 20px;">
            <a-row>
              <a-col :span="18">
                <p style="font-weight: bold;"><ReadOutlined /> &nbsp;&nbsp;Latest Updates</p>
              </a-col>
              <a-col :span="6" style="display: flex; justify-content: right;color: grey;">
                Updated 2 minutes ago
              </a-col>
            </a-row>
            <a-card style="margin-top: 20px;">
              <a-row>
                <a-col :span="18">
                  <p style="font-size: 16px; font-weight: bold;">Microsoft Expands AI Infrastructure Investment</p>
                </a-col>
                <a-col :span="6" style="display: flex; justify-content: right;">
                  <RightOutlined />
                </a-col>
              </a-row>
              <p>Microsoft announced plans to invest significantly in expanding its AI infrastructure over the next three years, demonstrating its commitment to maintaining leadership in the AI space.</p>
              <p>January 18, 2025</p>
            </a-card>
          </a-card>
        </section>
      </div>

      <!-- Sidebar -->
      <div class="sidebar">
        <a-anchor
          :items="[
            { key: 'stockAnalysis', href: '#stockAnalysis', title: 'Stock Analysis' },
            { key: 'marketOverview', href: '#marketOverview', title: 'Market Overview' },
            { key: 'earnings', href: '#earnings', title: 'Earnings' },
            { key: 'relevantPeers', href: '#relevantPeers', title: 'Relevant Peers' },
            { key: 'technicalAnalysis', href: '#technicalAnalysis', title: 'Technical Analysis' },
            { key: 'financialStatements', href: '#financialStatements', title: 'Financial Statements' },
            { key: 'newsAnalysis', href: '#newsAnalysis', title: 'News & Analysis' },
            { key: 'dynamicFeeds', href: '#dynamicFeeds', title: 'Dynamic Feeds' }
          ]"
          @click="handleAnchorClick"
        />
      </div>
    </div>
  </div>
</template>

<script lang="tsx">
import { defineComponent, onMounted, ref, nextTick, h } from 'vue';
import { Line, Column, DualAxes } from '@antv/g2plot';
import DataSet from '@antv/data-set';
import { 
  BarChartOutlined, 
  FundOutlined, 
  ProfileOutlined,
  StockOutlined,
  ReadOutlined,
  RightOutlined,
  DownOutlined,
  TeamOutlined,
  AccountBookOutlined
} from '@ant-design/icons-vue';
import type { Options as DualAxesOptions } from '@antv/g2plot/lib/plots/dual-axes';

interface MenuInfo {
  key: string;
}

interface AnchorLink {
  href: string;
}

interface CustomRenderProps {
  text: string;
}

interface StockData {
  date: string;
  price: number;
  volume: number;
  ma5: number;
  ma20: number;
}

interface GeometryTooltipConfig {
  formatter: (datum: StockData) => { name: string; value: string };
}

interface CustomGeometryOption {
  geometry: string;
  smooth?: boolean;
  color?: string;
  lineStyle?: {
    lineWidth: number;
  };
  point?: {
    size: number;
    shape: string;
    style: {
      fill: string;
      stroke: string;
      lineWidth: number;
    };
  };
  tooltip?: GeometryTooltipConfig;
}

export default defineComponent({
  components: {
    BarChartOutlined,
    FundOutlined,
    ProfileOutlined,
    StockOutlined,
    ReadOutlined,
    RightOutlined,
    DownOutlined,
    TeamOutlined,
    AccountBookOutlined
  },
  setup() {
    const timeRange = ref('week');
    const chartContainer = ref(null);
    const macdChartContainer = ref(null);
    const analystsChartContainer = ref(null);
    
    const handleMenuClick = (menuInfo: MenuInfo) => {
      console.log('menu clicked', menuInfo);
      timeRange.value = menuInfo.key.charAt(0).toUpperCase() + menuInfo.key.slice(1);
    };

    const handleAnchorClick = (e: Event, link: AnchorLink) => {
      e.preventDefault();
      const targetElement = document.querySelector(link.href);
      if (targetElement) {
        targetElement.scrollIntoView({ behavior: 'smooth' });
      }
    };

    const customRender = ({ text }: CustomRenderProps) => {
      const value = parseFloat(text);
      return {
        props: {
          style: { color: value >= 0 ? '#52c41a' : '#f5222d' }
        },
        children: `${value >= 0 ? '+' : ''}${text}%`
      };
    };

    // Income Statement Data
    const incomeStatementColumns = ref([
      { title: 'Year', dataIndex: 'year', key: 'year' },
      { title: 'Revenue', dataIndex: 'revenue', key: 'revenue' },
      { title: 'Cost of Revenue', dataIndex: 'costOfRevenue', key: 'costOfRevenue' },
      { title: 'Gross Profit', dataIndex: 'grossProfit', key: 'grossProfit' },
      { title: 'Gross Profit %', dataIndex: 'grossProfitMargin', key: 'grossProfitMargin' },
      { title: 'R&D Expenses', dataIndex: 'rdExpenses', key: 'rdExpenses' }
    ]);

    const incomeStatementData = ref([
      {
        key: '2024',
        year: '2024',
        revenue: 'US$2451亿',
        costOfRevenue: 'US$741亿',
        grossProfit: 'US$1710亿',
        grossProfitMargin: '70%',
        rdExpenses: 'US$295亿'
      },
      {
        key: '2023',
        year: '2023',
        revenue: 'US$2119亿',
        costOfRevenue: 'US$659亿',
        grossProfit: 'US$1461亿',
        grossProfitMargin: '69%',
        rdExpenses: 'US$272亿'
      },
      {
        key: '2022',
        year: '2022',
        revenue: 'US$1983亿',
        costOfRevenue: 'US$627亿',
        grossProfit: 'US$1356亿',
        grossProfitMargin: '68%',
        rdExpenses: 'US$245亿'
      },
      {
        key: '2021',
        year: '2021',
        revenue: 'US$1681亿',
        costOfRevenue: 'US$522亿',
        grossProfit: 'US$1159亿',
        grossProfitMargin: '69%',
        rdExpenses: 'US$207亿'
      },
      {
        key: '2020',
        year: '2020',
        revenue: 'US$1430亿',
        costOfRevenue: 'US$461亿',
        grossProfit: 'US$969亿',
        grossProfitMargin: '68%',
        rdExpenses: 'US$193亿'
      }
    ]);

    // Cash Flow Data
    const cashFlowColumns = ref([
      { title: 'Year', dataIndex: 'year', key: 'year' },
      { title: 'Net Income', dataIndex: 'netIncome', key: 'netIncome' },
      { title: 'Dep. & Amort.', dataIndex: 'depAndAmort', key: 'depAndAmort' },
      { title: 'Def. Tax', dataIndex: 'defTax', key: 'defTax' },
      { title: 'Stock Comp.', dataIndex: 'stockComp', key: 'stockComp' },
      { title: 'Chg. in WC', dataIndex: 'chgInWc', key: 'chgInWc' }
    ]);

    const cashFlowData = ref([
      {
        key: '2024',
        year: '2024',
        netIncome: 'US$881亿',
        depAndAmort: 'US$223亿',
        defTax: '-US$47亿',
        stockComp: 'US$107亿',
        chgInWc: 'US$18亿'
      },
      {
        key: '2023',
        year: '2023',
        netIncome: 'US$724亿',
        depAndAmort: 'US$139亿',
        defTax: '-US$61亿',
        stockComp: 'US$96亿',
        chgInWc: '-US$24亿'
      },
      {
        key: '2022',
        year: '2022',
        netIncome: 'US$727亿',
        depAndAmort: 'US$145亿',
        defTax: '-US$57亿',
        stockComp: 'US$75亿',
        chgInWc: 'US$4.5亿'
      },
      {
        key: '2021',
        year: '2021',
        netIncome: 'US$613亿',
        depAndAmort: 'US$117亿',
        defTax: '-US$1.5亿',
        stockComp: 'US$61亿',
        chgInWc: '-US$9.4亿'
      },
      {
        key: '2020',
        year: '2020',
        netIncome: 'US$443亿',
        depAndAmort: 'US$128亿',
        defTax: '-US$36亿',
        stockComp: 'US$53亿',
        chgInWc: 'US$21亿'
      }
    ]);

    // Balance Sheet Data
    const balanceSheetColumns = ref([
      { title: 'Year', dataIndex: 'year', key: 'year' },
      { title: 'Cash', dataIndex: 'cash', key: 'cash' },
      { title: 'ST Investments', dataIndex: 'stInvestments', key: 'stInvestments' },
      { title: 'Cash & ST Inv.', dataIndex: 'cashAndStInv', key: 'cashAndStInv' },
      { title: 'Receivables', dataIndex: 'receivables', key: 'receivables' },
      { title: 'Inventory', dataIndex: 'inventory', key: 'inventory' }
    ]);

    const balanceSheetData = ref([
      {
        key: '2024',
        year: '2024',
        cash: 'US$183亿',
        stInvestments: 'US$572亿',
        cashAndStInv: 'US$755亿',
        receivables: 'US$569亿',
        inventory: 'US$12亿'
      },
      {
        key: '2023',
        year: '2023',
        cash: 'US$347亿',
        stInvestments: 'US$766亿',
        cashAndStInv: 'US$1113亿',
        receivables: 'US$487亿',
        inventory: 'US$25亿'
      },
      {
        key: '2022',
        year: '2022',
        cash: 'US$139亿',
        stInvestments: 'US$908亿',
        cashAndStInv: 'US$1047亿',
        receivables: 'US$443亿',
        inventory: 'US$37亿'
      },
      {
        key: '2021',
        year: '2021',
        cash: 'US$142亿',
        stInvestments: 'US$1160亿',
        cashAndStInv: 'US$1303亿',
        receivables: 'US$380亿',
        inventory: 'US$26亿'
      },
      {
        key: '2020',
        year: '2020',
        cash: 'US$136亿',
        stInvestments: 'US$1229亿',
        cashAndStInv: 'US$1365亿',
        receivables: 'US$320亿',
        inventory: 'US$19亿'
      }
    ]);

    // 股票数据
    const stockData = ref<StockData[]>([
      {
        date: '2024-01-18',
        price: 429.03,
        volume: 25.26,
        ma5: 428.50,
        ma20: 425.75
      },
      { date: '2023-12', price: 427.12, volume: 24.85, ma5: 424.56, ma20: 422.78 },
      { date: '2023-11', price: 425.89, volume: 23.92, ma5: 423.89, ma20: 421.95 },
      { date: '2023-10', price: 423.45, volume: 22.78, ma5: 422.67, ma20: 420.85 },
      { date: '2023-09', price: 420.78, volume: 21.95, ma5: 421.34, ma20: 419.76 },
      { date: '2023-08', price: 418.92, volume: 20.85, ma5: 420.12, ma20: 418.89 },
      { date: '2023-07', price: 415.67, volume: 19.76, ma5: 418.89, ma20: 417.92 },
      { date: '2023-06', price: 412.85, volume: 18.89, ma5: 417.56, ma20: 416.85 },
      { date: '2023-05', price: 410.23, volume: 17.92, ma5: 416.34, ma20: 415.78 },
      { date: '2023-04', price: 408.56, volume: 16.85, ma5: 415.12, ma20: 414.67 },
      { date: '2023-03', price: 405.89, volume: 15.78, ma5: 413.89, ma20: 413.45 },
      { date: '2023-02', price: 403.45, volume: 14.67, ma5: 412.67, ma20: 412.34 }
    ]);

    onMounted(() => {
      nextTick(() => {
        try {
          if (document.getElementById('container')) {
            const dualAxes = new DualAxes('container', {
              data: [stockData.value, stockData.value],
              xField: 'date',
              yField: ['price', 'volume'],
              geometryOptions: [
                {
                  geometry: 'line',
                  smooth: true,
                  color: '#2196F3',
                  lineStyle: {
                    lineWidth: 2,
                  },
                  point: {
                    size: 3,
                    shape: 'circle',
                    style: {
                      fill: '#2196F3',
                      stroke: '#fff',
                      lineWidth: 2,
                    },
                  },
                  tooltip: {
                    formatter: (datum: StockData) => {
                      return { name: '股价', value: `$${datum.price}` };
                    },
                  },
                } as CustomGeometryOption,
                {
                  geometry: 'column',
                  color: '#E0E0E0',
                  tooltip: {
                    formatter: (datum: StockData) => {
                      return { name: '成交量', value: `${datum.volume}M` };
                    },
                  },
                } as CustomGeometryOption,
              ],
              annotations: {
                price: [
                  {
                    type: 'line',
                    start: ['min', 'mean'],
                    end: ['max', 'mean'],
                    style: {
                      stroke: '#F5222D',
                      lineDash: [4, 4],
                    },
                  },
                ],
              },
              meta: {
                price: {
                  alias: '股价',
                  formatter: (v) => `$${v}`,
                },
                volume: {
                  alias: '成交量',
                  formatter: (v) => `${v}M`,
                },
              },
              xAxis: {
                type: 'time',
                tickCount: 6,
                grid: {
                  line: {
                    style: {
                      stroke: '#E8E8E8',
                      lineWidth: 1,
                      lineDash: [4, 4],
                    },
                  },
                },
              },
              yAxis: {
                price: {
                  grid: {
                    line: {
                      style: {
                        stroke: '#E8E8E8',
                        lineWidth: 1,
                        lineDash: [4, 4],
                      },
                    },
                  },
                },
                volume: false,
              },
              legend: {
                position: 'top-right',
              },
              animation: {
                appear: {
                  animation: 'fade-in',
                },
              },
            });
            dualAxes.render();
          }
        } catch (error) {
          console.error('Error initializing charts:', error);
        }
      });
    });

    return {
      timeRange,
      handleMenuClick,
      handleAnchorClick,
      customRender,
      incomeStatementColumns,
      incomeStatementData,
      cashFlowColumns,
      cashFlowData,
      balanceSheetColumns,
      balanceSheetData,
      chartContainer,
      macdChartContainer,
      analystsChartContainer,
    };
  },
});
</script>

<style scoped>
.stock-analysis-container {
  padding: 16px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

.stock-analysis-container h1 {
  margin: -30px 0 16px 0;
  font-size: 24px;
  line-height: 1.4;
  color: rgba(0, 0, 0, 0.85);
}

.content-wrapper {
  display: flex;
  gap: 30px;
  position: relative;
  width: 100%;
}

.main-content {
  flex: 1;
  min-width: 0;
  max-width: 75%;
}

.main-content section {
  margin-bottom: 24px;
}

.main-content section:last-child {
  margin-bottom: 0;
}

:deep(.ant-card) {
  margin-bottom: 0;
}

.sidebar {
  position: sticky;
  top: 20px;
  height: fit-content;
  width: 200px;
  flex-shrink: 0;
  margin-left: auto;
}

@media (min-width: 1024px) {
  .stock-analysis-container {
    padding: 45px 40px;
  }

  .main-content {
    max-width: calc(100% - 230px);
  }
}

@media (max-width: 1024px) {
  .content-wrapper {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    margin-top: 20px;
    position: static;
  }

  .main-content {
    max-width: 100%;
  }
}

@media (max-width: 768px) {
  .stock-analysis-container {
    padding: 10px;
  }
}

.custom-descriptions :deep(.ant-descriptions-item) {
  margin-bottom: 6px;
  padding-bottom: 0;
}

.custom-descriptions :deep(.ant-descriptions-item-content) {
  font-size: 14px;
}

.market-stat {
  padding: 16px;
  text-align: center;
}

.stat-label {
  color: rgba(0, 0, 0, 0.45);
  font-size: 14px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  margin: 8px 0;
}

.stat-change {
  font-size: 14px;
}

.positive {
  color: #52c41a;
}

.negative {
  color: #f5222d;
}

.neutral {
  color: #faad14;
}

:deep(.ant-tabs-tab) {
  font-size: 14px;
}

:deep(.ant-descriptions-item-label) {
  color: rgba(0, 0, 0, 0.65);
}

/* 添加平滑滚动效果 */
html {
  scroll-behavior: smooth;
}

/* 确保锚点定位正确 */
section {
  scroll-margin-top: 20px;
}

.ant-dropdown-link {
  cursor: pointer;
  color: #1890ff;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.time-range-button {
  min-width: 100px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* 统一卡片内容的间距 */
:deep(.ant-card-body) {
  padding: 24px;
}

/* 统一表格的间距 */
:deep(.ant-table-wrapper) {
  margin: 0;
}

/* 统一标签页的间距 */
:deep(.ant-tabs-content) {
  padding-top: 16px;
}

/* 统一描述列表的间距 */
:deep(.ant-descriptions) {
  padding: 0;
}

/* 统一统计数据的间距 */
:deep(.ant-statistic) {
  margin: 0;
}

/* 统一行间距 */
:deep(.ant-row) {
  margin-bottom: 16px;
}

:deep(.ant-row:last-child) {
  margin-bottom: 0;
}

.time-range-selector {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 8px 0;
}

:deep(.ant-radio-group) {
  display: flex;
  gap: 1px;
}

:deep(.ant-radio-button-wrapper) {
  height: 32px;
  padding: 0 16px;
  font-size: 14px;
  line-height: 30px;
  border-color: #d9d9d9;
  background: #fff;
  color: rgba(0, 0, 0, 0.65);
}

:deep(.ant-radio-button-wrapper:first-child) {
  border-radius: 6px 0 0 6px;
}

:deep(.ant-radio-button-wrapper:last-child) {
  border-radius: 0 6px 6px 0;
}

:deep(.ant-radio-button-wrapper-checked) {
  color: #1890ff;
  background: #e6f4ff;
  border-color: #1890ff;
  box-shadow: -1px 0 0 0 #1890ff;
}

:deep(.ant-radio-button-wrapper:hover) {
  color: #1890ff;
  border-color: #1890ff;
  position: relative;
  z-index: 1;
}

/* 添加earnings section的样式 */
.ant-card-small .ant-descriptions-item-label {
  color: rgba(0, 0, 0, 0.45);
  font-size: 12px;
}

.ant-card-small .ant-descriptions-item-content {
  font-size: 14px;
  font-weight: 500;
}

#earnings .ant-card-head-title {
  font-size: 16px;
  font-weight: 500;
}

#earnings .ant-card-small {
  background: #fafafa;
}

#earnings .ant-card-small .ant-card-head {
  min-height: 36px;
  padding: 0 12px;
  font-size: 14px;
}

#earnings .ant-card-small .ant-card-body {
  padding: 12px;
}
</style>
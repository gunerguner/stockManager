<template>
  <div class="home">
    <el-row display="margin-top:10px"></el-row>
    <el-row style="margin-bottom: 20px">
      <el-table :data="overall" style="width: 100%" border :cell-style="overallCellStyle">
        <el-table-column prop="offsetToday" label="当日盈亏">
          <template slot-scope="scope">{{scope.row.offsetToday.toFixed(2)}}</template>
        </el-table-column>
        <el-table-column prop="offsetCurrent" label="浮动盈亏">
          <template
            slot-scope="scope"
          >{{scope.row.offsetCurrent.toFixed(2)+" (" + scope.row.offsetCurrentRatio + ")"}}</template>
        </el-table-column>
        <el-table-column prop="offsetTotal" label="累计盈亏">
          <template slot-scope="scope">{{scope.row.offsetTotal.toFixed(2)}}</template>
        </el-table-column>
        <el-table-column prop="totalValue" label="市值">
          <template slot-scope="scope">{{scope.row.totalValue.toFixed(2)}}</template>
        </el-table-column>
        <el-table-column label="总资产">
          <template slot-scope="scope">{{(scope.row.totalCash+scope.row.totalValue).toFixed(2)}}</template>
        </el-table-column>
        <el-table-column prop="totalCash" label="现金">
          <template slot-scope="scope">{{scope.row.totalCash.toFixed(2)}}</template>
        </el-table-column>
        <el-table-column prop="originCashStr" label="本金">
          <template slot-scope="scope">{{scope.row.originCash.toFixed(2)}}</template>
        </el-table-column>
      </el-table>
    </el-row>
    <el-row type="flex" style="margin-bottom: 20px" justify="end">
      <el-button @click="resetHide" style="margin-right: 20px">{{hideStr}}市值为零的股票</el-button>
    </el-row>
    <el-row>
      <el-table
        :data="stockList"
        style="width: 100%"
        border
        :cell-style="stockCellStyle"
        :row-style="stockRowStyle"
      >
        <el-table-column type="expand">
          <template slot-scope="props">
            <el-table
              :data="props.row.operationList"
              style="width: 100%"
              border
              :cell-style="{'font-size': '10px','padding':'0px'}"
              :row-style="{'height':'40px'}"
            >
              <el-table-column label="交易日期" prop="date"></el-table-column>
              <el-table-column label="类型" prop="type">
                <template
                  slot-scope="scope"
                >{{(scope.row.type == 'BUY')?'买入':((scope.row.type == 'SELL')?'卖出':'除权除息')}}</template>
              </el-table-column>
              <el-table-column label="成交价" prop="price"></el-table-column>
              <el-table-column label="数量" prop="count"></el-table-column>
              <el-table-column label="佣金" prop="fee">
                <template slot-scope="scope">{{scope.row.fee.toFixed(2)}}</template>
              </el-table-column>
              <el-table-column label="成交金额" prop="sum">
                <template slot-scope="scope">{{scope.row.sum.toFixed(2)}}</template>
              </el-table-column>
              <el-table-column label="说明" prop="comment"></el-table-column>
            </el-table>
          </template>
        </el-table-column>
        <el-table-column label="名称">
          <template slot-scope="scope">
            <a
              :href="'https://xueqiu.com/S/'+scope.row.code"
              target="_blank"
              style="text-decoration: none;color:black; font-weight: bold;"
            >{{scope.row.name+ " (" + scope.row.code + ")"}}</a>
          </template>
        </el-table-column>
        <el-table-column prop="priceNow" label="现价"></el-table-column>
        <el-table-column prop="offsetToday" label="涨跌">
          <template
            slot-scope="scope"
          >{{scope.row.offsetToday.toFixed(3) + " (" + scope.row.offsetTodayRatio + ")"}}</template>
        </el-table-column>
        <el-table-column prop="totalValue" label="市值" sortable>
          <template slot-scope="scope">{{scope.row.totalValue.toFixed(2)}}</template>
        </el-table-column>
        <el-table-column prop="holdCount" label="持仓"></el-table-column>
        <el-table-column prop="overallCost" label="摊薄成本/持仓成本">
          <template
            slot-scope="scope"
          >{{scope.row.overallCost.toFixed(2) + " / " + scope.row.holdCost.toFixed(2)}}</template>
        </el-table-column>
        <el-table-column prop="offsetCurrent" label="浮动盈亏" sortable>
          <template
            slot-scope="scope"
          >{{scope.row.offsetCurrent.toFixed(2) + " (" + scope.row.offsetCurrentRatio + ")"}}</template>
        </el-table-column>
        <el-table-column prop="offsetTotal" label="累计盈亏" sortable>
          <template slot-scope="scope">{{scope.row.offsetTotal.toFixed(2)}}</template>
        </el-table-column>
      </el-table>
    </el-row>
  </div>
</template>

<script>
export default {
  /* eslint-disable */
  name: "home",
  data() {
    return {
      stockList: [],
      overall: [],
      hideState: true,
      hideStr: "显示"
    };
  },
  mounted: function() {
    this.showStocks();
  },
  methods: {
    showStocks() {
      this.$axios.get("http://127.0.0.1:8000/api/").then(res => {
        var response = res.data;
        this.stockList = response.stocks;
        this.stockList.sort(function(a, b) {
          return b["totalValue"] - a["totalValue"];
        });
        this.overall.push(response.overall);
      });
    },
    stockCellStyle({ row, column, rowIndex, columnIndex }) {
      if (columnIndex === 2) {
        return this.cellStyle(row["offsetToday"]);
      }
      if (columnIndex === 7) {
        return this.cellStyle(row["offsetCurrent"]);
      }
      if (columnIndex === 8) {
        return this.cellStyle(row["offsetTotal"]);
      }
    },
    overallCellStyle({ row, column, rowIndex, columnIndex }) {
      if (columnIndex === 0) {
        return this.cellStyle(row["offsetToday"]);
      }
      if (columnIndex === 1) {
        return this.cellStyle(row["offsetCurrent"]);
      }
      if (columnIndex === 2) {
        return this.cellStyle(row["offsetTotal"]);
      }
    },
    cellStyle(value) {
      if (value == 0) {
        return "color: black;";
      } else if (value > 0) {
        return "color: red;";
      } else {
        return "color: green;";
      }
    },
    stockRowStyle({ row, rowIndex }) {
      if (row["totalValue"] < 0.1 && this.hideState) {
        return { display: "none" };
      }
    },
    resetHide() {
      this.hideState = !this.hideState;
      this.hideStr = this.hideState ? "显示" : "隐藏";
    },
    sortTotalValue(obj1, obj2) {
      return parseFloat(obj1) < parseFloat(obj2);
    }
  }
};
</script>
<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>

import { tradeAmountCny } from '@/utils/format/stock';

export type CostPeriodType = 'year' | 'month';

export interface CostListModel {
  id: string;
  type: CostPeriodType;
  // ── 交易活跃（次数） ──
  normalTradeCount: number; // 普通交易 BUY+SELL 笔数（非 CONV、非 DV）
  convTradeCount: number; // 可转债 BUY+SELL 笔数（CONV、非 DV）
  dividendCount: number; // 除权除息 DV 笔数
  // ── 资金动向（金额，均为人民币 CNY）──
  buyAmount: number; // 所有 BUY 人民币成交额合计
  sellAmount: number; // 所有 SELL 人民币成交额合计
  cashFlow: number; // cashFlowList.amount 合计（正入负出）
  fee: number; // fee 合计（人民币）
  subList?: CostListModel[]; // year 持有月份明细；month 为 undefined
}

export const parseYearMonth = (date: string): { year: string; month: string } => ({
  year: date.substring(0, 4),
  month: date.substring(5, 7),
});

const createEmptyRecord = (id: string, type: CostPeriodType): CostListModel => ({
  id,
  type,
  normalTradeCount: 0,
  convTradeCount: 0,
  dividendCount: 0,
  buyAmount: 0,
  sellAmount: 0,
  cashFlow: 0,
  fee: 0,
  subList: type === 'year' ? [] : undefined,
});

/** 取或建年份记录 */
const getOrCreateYear = (yearMap: Map<string, CostListModel>, year: string) => {
  let record = yearMap.get(year);
  if (!record) {
    record = createEmptyRecord(year, 'year');
    yearMap.set(year, record);
  }
  return record;
};

/** 取或建月份记录 */
const getOrCreateMonth = (yearRecord: CostListModel, month: string) => {
  let record = yearRecord.subList!.find((m) => m.id === month);
  if (!record) {
    record = createEmptyRecord(month, 'month');
    yearRecord.subList!.push(record);
  }
  return record;
};

/** 统计交易数据（买卖金额、手续费一律按人民币口径累加） */
export const buildCostListByPeriod = (
  data: API.Stock[],
  operations: Record<string, API.Operation[]>,
  cashFlowList?: API.CashFlowRecord[],
): CostListModel[] => {
  const yearMap = new Map<string, CostListModel>();

  for (const stock of data) {
    for (const op of operations[stock.code] || []) {
      const { year, month } = parseYearMonth(op.date);
      const yearRecord = getOrCreateYear(yearMap, year);
      const records = [yearRecord, getOrCreateMonth(yearRecord, month)];

      if (op.type === 'DV') {
        records.forEach((r) => r.dividendCount++);
        continue;
      }

      const amount = tradeAmountCny(stock.code, op);
      const countKey = stock.stockType === 'CONV' ? 'convTradeCount' : 'normalTradeCount';
      records.forEach((r) => {
        if (op.type === 'BUY') r.buyAmount += amount;
        else if (op.type === 'SELL') r.sellAmount += amount;
        r[countKey]++;
        r.fee += op.fee ?? 0;
      });
    }
  }

  // 出入金按年月合并（与交易同口径）
  for (const cf of cashFlowList ?? []) {
    const { year, month } = parseYearMonth(cf.date);
    if (!year) continue;
    const yearRecord = getOrCreateYear(yearMap, year);
    yearRecord.cashFlow += cf.amount;
    getOrCreateMonth(yearRecord, month).cashFlow += cf.amount;
  }

  const result = [...yearMap.values()].sort((a, b) => Number(b.id) - Number(a.id));
  result.forEach((year) => year.subList?.sort((a, b) => Number(b.id) - Number(a.id)));
  return result;
};

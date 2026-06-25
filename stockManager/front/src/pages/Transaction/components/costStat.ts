import { toCnyAmount } from '@/utils/format/stock';

export type CostPeriodType = 'year' | 'month';

export interface CostListModel {
  id: string;
  type: CostPeriodType;
  normalTradeCount: number;
  convTradeCount: number;
  dividendCount: number;
  fee: number;
  subList?: CostListModel[];
}

const parseYearMonth = (date: string): { year: string; month: string } => ({
  year: date.substring(0, 4),
  month: date.substring(5, 7),
});

const createEmptyRecord = (id: string, type: CostPeriodType): CostListModel => ({
  id,
  type,
  normalTradeCount: 0,
  convTradeCount: 0,
  dividendCount: 0,
  fee: 0,
  subList: type === 'year' ? [] : undefined,
});

/** 统计交易数据（港股通 fee 按汇率折算为 CNY） */
export const buildCostListByPeriod = (
  data: API.Stock[],
  operations: Record<string, API.Operation[]>,
  hkdCnyRate: number,
): CostListModel[] => {
  const yearMap = new Map<string, CostListModel>();

  for (const stock of data) {
    const stockOperations = operations[stock.code] || [];
    for (const op of stockOperations) {
      const { year, month } = parseYearMonth(op.date);

      if (!yearMap.has(year)) yearMap.set(year, createEmptyRecord(year, 'year'));
      const yearRecord = yearMap.get(year)!;

      let monthRecord = yearRecord.subList!.find((m) => m.id === month);
      if (!monthRecord) {
        monthRecord = createEmptyRecord(month, 'month');
        yearRecord.subList!.push(monthRecord);
      }

      if (op.type === 'DV') {
        yearRecord.dividendCount++;
        monthRecord.dividendCount++;
      } else {
        const feeCny = toCnyAmount(stock.code, op.fee, hkdCnyRate);
        if (stock.stockType === 'CONV') {
          yearRecord.convTradeCount++;
          monthRecord.convTradeCount++;
        } else {
          yearRecord.normalTradeCount++;
          monthRecord.normalTradeCount++;
        }
        yearRecord.fee += feeCny;
        monthRecord.fee += feeCny;
      }
    }
  }

  const result = [...yearMap.values()].sort((a, b) => Number(a.id) - Number(b.id));
  result.forEach((year) => year.subList?.sort((a, b) => Number(a.id) - Number(b.id)));
  return result;
};

export { parseYearMonth };

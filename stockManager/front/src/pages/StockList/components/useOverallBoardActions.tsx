import { Form, InputNumber, App } from 'antd';
import { updateIncomeCash } from '@/services/api';
import { isApiSuccess } from '@/utils/api';
import { useCashFlowModal } from './CashFlowModal';
import type { OverallBoardActions } from './overallBoardStat';

type UseOverallBoardActionsOptions = {
  data: API.Overall;
  onModifySuccess?: () => void;
};

export const useOverallBoardActions = ({
  data,
  onModifySuccess,
}: UseOverallBoardActionsOptions): OverallBoardActions => {
  const [form] = Form.useForm();
  const { modal } = App.useApp();
  const { showCashFlow } = useCashFlowModal();

  const editIncomeCash = () => {
    const totalAsset = data.totalAsset || 0;
    const incomeCash = data.incomeCash || 0;
    const fixedPart = totalAsset - incomeCash;

    form.setFieldsValue({ incomeCash, totalAsset });

    modal.confirm({
      title: '编辑现金收入',
      icon: null,
      content: (
        <Form form={form} layout="vertical" name="incomeCash" style={{ marginTop: 30 }}>
          <Form.Item
            label="现金收入"
            name="incomeCash"
            rules={[{ required: true, message: '请输入现金收入' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              precision={2}
              step={0.01}
              onChange={(v) =>
                form.setFieldsValue({ totalAsset: fixedPart + ((v as number) || 0) })
              }
            />
          </Form.Item>
          <Form.Item
            label="总资产"
            name="totalAsset"
            rules={[{ required: true, message: '请输入总资产' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              precision={2}
              step={0.01}
              onChange={(v) =>
                form.setFieldsValue({ incomeCash: ((v as number) || 0) - fixedPart })
              }
            />
          </Form.Item>
        </Form>
      ),
      onOk: async () => {
        const { incomeCash: nextIncomeCash } = await form.validateFields();
        const response = await updateIncomeCash(nextIncomeCash);
        if (isApiSuccess(response)) onModifySuccess?.();
      },
    });
  };

  const showOriginCashFlow = () =>
    showCashFlow({
      totalCashIn: data.originCash || 0,
      cashFlowList: data.cashFlowList || [],
    });

  return {
    incomeCash: editIncomeCash,
    originCash: showOriginCashFlow,
  };
};

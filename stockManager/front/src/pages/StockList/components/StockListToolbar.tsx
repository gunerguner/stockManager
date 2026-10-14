import { Button, Checkbox } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import { useIsMobile } from '@/hooks/useIsMobile';
import './index.less';

type StockListToolbarProps = {
  showAll: boolean;
  showConv: boolean;
  onRefresh: () => void;
  onShowAllChange: (checked: boolean) => void;
  onShowConvChange: (checked: boolean) => void;
};

export const StockListToolbar: React.FC<StockListToolbarProps> = ({
  showAll,
  showConv,
  onRefresh,
  onShowAllChange,
  onShowConvChange,
}) => {
  const isMobile = useIsMobile();

  return (
    <div className="stock-list-toolbar">
      <Button
        className="stock-list-toolbar-refresh"
        type="primary"
        ghost
        onClick={onRefresh}
        icon={<ReloadOutlined />}
        size={isMobile ? 'small' : 'middle'}
      >
        刷新
      </Button>
      <div className="stock-list-toolbar-filters">
        <Checkbox checked={showAll} onChange={(e) => onShowAllChange(e.target.checked)}>
          {isMobile ? '显示市值为零' : '显示市值为零的股票'}
        </Checkbox>
        <Checkbox checked={showConv} onChange={(e) => onShowConvChange(e.target.checked)}>
          显示可转债
        </Checkbox>
      </div>
    </div>
  );
};

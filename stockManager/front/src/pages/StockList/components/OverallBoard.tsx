import { Statistic, Row, Col, Divider } from 'antd';
import { useState } from 'react';
import { UpOutlined, DownOutlined } from '@ant-design/icons';
import { colorFromValue } from '@/utils/format/stock';
import { useIsMobile } from '@/hooks/useIsMobile';
import {
  EXPANDED_STATISTICS,
  MAIN_STATISTICS,
  resolveOverallStat,
  STAT_ACTIONS,
  type OverallBoardActions,
  type OverallStatConfig,
} from './overallStat';
import { useOverallBoardActions } from './useOverallBoardActions';
import './index.less';

type OverallBoardProps = {
  data: API.Overall;
  onModifySuccess?: () => void;
};

type StatisticItemProps = {
  title: string;
  value: string;
  numericValue?: number;
  showColor?: boolean;
  isMain?: boolean;
  onClick?: () => void;
};

const StatisticItem: React.FC<StatisticItemProps> = ({
  title,
  value,
  numericValue,
  showColor,
  isMain,
  onClick,
}) => {
  const isMobile = useIsMobile();
  const clickable = !!onClick;

  const styles = {
    title: {
      fontSize: isMobile ? 12 : isMain ? 14 : 13,
      marginBottom: isMobile ? (isMain ? 6 : 4) : isMain ? 8 : 4,
    },
    content: {
      fontWeight: isMain ? 'bold' : 'normal',
      fontSize: isMobile ? (isMain ? 24 : 18) : isMain ? 28 : 20,
      lineHeight: 1.2,
      ...(showColor && numericValue !== undefined && { color: colorFromValue(numericValue) }),
      ...(clickable && { color: '#1890ff' }),
    },
  };

  return (
    <Col span={isMobile ? 12 : 6} onClick={onClick} style={clickable ? { cursor: 'pointer' } : undefined}>
      <Statistic title={title} value={value} styles={styles} />
    </Col>
  );
};

const renderStatistics = (
  configs: OverallStatConfig[],
  data: API.Overall,
  actions: OverallBoardActions,
) =>
  configs
    .filter(({ when }) => !when || when(data))
    .map(({ key, title, showColor, isMain }) => {
      const { value, numeric } = resolveOverallStat(key, data);
      const actionKey = STAT_ACTIONS[key];
      const onClick = actionKey ? actions[actionKey] : undefined;

      return (
        <StatisticItem
          key={key}
          title={title}
          value={value}
          numericValue={showColor ? numeric : undefined}
          showColor={showColor}
          isMain={isMain}
          onClick={onClick}
        />
      );
    });

export const OverallBoard: React.FC<OverallBoardProps> = ({ data, onModifySuccess }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const isMobile = useIsMobile();
  const actions = useOverallBoardActions({ data, onModifySuccess });

  return (
    <div className="overall-board-wrapper">
      <Row gutter={[16, 16]}>{renderStatistics(MAIN_STATISTICS, data, actions)}</Row>

      <div
        className={`expand-divider-wrapper ${isExpanded ? 'expanded' : 'collapsed'}`}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <Divider className="expand-divider" styles={{ root: { margin: 0 }, content: { margin: '0 8px' } }}>
          {isExpanded ? <UpOutlined className="expand-icon" /> : <DownOutlined className="expand-icon" />}
        </Divider>
      </div>

      {isExpanded && (
        <Row gutter={[16, 16]} style={{ marginTop: isMobile ? 16 : 24 }}>
          {renderStatistics(EXPANDED_STATISTICS, data, actions)}
        </Row>
      )}
    </div>
  );
};

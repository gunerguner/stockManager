import { Statistic, Row, Col, Divider, theme } from 'antd';
import { useState } from 'react';
import { UpOutlined, DownOutlined } from '@ant-design/icons';
import { useProfitLossColors } from '@/hooks/useProfitLossColors';
import { useIsMobile } from '@/hooks/useIsMobile';
import {
  EXPANDED_STATISTICS,
  MAIN_STATISTICS,
  resolveOverallBoardStat,
  STAT_ACTIONS,
  type OverallBoardActions,
  type OverallStatConfig,
} from './overallBoardStat';
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
  colorFromValue: (value: number) => string | undefined;
  primaryColor: string;
};

const getBoardStatisticStyles = (
  isMobile: boolean,
  options?: {
    isMain?: boolean;
    showColor?: boolean;
    numericValue?: number;
    colorFromValue?: (value: number) => string | undefined;
    primaryColor?: string;
    clickable?: boolean;
  },
) => {
  const { isMain = false, showColor, numericValue, colorFromValue, primaryColor, clickable } =
    options ?? {};

  return {
    title: {
      fontSize: isMobile ? 12 : isMain ? 14 : 13,
      marginBottom: isMobile ? (isMain ? 6 : 4) : isMain ? 8 : 4,
    },
    content: {
      fontWeight: isMain ? 600 : ('normal' as const),
      fontSize: isMobile ? (isMain ? 24 : 18) : isMain ? 32 : 20,
      lineHeight: 1.2,
      fontVariantNumeric: 'tabular-nums' as const,
      ...(showColor &&
        numericValue !== undefined &&
        colorFromValue && {
          color: colorFromValue(numericValue),
        }),
      ...(clickable && primaryColor && { color: primaryColor }),
    },
  };
};

const StatisticItem: React.FC<StatisticItemProps> = ({
  title,
  value,
  numericValue,
  showColor,
  isMain,
  onClick,
  colorFromValue,
  primaryColor,
}) => {
  const isMobile = useIsMobile();
  const clickable = !!onClick;

  const styles = getBoardStatisticStyles(isMobile, {
    isMain,
    showColor,
    numericValue,
    colorFromValue,
    primaryColor,
    clickable,
  });

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
  colors: {
    colorFromValue: (value: number) => string | undefined;
    primaryColor: string;
  },
  isMain = false,
) =>
  configs.map(({ key, title, showColor }) => {
    const { value, numeric } = resolveOverallBoardStat(key, data);
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
        {...colors}
      />
    );
  });

export const OverallBoard: React.FC<OverallBoardProps> = ({ data, onModifySuccess }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const isMobile = useIsMobile();
  const actions = useOverallBoardActions({ data, onModifySuccess });
  const { colorFromValue } = useProfitLossColors();
  const { token } = theme.useToken();

  const colorProps = {
    colorFromValue,
    primaryColor: token.colorPrimary,
  };

  return (
    <div className="overall-board-wrapper">
      <Row gutter={[16, 16]}>{renderStatistics(MAIN_STATISTICS, data, actions, colorProps, true)}</Row>

      <div
        className={`expand-divider-wrapper ${isExpanded ? 'expanded' : 'collapsed'}`}
        onClick={() => setIsExpanded(!isExpanded)}
        style={
          {
            '--divider-color': token.colorBorderSecondary,
            '--divider-hover-color': token.colorPrimary,
          } as React.CSSProperties
        }
      >
        <Divider
          className="expand-divider"
          styles={{
            root: { margin: 0 },
            content: { margin: '0 8px' },
          }}
        >
          {isExpanded ? <UpOutlined className="expand-icon" /> : <DownOutlined className="expand-icon" />}
        </Divider>
      </div>

      {isExpanded && (
        <Row gutter={[16, 16]} style={{ marginTop: isMobile ? 16 : 24 }}>
          {renderStatistics(EXPANDED_STATISTICS, data, actions, colorProps)}
        </Row>
      )}
    </div>
  );
};

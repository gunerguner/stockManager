import { App, Table } from 'antd';
import type { ModalFuncProps } from 'antd';
import type { ColumnsType } from 'antd/lib/table';
import type { GetRowKey } from 'antd/es/table/interface';
import React from 'react';
import { useIsMobile } from '@/hooks/useIsMobile';
import './index.less';

type ShowModalParams = {
  title: string;
  content: React.ReactNode;
  width?: number;
};

type SingleTableParams = {
  title: string;
  width?: number;
  headerView?: React.ReactNode;
  columns: ColumnsType<any>;
  dataSource: any[];
};

type TableGroup = {
  headerView?: React.ReactNode;
  columns: ColumnsType<any>;
  dataSource: any[];
};

type MultiTableParams = {
  title: string;
  width?: number;
  tables: TableGroup[];
};

type RenderTableParams = TableGroup & { rowKey: GetRowKey<any> };

/**
 * 通用 Modal Hook
 * 封装了 modal.info 的调用逻辑和样式配置
 */
export const useCommonModal = () => {
  const { modal } = App.useApp();
  const isMobile = useIsMobile();

  const prefixedRowKey = (prefix: string): GetRowKey<any> => (record, index) =>
    record?.id ?? record?.key ?? `${prefix}-${index ?? 0}`;

  const commonTableProps = React.useMemo(
    () =>
      ({
        size: 'small',
        bordered: true,
        pagination: false,
        scroll: { x: 'max-content' },
        ...(isMobile && {
          styles: {
            body: { row: { fontSize: 12 } },
            header: { row: { fontSize: 11 } },
          },
        }),
      } as const),
    [isMobile],
  );

  const renderTable = ({ headerView, columns, dataSource, rowKey }: RenderTableParams) => (
    <div className="common-table-group-item">
      {headerView && <div className="common-table-header">{headerView}</div>}
      <Table {...commonTableProps} columns={columns} dataSource={dataSource} rowKey={rowKey} />
    </div>
  );

  const renderTables = (tables: TableGroup[], variant: 'single' | 'multi') =>
    !tables?.length || tables.every((t) => !t.dataSource?.length) ? (
      <div className="common-empty-data">暂无数据</div>
    ) : (
      <div className={variant === 'single' ? 'common-single-table-content' : 'common-multi-table-content'}>
        {tables.map((table, tableIndex) =>
          !table.dataSource?.length ? null : (
            <React.Fragment key={tableIndex}>
              {renderTable({
                headerView: table.headerView,
                columns: table.columns,
                dataSource: table.dataSource,
                rowKey: prefixedRowKey(`row-${tableIndex}`),
              })}
              {variant === 'multi' && tableIndex < tables.length - 1 && <div className="table-group-divider" />}
            </React.Fragment>
          ),
        )}
      </div>
    );

  const showModal = React.useCallback(
    ({ title, content, width = 600 }: ShowModalParams) => {
      const styles: ModalFuncProps['styles'] = isMobile
        ? {
            body: { maxHeight: 'none', padding: '12px', flex: 1, overflowY: 'auto' },
            header: { padding: '8px 16px 12px 16px', borderBottom: '1px solid rgba(0, 0, 0, 0.06)' },
            wrapper: { margin: 0, maxWidth: '100vw', top: 0, paddingBottom: 0 },
          }
        : { body: { maxHeight: 'none' } };

      modal.info({
        title,
        content,
        width: isMobile ? '95%' : width,
        icon: null,
        footer: null,
        closable: true,
        maskClosable: true,
        styles,
      });
    },
    [modal, isMobile],
  );

  const showSingleTable = React.useCallback(
    ({ title, width = 600, headerView, columns, dataSource }: SingleTableParams) => {
      showModal({
        title,
        content: renderTables([{ headerView, columns, dataSource }], 'single'),
        width,
      });
    },
    [showModal, renderTables],
  );

  const showMultiTable = React.useCallback(
    ({ title, width = 600, tables }: MultiTableParams) => {
      showModal({
        title,
        content: renderTables(tables, 'multi'),
        width,
      });
    },
    [showModal, renderTables],
  );

  return { showModal, showSingleTable, showMultiTable };
};


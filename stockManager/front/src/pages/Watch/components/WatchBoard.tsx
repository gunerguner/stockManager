import { useCallback, useMemo } from 'react';
import { WatchToolbar } from './WatchToolbar';
import { WatchTable } from './WatchTable';
import { HiddenWatchSection } from './HiddenWatchSection';

type WatchBoardProps = {
  list: API.WatchItem[];
  loading?: boolean;
  onRefresh: () => void;
  onSetHidden: (code: string, hidden: boolean) => Promise<boolean>;
};

export const WatchBoard: React.FC<WatchBoardProps> = ({
  list,
  loading = false,
  onRefresh,
  onSetHidden,
}) => {
  const visibleList = useMemo(() => list.filter((item) => !item.hidden), [list]);
  const hiddenList = useMemo(() => list.filter((item) => item.hidden), [list]);

  const handleToggleHidden = useCallback(
    async (record: API.WatchItem, nextHidden: boolean) => {
      return onSetHidden(record.code, nextHidden);
    },
    [onSetHidden],
  );

  return (
    <>
      <WatchToolbar loading={loading} onRefresh={onRefresh} />
      <WatchTable
        data={visibleList}
        loading={loading}
        onToggleHidden={handleToggleHidden}
      />
      <HiddenWatchSection
        data={hiddenList}
        loading={loading}
        onToggleHidden={handleToggleHidden}
      />
    </>
  );
};

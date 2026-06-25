/** 顶部 Statistic 卡片（标题/数值）的移动端自适应样式 */
export const getHeaderStatisticStyles = (isMobile: boolean, color?: string) => ({
  title: {
    fontSize: isMobile ? 12 : undefined,
    marginBottom: 4,
  },
  content: {
    fontSize: isMobile ? 18 : undefined,
    ...(color ? { color } : {}),
  },
});

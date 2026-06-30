/** 顶部 Statistic 卡片（标题/数值）的移动端自适应样式 */
export const getHeaderStatisticStyles = (isMobile: boolean, color?: string) => ({
  title: {
    fontSize: isMobile ? 11 : undefined,
    marginBottom: isMobile ? 2 : 4,
  },
  content: {
    fontSize: isMobile ? 16 : undefined,
    lineHeight: 1.2,
    ...(color ? { color } : {}),
  },
});

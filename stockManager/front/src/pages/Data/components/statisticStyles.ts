/** Data 页头部 Statistic 移动端样式 */
export const getHeaderStatisticStyles = (isMobile: boolean, color?: string | undefined) => ({
  title: {
    fontSize: isMobile ? 12 : undefined,
    marginBottom: 4,
  },
  content: {
    fontSize: isMobile ? 18 : undefined,
    ...(color ? { color } : {}),
  },
});

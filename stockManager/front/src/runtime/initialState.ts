import type { ProLayoutProps } from '@ant-design/pro-components';
import { history } from '@umijs/max';
import defaultSettings from '../../config/defaultSettings';
import { getCurrentUser as queryCurrentUser } from '@/services/api';
import { RESPONSE_STATUS } from '@/utils/apiConstants';
import { LOGIN_PATH } from './constants';

export async function getInitialState(): Promise<{
  settings?: Partial<ProLayoutProps>;
  currentUser?: API.CurrentUser;
  fetchUserInfo?: () => Promise<API.CurrentUser | undefined>;
}> {
  const fetchUserInfo = async () => {
    try {
      const result = await queryCurrentUser();
      if (result.status === RESPONSE_STATUS.SUCCESS) return result.info;
      if (result.status === RESPONSE_STATUS.UNAUTHORIZED) history.push(LOGIN_PATH);
    } catch {
      history.push(LOGIN_PATH);
    }
    return undefined;
  };

  const isLoginPage = history.location.pathname === LOGIN_PATH;
  const currentUser = isLoginPage ? undefined : await fetchUserInfo();

  return {
    fetchUserInfo,
    currentUser,
    settings: defaultSettings,
  };
}

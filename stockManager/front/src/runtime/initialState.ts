import type { ProLayoutProps } from '@ant-design/pro-components';
import { history } from '@umijs/max';
import defaultSettings from '../../config/defaultSettings';
import { getCurrentUser as queryCurrentUser } from '@/services/api';
import { isApiSuccess } from '@/utils/api';
import { LOGIN_PATH } from './constants';

export async function getInitialState(): Promise<{
  settings?: Partial<ProLayoutProps>;
  currentUser?: API.CurrentUser;
  fetchUserInfo?: () => Promise<API.CurrentUser | undefined>;
}> {
  const fetchUserInfo = async () => {
    try {
      const result = await queryCurrentUser();
      if (isApiSuccess(result)) return result.info;
    } catch {
      if (history.location.pathname !== LOGIN_PATH) {
        history.push(LOGIN_PATH);
      }
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


import { apiGet } from '../../../services/apiClient.js';
import { API_ENDPOINTS } from '../../../services/endpointConfig.js';
import { unwrapList } from '../../../utils/formatters.js';

export async function getPublicContent() {
  const [notices, members] = await Promise.allSettled([
    apiGet(API_ENDPOINTS.notices),
    apiGet(API_ENDPOINTS.activeMembers),
  ]);
  return {
    notices: notices.status === 'fulfilled' ? unwrapList(notices.value) : [],
    members: members.status === 'fulfilled' ? unwrapList(members.value) : [],
    hasError: [notices, members].some((result) => result.status === 'rejected'),
  };
}

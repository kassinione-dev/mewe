import { requestJson } from '../core/http.js';

export function updateAbout(about) {
  return requestJson('/api/users/me', { method: 'PATCH', body: { about } });
}

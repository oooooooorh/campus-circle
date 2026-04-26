/**
 * 统一的 API 配置
 * 会根据环境自动切换:
 * - 本地开发环境 (npm run dev): http://127.0.0.1:8000
 * - 生产打包环境 (npm run build): https://campus-api-bkfua8a9gdcfaff3.eastasia-01.azurewebsites.net
 */
export const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

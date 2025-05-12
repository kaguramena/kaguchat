// frontend/src/admin/services/adminApi.js
import axios from 'axios'; // 或者你全局配置的 axios 实例

// 后端 Admin API 的基础 URL 前缀
const API_BASE_URL = 'http://localhost:5001/api/admin'; // 确保这个与你的 Flask 后端匹配

// 创建一个 axios 实例，专门用于 admin API 调用
// 这样做的好处是，如果将来 admin API 有特定的头部或配置，可以在这里统一处理
// 但目前，我们假设全局的 axios 实例已经通过 AuthContext 配置好了认证头部 (Authorization 和 X-CSRF-TOKEN)
// 所以直接使用全局 axios 也是可以的。为了演示，我们创建一个新实例，但你可以根据情况调整。
const adminApiClient = axios.create({
    baseURL: API_BASE_URL,
    // 你可以在这里设置一些 admin API 特有的默认配置，如果需要的话
    // 例如，特定的超时时间等
});

// --- 拦截器 (可选，但推荐) ---
// 你可以为这个 adminApiClient 实例添加请求拦截器和响应拦截器
// 请求拦截器：可以在每个请求发送前做一些事情，例如再次确认头部是否正确
adminApiClient.interceptors.request.use(
    (config) => {
        // 确保认证头部已经由 AuthContext 的全局 axios 配置设置了
        // 如果没有，你可以在这里从 localStorage 读取并设置，但这通常不是最佳实践
        // 最佳实践是 AuthContext 维护全局 axios 实例的头部
        // console.log('[adminApi] Sending request with headers:', config.headers);
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);


adminApiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('authToken'); // 从 localStorage 获取 token
        const csrfToken = localStorage.getItem('csrfToken'); // 从 localStorage 获取 CSRF token

        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        if (csrfToken) { // 如果你的后端API也需要CSRF token
            config.headers['X-CSRF-TOKEN'] = csrfToken;
        }
        // console.log('[adminApi] Sending request with headers:', config.headers);
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// 响应拦截器：可以在接收到响应后做一些事情，例如全局错误处理
adminApiClient.interceptors.response.use(
    (response) => {
        // 直接返回 response.data，这样调用方可以直接使用数据
        return response.data;
    },
    (error) => {
        // 全局处理一些常见的错误，或者只是重新抛出
        console.error('[adminApi] API Error:', error.response || error.message);
        if (error.response) {
            // 例如，如果收到 401 或 403，可能需要触发登出或显示权限错误
            // if (error.response.status === 401 || error.response.status === 403) {
            //     // 可以在这里调用 AuthContext.logout() 或其他全局错误处理
            // }
            // 为了让调用方能处理具体的错误，通常会重新抛出错误，或者返回一个包含错误信息的对象
            return Promise.reject(error.response.data || { msg: 'An unknown API error occurred' });
        }
        return Promise.reject({ msg: error.message || 'Network error or no response from server' });
    }
);


// --- API 函数 ---

/**
 * 获取可管理的表名列表及其显示名。
 * @returns {Promise<Array<{key: string, displayName: string}>>}
 */
export const getAdminTables = async () => {
    // API 返回的数据结构是 { tables: [{key: "...", displayName: "..."}] }
    // 拦截器已经处理了返回 response.data，所以这里直接用 tables
    const responseData = await adminApiClient.get('/config/tables');
    return responseData.tables || []; // 确保即使 tables 不存在也返回空数组
};

/**
 * 获取指定表的结构信息。
 * @param {string} tableNameDisplay - 表的显示名 (URL中的key)。
 * @returns {Promise<object>} Schema information.
 */
export const getTableSchema = async (tableNameDisplay) => {
    return await adminApiClient.get(`/table/${tableNameDisplay}/schema`);
};

/**
 * 获取指定表的所有数据记录。
 * @param {string} tableNameDisplay - 表的显示名。
 * @returns {Promise<{data: Array<object>, primary_key: string}>} Object containing data array and primary key name.
 */
export const getTableData = async (tableNameDisplay) => {
    // API 返回 { data: [...], primary_key: "..." }
    return await adminApiClient.get(`/table/${tableNameDisplay}/data`);
};

/**
 * 添加一条新记录到指定表。
 * @param {string} tableNameDisplay - 表的显示名。
 * @param {object} recordData - 要添加的记录数据 (JSON对象)。
 * @returns {Promise<object>} Contains msg and the newly added record.
 */
export const addTableRecord = async (tableNameDisplay, recordData) => {
    // API 返回 { msg: "...", record: {...} }
    return await adminApiClient.post(`/table/${tableNameDisplay}/data`, recordData);
};

/**
 * 更新指定表中的特定记录。
 * @param {string} tableNameDisplay - 表的显示名。
 * @param {string|number} recordId - 要更新的记录的ID。
 * @param {object} recordData - 包含待更新字段的JSON对象。
 * @returns {Promise<object>} Contains msg and the updated record.
 */
export const updateTableRecord = async (tableNameDisplay, recordId, recordData) => {
    // API 返回 { msg: "...", record: {...} }
    return await adminApiClient.put(`/table/${tableNameDisplay}/data/${recordId}`, recordData);
};

/**
 * 删除指定表中的特定记录。
 * @param {string} tableNameDisplay - 表的显示名。
 * @param {string|number} recordId - 要删除的记录的ID。
 * @returns {Promise<object>} Contains msg.
 */
export const deleteTableRecord = async (tableNameDisplay, recordId) => {
    // API 返回 { msg: "..." }
    return await adminApiClient.delete(`/table/${tableNameDisplay}/data/${recordId}`);
};

// 如果有仪表盘数据的 API，也可以在这里添加
/**
 * 获取仪表盘数据。
 * @returns {Promise<object>} Dashboard data.
 */
// export const getAdminDashboardData = async () => {
//     return await adminApiClient.get('/dashboard-data');
// };

// 你可以将 adminApiClient 导出，以便在其他地方如果需要直接使用带有 baseURL 的实例
// export default adminApiClient;
// 或者只导出这些函数
/**
 * 课表爬虫 API 调用示例 (Vue.js / JavaScript)
 * 用于前端集成调用后端的课表爬虫 API
 */

// API 端点
const API_BASE = "http://127.0.0.1:8000";
const SCHEDULE_API = `${API_BASE}/api/schedule`;

/**
 * 获取课表
 * @param {string} username - 教务系统账号
 * @param {string} password - 教务系统密码
 * @returns {Promise} 课表数据
 */
async function getSchedule(username, password) {
  try {
    console.log("🔄 正在获取课表...");
    
    const response = await fetch(SCHEDULE_API, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username: username,
        password: password,
      }),
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.detail || "获取课表失败");
    }

    console.log("✅ 成功获取课表！", result);
    return result;
  } catch (error) {
    console.error("❌ 获取课表出错:", error.message);
    throw error;
  }
}

/**
 * 处理课表数据（示例）
 * @param {Array} scheduleData - 课表数据数组
 */
function processScheduleData(scheduleData) {
  if (!scheduleData || !Array.isArray(scheduleData)) {
    console.warn("⚠️ 无有效课表数据");
    return;
  }

  console.log(`📊 共获取 ${scheduleData.length} 条课表记录`);

  // 按日期分组
  const grouped = {};
  scheduleData.forEach((item) => {
    const day = item.xq || "未知";
    if (!grouped[day]) {
      grouped[day] = [];
    }
    grouped[day].push(item);
  });

  console.log("📅 按日期分组:", grouped);
  return grouped;
}

/**
 * Vue 组件示例：课表查询表单
 */
const ScheduleFormComponent = {
  template: `
    <div class="schedule-form">
      <h2>📚 个人课表查询</h2>
      
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="username">账号：</label>
          <input 
            id="username"
            v-model="form.username" 
            type="text"
            placeholder="请输入教务系统账号"
            required
          />
        </div>

        <div class="form-group">
          <label for="password">密码：</label>
          <input 
            id="password"
            v-model="form.password" 
            type="password"
            placeholder="请输入教务系统密码"
            required
          />
        </div>

        <button type="submit" :disabled="loading">
          {{ loading ? "⏳ 正在查询..." : "🔍 查询课表" }}
        </button>
      </form>

      <!-- 错误提示 -->
      <div v-if="error" class="error-message">
        ❌ {{ error }}
      </div>

      <!-- 课表结果 -->
      <div v-if="scheduleData && scheduleData.length > 0" class="schedule-result">
        <h3>✅ 课表信息 (共 {{ scheduleData.length }} 条)</h3>
        <table>
          <thead>
            <tr>
              <th>课程代码</th>
              <th>课程名称</th>
              <th>学分</th>
              <th>班级</th>
              <th>周次</th>
              <th>星期</th>
              <th>节次</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in scheduleData.slice(0, 10)" :key="item.kh">
              <td>{{ item.kh }}</td>
              <td>{{ item.kcmc }}</td>
              <td>{{ item.xf }}</td>
              <td>{{ item.jxb }}</td>
              <td>{{ item.zc }}</td>
              <td>{{ item.xq }}</td>
              <td>{{ item.jc }}</td>
            </tr>
          </tbody>
        </table>
        <p v-if="scheduleData.length > 10" class="text-muted">
          ...还有 {{ scheduleData.length - 10 }} 条记录
        </p>
      </div>

      <!-- 下载按钮 -->
      <div v-if="scheduleData" class="action-buttons">
        <button @click="downloadJSON">💾 下载 JSON</button>
        <button @click="downloadCSV">📊 下载 CSV</button>
      </div>
    </div>
  `,

  data() {
    return {
      form: {
        username: "",
        password: "",
      },
      loading: false,
      error: null,
      scheduleData: null,
    };
  },

  methods: {
    async handleSubmit() {
      this.loading = true;
      this.error = null;

      try {
        const result = await getSchedule(
          this.form.username,
          this.form.password
        );

        if (result.status === "success") {
          this.scheduleData = result.data;
          console.log("📚 课表数据已加载", this.scheduleData);
        } else {
          this.error = "获取课表失败";
        }
      } catch (error) {
        this.error = error.message || "网络错误，请重试";
      } finally {
        this.loading = false;
      }
    },

    downloadJSON() {
      if (!this.scheduleData) return;

      const dataStr = JSON.stringify(this.scheduleData, null, 2);
      const dataBlob = new Blob([dataStr], { type: "application/json" });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `课表_${new Date().getTime()}.json`;
      link.click();
      URL.revokeObjectURL(url);
    },

    downloadCSV() {
      if (!this.scheduleData || this.scheduleData.length === 0) return;

      const headers = [
        "课程代码",
        "课程名称",
        "学分",
        "班级",
        "周次",
        "星期",
        "节次",
      ];
      const rows = this.scheduleData.map((item) => [
        item.kh,
        item.kcmc,
        item.xf,
        item.jxb,
        item.zc,
        item.xq,
        item.jc,
      ]);

      let csvContent = headers.join(",") + "\\n";
      rows.forEach((row) => {
        csvContent += row.join(",") + "\\n";
      });

      const dataBlob = new Blob([csvContent], {
        type: "text/csv;charset=utf-8;",
      });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `课表_${new Date().getTime()}.csv`;
      link.click();
      URL.revokeObjectURL(url);
    },
  },
};

// 导出供其他模块使用
export { getSchedule, processScheduleData, ScheduleFormComponent };

/**
 * 使用示例
 * 
 * import { getSchedule, ScheduleFormComponent } from './schedule-api.js'
 * 
 * // 1. 在 Vue 中注册组件
 * app.component('ScheduleForm', ScheduleFormComponent)
 * 
 * // 2. 或者直接调用函数
 * const result = await getSchedule('2320110098', '153624orhA')
 * console.log(result.data)
 */

const { createApp } = Vue;

createApp({
    data() {
        return {
            currentTab: 'status',
            wsConnected: false,
            ws: null,
            config: {
                global: {
                    proxy: null,
                    output: 'output'
                },
                users: []
            },
            recordingStatus: {},
            files: [],
            logs: [],
            platforms: [],
            autoScroll: true,
            showAddForm: false,
            editingIndex: null,
            editingUser: {
                platform: 'Bilibili',
                id: '',
                name: '',
                interval: 10,
                format: ''
            },
            notification: {
                show: false,
                message: '',
                type: 'success'
            },
            stats: {
                totalUsers: 0,
                recording: 0,
                files: 0,
                totalSize: '0 MB'
            }
        };
    },
    mounted() {
        this.loadConfig();
        this.loadPlatforms();
        this.loadFiles();
        this.loadLogs();
        this.connectWebSocket();
        
        // 定时刷新数据
        setInterval(() => {
            this.loadFiles();
            this.loadLogs();
        }, 10000); // 每10秒刷新一次
    },
    methods: {
        // WebSocket连接
        connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                this.wsConnected = true;
                console.log('WebSocket connected');
                // 发送心跳并更新状态
                setInterval(() => {
                    if (this.ws.readyState === WebSocket.OPEN) {
                        this.ws.send('ping');
                    }
                }, 30000);
                
                // 定期从API获取状态
                this.loadStatus();
                setInterval(() => this.loadStatus(), 5000);
            };
            
            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'status_update') {
                    this.recordingStatus = data.data.recording || data.data;
                    this.updateStats();
                }
            };
            
            this.ws.onclose = () => {
                this.wsConnected = false;
                console.log('WebSocket disconnected, reconnecting...');
                // 5秒后重连
                setTimeout(() => this.connectWebSocket(), 5000);
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        },
        
        // 加载录制状态
        async loadStatus() {
            try {
                const response = await axios.get('/api/status');
                if (response.data.recording_count !== undefined) {
                    this.stats.recording = response.data.recording_count;
                }
                this.recordingStatus = response.data.recording || {};
            } catch (error) {
                console.error('加载状态失败:', error);
            }
        },
        
        // 加载配置
        async loadConfig() {
            try {
                const response = await axios.get('/api/config');
                this.config = {
                    global: response.data.global || { proxy: null, output: 'output' },
                    users: response.data.users || []
                };
                this.updateStats();
            } catch (error) {
                console.error('加载配置失败:', error);
                this.showNotification('加载配置失败', 'error');
            }
        },
        
        // 保存配置
        async saveConfig() {
            try {
                const configData = {
                    ...this.config.global,
                    user: this.config.users
                };
                await axios.post('/api/config', configData);
                this.showNotification('配置保存成功！需要重启程序生效', 'success');
            } catch (error) {
                console.error('保存配置失败:', error);
                this.showNotification('保存配置失败', 'error');
            }
        },
        
        // 加载平台列表
        async loadPlatforms() {
            try {
                const response = await axios.get('/api/platforms');
                this.platforms = response.data.platforms || [];
            } catch (error) {
                console.error('加载平台列表失败:', error);
            }
        },
        
        // 加载文件列表
        async loadFiles() {
            try {
                const response = await axios.get('/api/files');
                this.files = response.data.files || [];
                this.stats.files = response.data.count || 0;
                this.stats.totalSize = `${response.data.total_size_mb || 0} MB`;
                console.log('文件列表:', response.data);
            } catch (error) {
                console.error('加载文件列表失败:', error);
            }
        },
        
        // 加载日志
        async loadLogs() {
            try {
                const response = await axios.get('/api/logs', {
                    params: { lines: 100 }
                });
                this.logs = response.data.logs || [];
                
                // 自动滚动到底部
                if (this.autoScroll) {
                    this.$nextTick(() => {
                        const container = this.$refs.logContainer;
                        if (container) {
                            container.scrollTop = container.scrollHeight;
                        }
                    });
                }
            } catch (error) {
                console.error('加载日志失败:', error);
            }
        },
        
        // 保存正在编辑的用户
        saveEditingUser() {
            if (!this.editingUser.id || !this.editingUser.name) {
                this.showNotification('请填写房间ID和主播名', 'error');
                return;
            }
            
            if (!this.config.users) {
                this.config.users = [];
            }
            
            if (this.editingIndex !== null) {
                // 更新现有用户
                this.config.users[this.editingIndex] = {...this.editingUser};
                this.showNotification('主播信息已更新', 'success');
            } else {
                // 添加新用户
                this.config.users.push({...this.editingUser});
                this.showNotification('主播添加成功', 'success');
            }
            
            this.cancelEditing();
        },
        
        // 编辑用户
        editUser(index) {
            this.editingIndex = index;
            this.editingUser = {...this.config.users[index]};
            this.showAddForm = false;
        },
        
        // 取消编辑
        cancelEditing() {
            this.showAddForm = false;
            this.editingIndex = null;
            this.editingUser = {
                platform: this.platforms[0] || 'Bilibili',
                id: '',
                name: '',
                interval: 10,
                format: ''
            };
        },
        
        // 删除用户
        removeUser(index) {
            if (confirm('确定要删除这个主播配置吗？')) {
                this.config.users.splice(index, 1);
                this.showNotification('主播已删除', 'success');
            }
        },
        
        // 开始录制
        async startRecording(user) {
            try {
                const response = await axios.post(`/api/start_recording/${user.platform}/${user.id}`);
                this.showNotification(`正在启动 ${user.name} 的录制...`, 'success');
                
                // 更新状态
                const key = `${user.platform}_${user.id}`;
                this.recordingStatus[key] = {
                    platform: user.platform,
                    user_id: user.id,
                    status: 'recording',
                    timestamp: new Date().toISOString()
                };
            } catch (error) {
                console.error('启动录制失败:', error);
                this.showNotification('启动录制失败', 'error');
            }
        },
        
        // 停止录制
        async stopRecording(user) {
            try {
                const response = await axios.post(`/api/stop_recording/${user.platform}/${user.id}`);
                this.showNotification(`已停止 ${user.name} 的录制`, 'success');
                
                // 更新状态
                const key = `${user.platform}_${user.id}`;
                if (this.recordingStatus[key]) {
                    this.recordingStatus[key].status = 'stopped';
                }
            } catch (error) {
                console.error('停止录制失败:', error);
                this.showNotification('停止录制失败', 'error');
            }
        },
        
        // 更新统计数据
        updateStats() {
            this.stats.totalUsers = this.config.users.length;
            
            // 统计正在录制的数量
            this.stats.recording = Object.values(this.recordingStatus)
                .filter(status => status.status === 'recording').length;
        },
        
        // 获取状态类
        getStatusClass(user) {
            const key = `${user.platform}_${user.id}`;
            const status = this.recordingStatus[key];
            
            if (status && status.status === 'recording') {
                return 'status-recording recording-pulse';
            } else if (status && status.status === 'online') {
                return 'status-online';
            } else {
                return 'status-offline';
            }
        },
        
        // 判断是否正在录制
        isRecording(user) {
            const key = `${user.platform}_${user.id}`;
            const status = this.recordingStatus[key];
            return status && status.status === 'recording';
        },
        
        // 格式化日期
        formatDate(isoString) {
            const date = new Date(isoString);
            return date.toLocaleString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        },
        
        // 显示通知
        showNotification(message, type = 'success') {
            this.notification = {
                show: true,
                message,
                type
            };
            
            setTimeout(() => {
                this.notification.show = false;
            }, 3000);
        }
    }
}).mount('#app');

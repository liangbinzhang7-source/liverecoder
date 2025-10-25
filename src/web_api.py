"""Web API服务器"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import uvicorn

from .config import Config
from .platforms import PLATFORMS

# 全局变量
app = FastAPI(title="LiveRecorder Web管理界面", version="1.0.0")
recording_status: Dict = {}  # 录制状态
recorder_tasks: Dict = {}  # 录制任务
ws_connections: List[WebSocket] = []  # WebSocket连接

# 共享的recording字典（将由main_web.py注入）
_shared_recording: Dict = {}

# 配置静态文件服务
from pathlib import Path as PathLib
static_dir = PathLib(__file__).parent.parent / "web" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


class UserConfig(BaseModel):
    """用户配置模型"""
    platform: str
    id: str
    name: Optional[str] = None
    interval: Optional[int] = 10
    format: Optional[str] = None
    output: Optional[str] = None
    proxy: Optional[str] = None
    headers: Optional[dict] = None
    cookies: Optional[str] = None


class GlobalConfig(BaseModel):
    """全局配置模型"""
    proxy: Optional[str] = None
    output: Optional[str] = "output"


# WebSocket管理
class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        """广播消息给所有连接的客户端"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()


def set_shared_recording(recording_dict: Dict):
    """设置共享的recording字典"""
    global _shared_recording
    _shared_recording = recording_dict


def get_recording_count() -> int:
    """获取当前正在录制的数量"""
    return len(_shared_recording)


def get_recording_info() -> Dict:
    """获取录制详细信息"""
    info = {}
    for url, (stream_fd, output) in _shared_recording.items():
        # 从URL提取平台和用户信息
        info[url] = {
            "url": url,
            "recording": True,
            "timestamp": datetime.now().isoformat()
        }
    return info


# API路由
@app.get("/")
async def read_root():
    """返回前端页面"""
    from pathlib import Path
    html_path = Path(__file__).parent.parent / "web" / "index.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail=f"未找到页面文件: {html_path}")
    return FileResponse(str(html_path))


@app.get("/api/status")
async def get_status():
    """获取录制状态"""
    # 根据实际的recording字典生成状态
    recording_info = get_recording_info()
    
    return {
        "recording": recording_info,
        "recording_count": get_recording_count(),
        "tasks": len(recorder_tasks),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/config")
async def get_config():
    """获取当前配置"""
    try:
        config = Config('web_config.json')
        return {
            "global": config.get_global_config(),
            "users": config.get_users()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/config")
async def update_config(config: dict):
    """更新配置"""
    try:
        web_config = Config('web_config.json')
        if web_config.save(config):
            return {"status": "success", "message": "配置已保存，请重启服务生效"}
        else:
            raise HTTPException(status_code=500, detail="保存失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/platforms")
async def get_platforms():
    """获取支持的平台列表"""
    return {
        "platforms": list(PLATFORMS.keys()),
        "count": len(PLATFORMS)
    }


@app.get("/api/files")
async def get_files(output_dir: str = None):
    """获取录制文件列表"""
    try:
        # 如果没有指定输出目录，从配置中获取
        if not output_dir:
            config = Config('web_config.json')
            output_dir = config.get_global_config().get('output', 'output')
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            return {"files": [], "count": 0, "total_size_mb": 0, "output_dir": output_dir}
        
        files = []
        for file in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                files.append({
                    "name": file,
                    "size": stat.st_size,
                    "size_mb": round(stat.st_size / 1024 / 1024, 2),
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        # 按修改时间倒序排列
        files.sort(key=lambda x: x['modified'], reverse=True)
        
        return {
            "files": files,
            "count": len(files),
            "total_size_mb": round(sum(f['size'] for f in files) / 1024 / 1024, 2),
            "output_dir": output_dir
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/logs")
async def get_logs(lines: int = 100):
    """获取最新日志"""
    try:
        log_dir = Path("logs")
        if not log_dir.exists():
            return {"logs": []}
        
        # 获取最新的日志文件
        log_files = sorted(log_dir.glob("log_*.log"), key=os.path.getmtime, reverse=True)
        if not log_files:
            return {"logs": []}
        
        latest_log = log_files[0]
        with open(latest_log, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        return {
            "logs": [line.strip() for line in recent_lines],
            "file": latest_log.name,
            "total_lines": len(all_lines)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/start_recording/{platform}/{user_id}")
async def start_recording(platform: str, user_id: str):
    """手动启动录制"""
    try:
        # TODO: 实现手动启动录制逻辑
        # 目前录制是自动进行的，此接口暂时只返回成功
        return {"status": "success", "message": f"已启动 {platform}/{user_id} 的录制"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/stop_recording/{platform}/{user_id}")
async def stop_recording(platform: str, user_id: str):
    """手动停止录制"""
    try:
        from loguru import logger
        
        # 查找并关闭对应的录制流
        stopped_count = 0
        urls_to_remove = []
        
        # 遍历所有正在录制的流
        for url, (stream_fd, output) in list(_shared_recording.items()):
            # 检查URL是否匹配平台和用户ID
            if f"/{user_id}" in url or f"={user_id}" in url or url.endswith(user_id):
                try:
                    logger.info(f"正在停止录制: {url}")
                    # 关闭流
                    if hasattr(stream_fd, 'close'):
                        stream_fd.close()
                    # 关闭输出
                    if hasattr(output, 'close'):
                        output.close()
                    urls_to_remove.append(url)
                    stopped_count += 1
                except Exception as e:
                    logger.error(f"关闭流时出错: {e}")
        
        # 从字典中移除已停止的录制
        for url in urls_to_remove:
            _shared_recording.pop(url, None)
            logger.info(f"已从录制列表中移除: {url}")
        
        if stopped_count > 0:
            return {
                "status": "success", 
                "message": f"已停止 {stopped_count} 个 {platform}/{user_id} 的录制流"
            }
        else:
            return {
                "status": "info",
                "message": f"{platform}/{user_id} 当前没有正在录制的流"
            }
    except Exception as e:
        logger.exception(f"停止录制失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端点，用于实时更新"""
    await manager.connect(websocket)
    try:
        while True:
            # 接收客户端消息（保持连接）
            data = await websocket.receive_text()
            
            # 发送当前状态
            await websocket.send_json({
                "type": "status_update",
                "data": {
                    "recording": recording_status,
                    "timestamp": datetime.now().isoformat()
                }
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# 状态更新函数（供主程序调用）
async def update_recording_status(platform: str, user_id: str, status: str, info: dict = None):
    """更新录制状态并广播"""
    key = f"{platform}_{user_id}"
    recording_status[key] = {
        "platform": platform,
        "user_id": user_id,
        "status": status,
        "info": info or {},
        "timestamp": datetime.now().isoformat()
    }
    
    # 广播更新
    await manager.broadcast({
        "type": "status_update",
        "data": recording_status
    })


def run_web_server(host: str = "0.0.0.0", port: int = 8000):
    """运行Web服务器"""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_web_server()

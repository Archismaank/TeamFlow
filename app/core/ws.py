from fastapi import WebSocket


class ProjectConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, project_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.setdefault(project_id, []).append(websocket)

    def disconnect(self, project_id: str, websocket: WebSocket):
        connections = self.active_connections.get(project_id, [])
        if websocket in connections:
            connections.remove(websocket)
        if not connections and project_id in self.active_connections:
            del self.active_connections[project_id]

    async def broadcast(self, project_id: str, payload: dict):
        dead_connections: list[WebSocket] = []
        for connection in self.active_connections.get(project_id, []):
            try:
                await connection.send_json(payload)
            except Exception:
                dead_connections.append(connection)

        for dead in dead_connections:
            self.disconnect(project_id, dead)


ws_manager = ProjectConnectionManager()
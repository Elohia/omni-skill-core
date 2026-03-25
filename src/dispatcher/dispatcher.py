"""
高并发触发与路由引擎主入口 (Dispatcher Engine)
"""
from typing import Any, Dict, Optional, Tuple
from concurrent.futures import Future

from .router import RadixRouter, HashRouter
from .nlp_index import TFIDFIndex
from .skill_loader import SkillLazyLoader
from .worker_pool import PrewarmedPool
import config.settings as settings

class DispatcherEngine:
    """高并发触发与路由引擎"""
    def __init__(self, cache_capacity: int = settings.CACHE_CAPACITY, pool_workers: int = settings.WORKER_POOL_SIZE):
        # 初始化四大核心模块
        self.radix_router = RadixRouter()
        self.hash_router = HashRouter()
        self.nlp_index = TFIDFIndex()
        self.skill_loader = SkillLazyLoader(capacity=cache_capacity)
        self.worker_pool = PrewarmedPool(max_workers=pool_workers)

        # 技能注册表
        self.skill_registry: Dict[str, Dict[str, str]] = {}

    def register_skill(self, 
                       skill_id: str, 
                       module_path: str, 
                       class_name: str,
                       trigger_path: Optional[str] = None, 
                       trigger_key: Optional[str] = None, 
                       nlp_desc: Optional[str] = None):
        """注册技能及触发条件"""
        # 记录技能信息
        self.skill_registry[skill_id] = {
            "module_path": module_path,
            "class_name": class_name
        }

        # 绑定触发条件
        if trigger_path:
            self.radix_router.add_route(trigger_path, skill_id)
        if trigger_key:
            self.hash_router.add_route(trigger_key, skill_id)
        if nlp_desc:
            self.nlp_index.add_skill(skill_id, nlp_desc)

    def dispatch(self, route_type: str, payload: str, *args, **kwargs) -> Future:
        """分发路由并异步执行任务"""
        skill_id = None

        # 第一步：匹配路由
        if route_type == "radix":
            skill_id = self.radix_router.match(payload)
        elif route_type == "hash":
            skill_id = self.hash_router.match(payload)
        elif route_type == "nlp":
            matches = self.nlp_index.match(payload, top_k=1)
            if matches:
                skill_id = matches[0][0] # 取出得分最高的 skill_id
        else:
            raise ValueError(f"不支持的路由类型: {route_type}")

        if not skill_id or skill_id not in self.skill_registry:
            raise ValueError("未找到匹配的技能")

        # 第二步：延迟加载并获取技能实例
        registry_info = self.skill_registry[skill_id]
        skill_instance = self.skill_loader.load_skill(
            skill_id,
            registry_info["module_path"],
            registry_info["class_name"]
        )

        if not skill_instance:
            raise RuntimeError(f"技能 {skill_id} 加载失败")

        # 第三步：投入线程池异步执行
        # 假设所有技能实例皆有 execute 方法
        if hasattr(skill_instance, "execute"):
            future = self.worker_pool.execute(skill_instance.execute, *args, **kwargs)
            return future
        else:
            raise TypeError(f"技能 {skill_id} 缺少 execute 方法")
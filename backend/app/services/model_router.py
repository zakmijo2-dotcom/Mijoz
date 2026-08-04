"""
Model Router - Intelligent routing of tasks to optimal models/providers
"""

from typing import Dict, List, Optional, Any
import asyncio
import time
from datetime import datetime
from app.models.router_models import (
    ModelConfig, ModelProvider, TaskContext, TaskType,
    RoutingDecision, RoutingStrategy, ModelHealth
)


class ModelRouter:
    """
    Intelligent model router that selects the best model/provider
    based on task requirements, cost, speed, quality, and availability.
    """
    
    def __init__(self):
        self.models: Dict[str, ModelConfig] = {}
        self.health_status: Dict[str, ModelHealth] = {}
        self.usage_stats: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        
        # Initialize default models
        self._register_default_models()
    
    def _register_default_models(self):
        """Register default model configurations"""
        defaults = [
            # OpenAI Models
            ModelConfig(
                provider=ModelProvider.OPENAI,
                model_name="gpt-4o",
                api_key_env="OPENAI_API_KEY",
                cost_per_million_input=5.0,
                cost_per_million_output=15.0,
                context_window=128000,
                speed_tier=2,
                quality_tier=1,
                is_available=True
            ),
            ModelConfig(
                provider=ModelProvider.OPENAI,
                model_name="gpt-4o-mini",
                api_key_env="OPENAI_API_KEY",
                cost_per_million_input=0.15,
                cost_per_million_output=0.6,
                context_window=128000,
                speed_tier=1,
                quality_tier=3,
                is_available=True
            ),
            
            # Anthropic Models
            ModelConfig(
                provider=ModelProvider.ANTHROPIC,
                model_name="claude-sonnet-4-20250514",
                api_key_env="ANTHROPIC_API_KEY",
                cost_per_million_input=3.0,
                cost_per_million_output=15.0,
                context_window=200000,
                speed_tier=2,
                quality_tier=1,
                is_available=True
            ),
            ModelConfig(
                provider=ModelProvider.ANTHROPIC,
                model_name="claude-opus-4-20250514",
                api_key_env="ANTHROPIC_API_KEY",
                cost_per_million_input=15.0,
                cost_per_million_output=75.0,
                context_window=200000,
                speed_tier=3,
                quality_tier=1,
                is_available=True
            ),
            ModelConfig(
                provider=ModelProvider.ANTHROPIC,
                model_name="claude-haiku-3-5",
                api_key_env="ANTHROPIC_API_KEY",
                cost_per_million_input=0.25,
                cost_per_million_output=1.25,
                context_window=200000,
                speed_tier=1,
                quality_tier=2,
                is_available=True
            ),
            
            # Google Models
            ModelConfig(
                provider=ModelProvider.GOOGLE,
                model_name="gemini-2.5-pro",
                api_key_env="GOOGLE_API_KEY",
                cost_per_million_input=1.25,
                cost_per_million_output=5.0,
                context_window=1000000,
                speed_tier=2,
                quality_tier=2,
                is_available=True
            ),
            ModelConfig(
                provider=ModelProvider.GOOGLE,
                model_name="gemini-2.5-flash",
                api_key_env="GOOGLE_API_KEY",
                cost_per_million_input=0.075,
                cost_per_million_output=0.3,
                context_window=1000000,
                speed_tier=1,
                quality_tier=3,
                is_available=True
            ),
            
            # Groq Models (Ultra-fast)
            ModelConfig(
                provider=ModelProvider.GROQ,
                model_name="llama-3.3-70b-versatile",
                api_key_env="GROQ_API_KEY",
                cost_per_million_input=0.59,
                cost_per_million_output=0.79,
                context_window=128000,
                speed_tier=1,
                quality_tier=2,
                is_available=True
            ),
            ModelConfig(
                provider=ModelProvider.GROQ,
                model_name="mixtral-8x7b-32768",
                api_key_env="GROQ_API_KEY",
                cost_per_million_input=0.24,
                cost_per_million_output=0.24,
                context_window=32000,
                speed_tier=1,
                quality_tier=3,
                is_available=True
            ),
            
            # OpenRouter (Multi-provider)
            ModelConfig(
                provider=ModelProvider.OPENROUTER,
                model_name="meta-llama/llama-3.1-405b-instruct",
                api_key_env="OPENROUTER_API_KEY",
                cost_per_million_input=2.5,
                cost_per_million_output=2.5,
                context_window=32000,
                speed_tier=2,
                quality_tier=2,
                is_available=True
            ),
            
            # Together AI
            ModelConfig(
                provider=ModelProvider.TOGETHER,
                model_name="Qwen/Qwen2.5-Coder-32B-Instruct",
                api_key_env="TOGETHER_API_KEY",
                cost_per_million_input=0.18,
                cost_per_million_output=0.18,
                context_window=32000,
                speed_tier=1,
                quality_tier=2,
                is_available=True
            ),
            
            # Cerebras (Fast inference)
            ModelConfig(
                provider=ModelProvider.CEREBRAS,
                model_name="llama-3.3-70b",
                api_key_env="CEREBRAS_API_KEY",
                cost_per_million_input=0.90,
                cost_per_million_output=0.90,
                context_window=128000,
                speed_tier=1,
                quality_tier=2,
                is_available=True
            ),
            
            # Mistral
            ModelConfig(
                provider=ModelProvider.MISTRAL,
                model_name="mistral-large-latest",
                api_key_env="MISTRAL_API_KEY",
                cost_per_million_input=2.0,
                cost_per_million_output=6.0,
                context_window=128000,
                speed_tier=2,
                quality_tier=2,
                is_available=True
            ),
            ModelConfig(
                provider=ModelProvider.MISTRAL,
                model_name="codestral-latest",
                api_key_env="MISTRAL_API_KEY",
                cost_per_million_input=0.5,
                cost_per_million_output=1.5,
                context_window=32000,
                speed_tier=1,
                quality_tier=2,
                is_available=True
            ),
        ]
        
        for model in defaults:
            key = f"{model.provider.value}:{model.model_name}"
            self.models[key] = model
            self.health_status[key] = ModelHealth(
                provider=model.provider,
                model_name=model.model_name,
                is_healthy=True
            )
            self.usage_stats[key] = {
                "total_requests": 0,
                "total_tokens_input": 0,
                "total_tokens_output": 0,
                "total_cost": 0.0,
                "last_used": None
            }
    
    def register_model(self, config: ModelConfig):
        """Register a custom model configuration"""
        key = f"{config.provider.value}:{config.model_name}"
        self.models[key] = config
        self.health_status[key] = ModelHealth(
            provider=config.provider,
            model_name=config.model_name,
            is_healthy=True
        )
        self.usage_stats[key] = {
            "total_requests": 0,
            "total_tokens_input": 0,
            "total_tokens_output": 0,
            "total_cost": 0.0,
            "last_used": None
        }
    
    def unregister_model(self, provider: ModelProvider, model_name: str):
        """Unregister a model"""
        key = f"{provider.value}:{model_name}"
        if key in self.models:
            del self.models[key]
        if key in self.health_status:
            del self.health_status[key]
        if key in self.usage_stats:
            del self.usage_stats[key]
    
    async def route_task(
        self,
        task_context: TaskContext,
        strategy: RoutingStrategy = RoutingStrategy.BALANCED,
        excluded_models: Optional[List[str]] = None
    ) -> RoutingDecision:
        """
        Route a task to the optimal model based on strategy and context.
        """
        async with self._lock:
            available_models = []
            
            for key, config in self.models.items():
                # Skip excluded models
                if excluded_models and key in excluded_models:
                    continue
                
                # Skip unavailable models
                if not config.is_available:
                    continue
                
                # Check health status
                health = self.health_status.get(key)
                if health and not health.is_healthy:
                    continue
                
                # Check context window
                if task_context.required_context > config.context_window:
                    continue
                
                available_models.append((key, config, health))
            
            if not available_models:
                return RoutingDecision(
                    selected_model="",
                    selected_provider=ModelProvider.OPENAI,
                    reasoning="No available models found",
                    fallback_options=[]
                )
            
            # Score each model based on strategy
            scored_models = []
            for key, config, health in available_models:
                score = self._calculate_score(
                    config, health, task_context, strategy
                )
                scored_models.append((key, config, health, score))
            
            # Sort by score (higher is better)
            scored_models.sort(key=lambda x: x[3], reverse=True)
            
            # Select best model
            best_key, best_config, best_health, best_score = scored_models[0]
            
            # Calculate estimated cost and time
            estimated_cost = self._estimate_cost(
                best_config, task_context.required_context
            )
            estimated_time = self._estimate_time(best_config, task_context)
            
            # Get fallback options (top 3 alternatives)
            fallback_options = [
                scored_models[i][0] 
                for i in range(1, min(4, len(scored_models)))
            ]
            
            # Generate reasoning
            reasoning = self._generate_reasoning(
                best_config, task_context, strategy, best_score
            )
            
            # Update usage stats
            self.usage_stats[best_key]["total_requests"] += 1
            self.usage_stats[best_key]["last_used"] = time.time()
            
            return RoutingDecision(
                selected_model=best_config.model_name,
                selected_provider=best_config.provider,
                reasoning=reasoning,
                estimated_cost=estimated_cost,
                estimated_time=estimated_time,
                fallback_options=fallback_options
            )
    
    def _calculate_score(
        self,
        config: ModelConfig,
        health: Optional[ModelHealth],
        task_context: TaskContext,
        strategy: RoutingStrategy
    ) -> float:
        """Calculate a score for a model based on strategy"""
        base_score = 100.0
        
        # Health factor
        if health:
            base_score *= health.success_rate
            if health.response_time_avg > 5.0:
                base_score *= 0.9
        
        # Strategy-specific scoring
        if strategy == RoutingStrategy.COST_OPTIMIZED:
            # Prioritize low cost
            cost_factor = 1.0 / (config.cost_per_million_input + 
                                config.cost_per_million_output + 0.01)
            base_score *= (cost_factor / 100.0)
            
        elif strategy == RoutingStrategy.SPEED_OPTIMIZED:
            # Prioritize speed
            speed_factor = (6 - config.speed_tier) / 5.0
            base_score *= (1.0 + speed_factor)
            
        elif strategy == RoutingStrategy.QUALITY_OPTIMIZED:
            # Prioritize quality
            quality_factor = (6 - config.quality_tier) / 5.0
            base_score *= (1.0 + quality_factor * 0.5)
            
            # Bonus for complex tasks
            if task_context.complexity >= 4:
                base_score *= 1.2
                
        elif strategy == RoutingStrategy.CONTEXT_AWARE:
            # Balance based on task type
            if task_context.task_type == TaskType.ARCHITECTURE:
                # Prefer high quality for architecture
                quality_factor = (6 - config.quality_tier) / 5.0
                base_score *= (1.0 + quality_factor * 0.3)
            elif task_context.task_type == TaskType.QUICK_FIX:
                # Prefer speed for quick fixes
                speed_factor = (6 - config.speed_tier) / 5.0
                base_score *= (1.0 + speed_factor * 0.3)
            elif task_context.task_type == TaskType.REVIEW:
                # Prefer quality for reviews
                quality_factor = (6 - config.quality_tier) / 5.0
                base_score *= (1.0 + quality_factor * 0.4)
        
        # Budget sensitivity adjustment
        if task_context.budget_sensitivity >= 4:
            cost_penalty = (config.cost_per_million_input + 
                          config.cost_per_million_output) * 0.1
            base_score -= cost_penalty
        
        # Urgency adjustment - prefer faster models for urgent tasks
        if task_context.urgency >= 4:
            speed_bonus = (6 - config.speed_tier) * 2.0
            base_score += speed_bonus
        
        return base_score
    
    def _estimate_cost(
        self, 
        config: ModelConfig, 
        context_tokens: int
    ) -> float:
        """Estimate the cost for a task"""
        input_cost = (context_tokens / 1_000_000) * config.cost_per_million_input
        # Assume output is ~30% of input for estimation
        output_tokens = int(context_tokens * 0.3)
        output_cost = (output_tokens / 1_000_000) * config.cost_per_million_output
        return round(input_cost + output_cost, 6)
    
    def _estimate_time(
        self, 
        config: ModelConfig, 
        task_context: TaskContext
    ) -> float:
        """Estimate execution time in seconds"""
        # Base time inversely proportional to speed tier
        base_time = config.speed_tier * 0.5
        
        # Add time for complexity
        complexity_factor = task_context.complexity * 0.3
        
        # Add time for context size
        context_factor = (task_context.required_context / 1000) * 0.01
        
        return round(base_time + complexity_factor + context_factor, 2)
    
    def _generate_reasoning(
        self,
        config: ModelConfig,
        task_context: TaskContext,
        strategy: RoutingStrategy,
        score: float
    ) -> str:
        """Generate human-readable reasoning for the routing decision"""
        reasons = []
        
        reasons.append(f"Selected {config.model_name} ({config.provider.value})")
        
        if strategy == RoutingStrategy.COST_OPTIMIZED:
            reasons.append(f"due to low cost (${config.cost_per_million_input}/1M input)")
        elif strategy == RoutingStrategy.SPEED_OPTIMIZED:
            reasons.append(f"for fast execution (speed tier {config.speed_tier})")
        elif strategy == RoutingStrategy.QUALITY_OPTIMIZED:
            reasons.append(f"for high quality output (quality tier {config.quality_tier})")
        
        if task_context.task_type == TaskType.ARCHITECTURE:
            reasons.append("- ideal for architectural decisions")
        elif task_context.task_type == TaskType.TESTING:
            reasons.append("- suitable for test generation")
        elif task_context.task_type == TaskType.SECURITY:
            reasons.append("- recommended for security analysis")
        
        if task_context.urgency >= 4:
            reasons.append("(prioritized due to high urgency)")
        
        if task_context.budget_sensitivity >= 4:
            reasons.append("(cost-optimized due to budget constraints)")
        
        return " ".join(reasons)
    
    async def update_health(
        self,
        provider: ModelProvider,
        model_name: str,
        success: bool,
        response_time: float,
        error_message: Optional[str] = None
    ):
        """Update health status based on request result"""
        key = f"{provider.value}:{model_name}"
        
        if key not in self.health_status:
            return
        
        health = self.health_status[key]
        health.last_check = time.time()
        
        # Update success rate with exponential moving average
        alpha = 0.1
        if success:
            health.success_rate = alpha * 1.0 + (1 - alpha) * health.success_rate
            health.error_count = max(0, health.error_count - 1)
        else:
            health.success_rate = alpha * 0.0 + (1 - alpha) * health.success_rate
            health.error_count += 1
            health.last_error = error_message
        
        # Update average response time
        n = health.response_time_avg
        health.response_time_avg = n + (response_time - n) / 10
        
        # Mark as unhealthy if too many errors
        if health.error_count >= 5 or health.success_rate < 0.5:
            health.is_healthy = False
        elif health.error_count == 0 and health.success_rate > 0.9:
            health.is_healthy = True
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get aggregated usage statistics"""
        total_requests = sum(
            stats["total_requests"] for stats in self.usage_stats.values()
        )
        total_cost = sum(
            stats["total_cost"] for stats in self.usage_stats.values()
        )
        total_tokens_input = sum(
            stats["total_tokens_input"] for stats in self.usage_stats.values()
        )
        total_tokens_output = sum(
            stats["total_tokens_output"] for stats in self.usage_stats.values()
        )
        
        return {
            "total_requests": total_requests,
            "total_cost": round(total_cost, 2),
            "total_tokens_input": total_tokens_input,
            "total_tokens_output": total_tokens_output,
            "models_used": len([
                k for k, v in self.usage_stats.items() 
                if v["total_requests"] > 0
            ]),
            "by_model": self.usage_stats
        }
    
    def get_available_models(
        self, 
        provider: Optional[ModelProvider] = None,
        only_healthy: bool = True
    ) -> List[Dict[str, Any]]:
        """Get list of available models"""
        results = []
        
        for key, config in self.models.items():
            if provider and config.provider != provider:
                continue
            
            health = self.health_status.get(key)
            if only_healthy and health and not health.is_healthy:
                continue
            
            results.append({
                "key": key,
                "provider": config.provider.value,
                "model_name": config.model_name,
                "context_window": config.context_window,
                "cost_per_million_input": config.cost_per_million_input,
                "cost_per_million_output": config.cost_per_million_output,
                "speed_tier": config.speed_tier,
                "quality_tier": config.quality_tier,
                "is_available": config.is_available,
                "is_healthy": health.is_healthy if health else False,
                "supports_function_calling": config.supports_function_calling
            })
        
        return results


# Global instance
model_router = ModelRouter()

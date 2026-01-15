"""
Base agent class with common functionality
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os
import yaml
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage

# Configure LangSmith tracing
os.environ.setdefault("LANGSMITH_TRACING", "true")
os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
os.environ.setdefault("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
# LANGSMITH_API_KEY and LANGCHAIN_PROJECT should be set in .env


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.
    Provides common functionality like LLM initialization and configuration loading.
    """
    
    def __init__(
        self,
        agent_name: str,
        config_path: Optional[str] = None
    ):
        self.agent_name = agent_name
        self.config = self._load_config(config_path)
        self.llm = self._initialize_llm()
        
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load agent configuration from YAML"""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "agents.yaml"
        
        with open(config_path, 'r') as f:
            all_configs = yaml.safe_load(f)
        
        # Get specific agent config
        agent_config = all_configs.get(self.agent_name, {})
        
        # Merge with global config
        global_config = all_configs.get('global', {})
        return {**global_config, **agent_config}
    
    def _initialize_llm(self):
        """Initialize the LLM based on configuration"""
        model_name = self.config.get('model', 'gpt-4o-mini')
        temperature = self.config.get('temperature', 0.0)
        max_tokens = self.config.get('max_tokens', 2000)
        
        # LangSmith metadata for tracing
        metadata = {
            "agent_name": self.agent_name,
            "model": model_name
        }
        tags = [self.agent_name, "executive-analytics"]
        
        # Determine provider from model name
        if model_name.startswith('gpt'):
            return ChatOpenAI(
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=os.getenv('OPENAI_API_KEY'),
                metadata=metadata,
                tags=tags
            )
        elif model_name.startswith('claude'):
            return ChatAnthropic(
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=os.getenv('ANTHROPIC_API_KEY'),
                metadata=metadata,
                tags=tags
            )
        else:
            raise ValueError(f"Unsupported model: {model_name}")
    
    def invoke_llm(
        self,
        user_message: str,
        system_message: Optional[str] = None
    ) -> str:
        """
        Invoke the LLM with a user message and optional system message
        
        Args:
            user_message: The user's prompt
            system_message: Optional system prompt (uses config default if not provided)
            
        Returns:
            The LLM's response as a string
        """
        messages = []
        
        # Add system message
        sys_msg = system_message or self.config.get('system_prompt', '')
        if sys_msg:
            messages.append(SystemMessage(content=sys_msg))
        
        # Add user message
        messages.append(HumanMessage(content=user_message))
        
        # Invoke LLM
        response = self.llm.invoke(messages)
        return response.content
    
    @abstractmethod
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the current state and return updates.
        This method must be implemented by all agent subclasses.
        
        Args:
            state: The current workflow state
            
        Returns:
            Dictionary with state updates
        """
        pass
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.agent_name}, model={self.config.get('model')})"

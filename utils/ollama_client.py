"""
Ollama client for Qwen vision models with function calling support.
"""
import json
import base64
from typing import List, Dict, Any, Optional
import io

import ollama
from PIL import Image

import config


class OllamaVisionClient:
    """Client for interacting with Qwen vision models via Ollama."""
    
    def __init__(
        self,
        model: str = config.MODEL_NAME,
        options: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Ollama client
        
        Args:
            model: Model name to use
            options: Ollama generation options
        """

        self.model = model
        self.options = dict(config.MODEL_OPTIONS if options is None else options)
        self.client = ollama

    def _to_plain_data(self, value):
        """Convert Ollama response objects to dict/list primitives."""
        if hasattr(value, "model_dump"):
            return self._to_plain_data(value.model_dump())
        if isinstance(value, dict):
            return {key: self._to_plain_data(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self._to_plain_data(item) for item in value]
        return value

    def _print_connection_help(self) -> None:
        """Print the command a user can try when Ollama/model setup fails."""
        print("\nERROR: Failed to initialize Ollama client")
        print("Make sure Ollama is running and the model is pulled or available:")
        print(f"  ollama run {self.model}")

        
    def encode_image_to_base64(self, image: Image.Image, format: str = 'PNG') -> str:
        """
        Encode PIL Image to base64 string
        
        Args:
            image: PIL Image object
            format: Image format (PNG, JPEG, etc.)
            
        Returns:
            Base64 encoded string
        """
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        img_bytes = buffer.getvalue()
        return base64.b64encode(img_bytes).decode('utf-8')
    
    def chat(self, 
             messages: List[Dict[str, Any]], 
             stream: bool = False,
             tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Send chat request to Ollama with vision support
        
        Args:
            messages: List of message dictionaries
            stream: Whether to stream the response
            tools: Optional list of tool definitions for function calling
            
        Returns:
            Response dictionary from Ollama
        """
        try:
            # Prepare the request
            request_params = {
                'model': self.model,
                'messages': messages,
                'stream': stream,
                'options': self.options,
            }
            
            # Add tools if provided
            if tools:
                request_params['tools'] = tools
            
            # Make the request
            response = self.client.chat(**request_params)
            
            return self._to_plain_data(response)
            
        except Exception as e:
            print(f"Error in Ollama chat: {e}")
            raise
    
    def chat_with_image(self,
                       user_query: str,
                       image: Image.Image,
                       system_prompt: Optional[str] = None,
                       tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Chat with image input
        
        Args:
            user_query: User's text query
            image: PIL Image object
            system_prompt: Optional system prompt
            tools: Optional list of tool definitions
            
        Returns:
            Response from the model
        """
        # Build messages
        messages = []
        
        # Add system message if provided
        if system_prompt:
            messages.append({
                'role': 'system',
                'content': system_prompt
            })
        
        # Encode image to base64
        image_base64 = self.encode_image_to_base64(image, format='PNG')
        
        # Add user message with image
        messages.append({
            'role': 'user',
            'content': user_query,
            'images': [image_base64]
        })
        
        # Make the request
        response = self.chat(messages=messages, tools=tools)
        
        return response
    
    def extract_tool_calls(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract tool calls from model response
        
        Args:
            response: Response from Ollama
            
        Returns:
            List of tool call dictionaries
        """
        tool_calls = []
        
        if 'message' in response:
            message = response['message']
            
            # Check for tool_calls in the message
            if 'tool_calls' in message:
                tool_calls = message['tool_calls']
        
        return tool_calls
    
    def parse_computer_use_action(self, response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse computer use action from model response
        
        Args:
            response: Response from Ollama
            
        Returns:
            Parsed action dictionary or None
        """
        # Try to extract tool calls
        tool_calls = self.extract_tool_calls(response)
        
        if tool_calls:
            return tool_calls[0]
        
        # Fallback: try to parse from content
        if 'message' in response and 'content' in response['message']:
            content = response['message']['content']
            
            # Look for tool_call markers
            if '<tool_call>' in content and '</tool_call>' in content:
                try:
                    json_str = content.split('<tool_call>')[1].split('</tool_call>')[0].strip()
                    action = json.loads(json_str)
                    return action
                except (json.JSONDecodeError, IndexError) as e:
                    print(f"Error parsing tool call: {e}")
        
        return None
    
    def test_connection(self) -> bool:
        """
        Test connection to Ollama and that the configured model can answer.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Try to list models
            models = self.client.list()

            # Check if our model is available
            available_models = getattr(models, 'models', None)
            if available_models is None and isinstance(models, dict):
                available_models = models.get('models', [])

            model_names = []
            for model in available_models or []:
                if isinstance(model, dict):
                    model_name = model.get('model') or model.get('name')
                else:
                    model_name = getattr(model, 'model', None) or getattr(model, 'name', None)

                if model_name:
                    model_names.append(model_name)

            if self.model in model_names or any(self.model in name for name in model_names):
                print(f"OK: Model '{self.model}' is available")
            else:
                try:
                    self.client.show(self.model)
                    print(f"OK: Model '{self.model}' metadata is available")
                except Exception:
                    print(f"ERROR: Model '{self.model}' not found")
                    print(f"Available models: {model_names}")
                    self._print_connection_help()
                    return False

            self.client.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": "Connection check. Reply with OK.",
                    }
                ],
                stream=False,
                options=self.options,
            )
            print(f"OK: Model '{self.model}' answered a chat request")
            return True

        except Exception as e:
            print(f"ERROR: Could not connect to Ollama: {e}")
            self._print_connection_help()
            return False


if __name__ == "__main__":
    # Test the Ollama client
    client = OllamaVisionClient()
    
    print("Testing Ollama connection...")
    if client.test_connection():
        print("\nOK: Ollama client initialized successfully")
    else:
        print("\nERROR: Failed to initialize Ollama client")
        print("Make sure Ollama is running and the model is pulled:")
        print(f"  ollama run {client.model}")

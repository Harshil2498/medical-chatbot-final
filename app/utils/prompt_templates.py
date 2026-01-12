# app/utils/prompt_templates.py
from typing import List, Dict, Any, Optional


class PromptTemplates:
    """Templates for LLM prompts"""
    
    @staticmethod
    def build_rag_prompt(
        query: str,
        context_documents: List[Dict[str, Any]],
        conversation_history: Optional[List] = None,
        additional_context: str = ""
    ) -> str:
        """Build RAG prompt with context"""
        
        # Build context section
        context_parts = []
        for i, doc in enumerate(context_documents, 1):
            metadata = doc.get('metadata', {})
            title = metadata.get('title', 'Unknown Source')
            context_parts.append(
                f"[Source {i}: {title}]\n{doc['document']}\n"
            )
        
        context = "\n".join(context_parts)
        
        # Build conversation history
        history_text = ""
        if conversation_history:
            history_parts = []
            for msg in conversation_history[-3:]:  # Last 3 messages
                history_parts.append(f"{msg.role.upper()}: {msg.content}")
            history_text = "\n".join(history_parts) + "\n\n"
        
        # Add any additional context (like vitals)
        extra_context = ""
        if additional_context:
            extra_context = f"\nADDITIONAL CONTEXT:\n{additional_context}\n"
        
        # Complete prompt
        prompt = f"""You are a helpful medical information assistant. Answer questions based ONLY on the provided context below.

IMPORTANT INSTRUCTIONS:
1. Use ONLY information from the context provided
2. If the context doesn't contain relevant information, say "I don't have enough information to answer that."
3. Cite which source number you used (e.g., "According to Source 1...")
4. Be concise but comprehensive
5. This is NOT medical advice - remind users to consult healthcare professionals for diagnosis or treatment

CONTEXT:
{context}
{extra_context}
{history_text}USER QUESTION: {query}

ANSWER:"""
        
        return prompt
    
    @staticmethod
    def build_conversation_prompt(query: str, history: List) -> str:
        """Build prompt for conversation without RAG"""
        history_text = ""
        if history:
            for msg in history[-5:]:
                history_text += f"{msg.role.upper()}: {msg.content}\n"
        
        return f"""{history_text}
USER: {query}
ASSISTANT:"""
#!/usr/bin/env python3
"""
Interview Agent Client - Example usage of the /api/interview endpoint.

This script demonstrates:
1. Starting a new interview session
2. Sending candidate responses
3. Handling interview completion and feedback

Usage:
    # Run the server first
    python -m uvicorn main:app --reload

    # In another terminal
    python client.py

Requirements:
    pip install httpx
"""

import httpx
import json
import asyncio
import sys
from typing import Optional

BASE_URL = "http://localhost:8000"

class InterviewClient:
    """Client for the Interview Agent API."""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
        self.session_id: Optional[str] = None
        self.interview_active = False
    
    async def start_interview(self, candidate_id: str, name: str, job_role: str, years: int) -> str:
        """Start a new interview session."""
        print(f"\n{'='*60}")
        print(f"Starting interview for: {name}")
        print(f"{'='*60}")
        
        # Generate session ID
        import uuid
        self.session_id = f"session-{uuid.uuid4().hex[:8]}"
        
        payload = {
            "sessionId": self.session_id,
            "candidate": {
                "id": candidate_id,
                "name": name,
                "jobRole": job_role,
                "yearsExperience": years,
                "education": "MS Computer Science",
                "status": "COMPLETED"
            }
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/interview",
                json=payload,
                timeout=30.0
            )
            
            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                print(response.text)
                return ""
            
            data = response.json()
            self.interview_active = not data.get("done", False)
            
            reply = data.get("reply", "")
            print(f"\n🤖 Interviewer:\n{reply}\n")
            
            return reply
        
        except Exception as e:
            print(f"Error starting interview: {e}")
            return ""
    
    async def send_response(self, message: str) -> tuple[str, bool]:
        """Send a candidate response and get interviewer's next message."""
        
        if not self.session_id:
            print("Error: No active session")
            return "", True
        
        print(f"📝 You: {message}\n")
        
        payload = {
            "sessionId": self.session_id,
            "message": message
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/interview",
                json=payload,
                timeout=30.0
            )
            
            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                print(response.text)
                return "", True
            
            data = response.json()
            is_done = data.get("done", False)
            reply = data.get("reply", "")
            
            if is_done:
                print(f"🤖 Interviewer:\n{reply}\n")
                
                # Show feedback if available
                feedback = data.get("feedback")
                if feedback:
                    print(f"\n{'='*60}")
                    print("INTERVIEW FEEDBACK")
                    print(f"{'='*60}\n")
                    
                    print(f"📋 Summary:\n{feedback.get('summary', 'N/A')}\n")
                    
                    strengths = feedback.get('strengths', [])
                    if strengths:
                        print("✅ Strengths:")
                        for s in strengths:
                            print(f"  • {s}")
                        print()
                    
                    gaps = feedback.get('gaps', [])
                    if gaps:
                        print("⚠️  Areas for Improvement:")
                        for g in gaps:
                            print(f"  • {g}")
                        print()
                    
                    next_steps = feedback.get('next', [])
                    if next_steps:
                        print("📚 Recommended Review:")
                        for n in next_steps:
                            print(f"  • {n}")
                        print()
                    
                    print(f"{'='*60}\n")
            else:
                print(f"🤖 Interviewer:\n{reply}\n")
            
            return reply, is_done
        
        except Exception as e:
            print(f"Error sending response: {e}")
            return "", True
    
    async def close(self):
        """Close the client."""
        await self.client.aclose()

async def interactive_interview():
    """Run an interactive interview session."""
    
    client = InterviewClient()
    
    try:
        # Start interview
        await client.start_interview(
            candidate_id="CAND-001",
            name="Sarah Johnson",
            job_role="Senior Data Engineer",
            years=9
        )
        
        if not client.session_id:
            print("Failed to start interview")
            return
        
        # Example responses
        responses = [
            "Embeddings are numerical representations of text that capture semantic meaning. I learned about this on Day 7 of the cohort. They're really useful for semantic search because they preserve the context and meaning of words.",
            
            "In a RAG system, embeddings are used to retrieve relevant documents from the knowledge base. You first embed the user's question, then search for similar embeddings in your vector database to find relevant documents. Those documents are then passed as context to the LLM.",
            
            "I would use a vector database like ChromaDB or Pinecone. ChromaDB is great for local development because it's lightweight and in-memory, while Pinecone is better for production because it's managed and scalable. I actually used ChromaDB first during the cohort.",
        ]
        
        # Interactive loop (can also get user input)
        print("\n" + "="*60)
        print("AUTOMATIC TEST MODE")
        print("(Using pre-written responses)")
        print("="*60)
        
        for i, response in enumerate(responses, 1):
            print(f"\n--- Response {i}/3 ---")
            _, is_done = await client.send_response(response)
            
            if is_done:
                print("\n✅ Interview completed!")
                break
            
            # Small delay between responses
            await asyncio.sleep(1)
        
    finally:
        await client.close()

async def list_candidates_demo():
    """Show how to list available candidates."""
    print("\n" + "="*60)
    print("AVAILABLE CANDIDATES")
    print("="*60 + "\n")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/candidates", timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                candidates = data.get('candidates', [])
                for i, cand_id in enumerate(candidates[:5], 1):
                    print(f"{i}. {cand_id}")
                if len(candidates) > 5:
                    print(f"... and {len(candidates) - 5} more")
                print(f"\nTotal: {len(candidates)} candidates")
            else:
                print("Failed to fetch candidates")
    except Exception as e:
        print(f"Error: {e}")

async def main():
    """Main entry point."""
    
    print("""
╔════════════════════════════════════════════════════════════╗
║     AI Interview Agent - Client Demo                       ║
║                                                            ║
║  Make sure the server is running:                          ║
║    python -m uvicorn main:app --reload                     ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Check if server is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health", timeout=2.0)
            if response.status_code == 200:
                print("✅ Server is running\n")
            else:
                print("❌ Server returned error\n")
                return
    except Exception as e:
        print(f"❌ Cannot connect to server at {BASE_URL}")
        print(f"   Make sure it's running: python -m uvicorn main:app --reload\n")
        return
    
    # Show candidates
    await list_candidates_demo()
    
    # Run interactive interview
    print("\n" + "="*60)
    print("RUNNING TEST INTERVIEW")
    print("="*60)
    
    await interactive_interview()
    
    print("\n✨ Demo complete!\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

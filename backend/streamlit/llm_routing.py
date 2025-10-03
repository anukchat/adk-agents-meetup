import streamlit as st
from src.utils.llm import call_llm
from chatgpt_ui import render_chatgpt_ui
from llm_retry_utils import llm_handle_send_with_retry, llm_handle_retry


# Define routing categories and their downstream handlers
ROUTING_CATEGORIES = {
    "general_question": {
        "name": "General Question",
        "description": "General inquiries that need informational responses",
        "prompt_template": "You are a helpful assistant. Answer the following question clearly and concisely: {user_input}",
        "icon": "❓"
    },
    "refund_request": {
        "name": "Refund Request", 
        "description": "Requests for refunds or billing issues",
        "prompt_template": "You are a customer service representative handling refund requests. Process this refund request professionally and provide next steps: {user_input}",
        "icon": "💰"
    },
    "technical_support": {
        "name": "Technical Support",
        "description": "Technical issues requiring troubleshooting",
        "prompt_template": "You are a technical support specialist. Diagnose and provide step-by-step solutions for this technical issue: {user_input}",
        "icon": "🔧"
    },
    "content_creation": {
        "name": "Content Creation",
        "description": "Requests for creating content like blog posts, emails, etc.",
        "prompt_template": "You are a professional content writer. Create high-quality content based on this request: {user_input}",
        "icon": "✍️"
    },
    "data_analysis": {
        "name": "Data Analysis",
        "description": "Questions about data interpretation or analysis",
        "prompt_template": "You are a data analyst. Analyze the following request and provide insights with recommendations: {user_input}",
        "icon": "📊"
    }
}


def classify_user_input(user_input: str) -> str:
    """
    Use LLM to classify user input into one of the predefined routing categories.
    """
    categories_list = "\n".join([
        f"- {key}: {info['description']}" 
        for key, info in ROUTING_CATEGORIES.items()
    ])
    
    prompt = [
        {"role": "system", "content": f"""
You are a routing classifier. Analyze the user input and classify it into ONE of these categories:

{categories_list}

Respond with ONLY the category key (e.g., 'general_question', 'refund_request', etc.).
If the input doesn't clearly fit any category, use 'general_question' as default.
"""},
        {"role": "user", "content": user_input}
    ]
    
    response = call_llm(prompt)
    classification = response.choices[0].message.content.strip().lower()
    
    # Validate classification is in our categories
    if classification not in ROUTING_CATEGORIES:
        classification = "general_question"
    
    return classification


def process_routed_request(user_input: str, category: str) -> str:
    """
    Process the user request using the appropriate downstream handler based on classification.
    """
    category_info = ROUTING_CATEGORIES[category]
    specialized_prompt = category_info["prompt_template"].format(user_input=user_input)
    
    prompt = [
        {"role": "system", "content": specialized_prompt}
    ]
    
    response = call_llm(prompt)
    return response.choices[0].message.content.strip()


def main():
    st.title("🧭 LLM-Based Routing Demo")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "error" not in st.session_state:
        st.session_state["error"] = False
    if "last_user_input" not in st.session_state:
        st.session_state["last_user_input"] = None
    if "routing_stats" not in st.session_state:
        st.session_state["routing_stats"] = {}

    # Display routing categories in sidebar
    with st.expander("🎯 Available Routing Categories", expanded=False):
        for key, info in ROUTING_CATEGORIES.items():
            st.markdown(f"**{info['icon']} {info['name']}**")
            st.caption(info['description'])
            st.markdown("---")

    def handle_send(user_input):
        def llm_call(messages):
            # Step 1: Classify the input
            classification = classify_user_input(user_input)
            category_info = ROUTING_CATEGORIES[classification]
            
            # Update routing stats
            if classification not in st.session_state["routing_stats"]:
                st.session_state["routing_stats"][classification] = 0
            st.session_state["routing_stats"][classification] += 1
            
            # Step 2: Process with specialized handler
            specialized_response = process_routed_request(user_input, classification)
            
            # Format the response to show routing decision
            formatted_response = f"""**🧭 Routing Decision:** {category_info['icon']} {category_info['name']}

**Response:**
{specialized_response}

---
*This query was automatically classified as "{category_info['name']}" and processed using specialized prompts and logic for this category.*"""
            
            # Overwrite the last user message with the original input for retry
            if messages and messages[-1]["role"] == "user":
                messages[-1]["content"] = user_input
                
            return type('Obj', (object,), {
                "choices": [type('Choice', (object,), {
                    "message": type('Msg', (object,), {
                        "content": formatted_response
                    })()
                })()]
            })()

        llm_handle_send_with_retry(
            user_input,
            messages_key="messages",
            last_user_input_key="last_user_input", 
            error_key="error",
            llm_call_fn=llm_call
        )

    def handle_retry():
        llm_handle_retry(
            messages_key="messages",
            last_user_input_key="last_user_input",
            error_key="error", 
            handle_send_fn=handle_send
        )

    # Display routing statistics
    if st.session_state["routing_stats"]:
        with st.expander("📈 Routing Statistics", expanded=False):
            for category, count in st.session_state["routing_stats"].items():
                category_info = ROUTING_CATEGORIES[category]
                st.metric(
                    f"{category_info['icon']} {category_info['name']}", 
                    count
                )

    render_chatgpt_ui(
        st.session_state["messages"],
        input_key="user_input_routing",
        on_send=handle_send,
        on_retry=handle_retry,
        placeholder="Ask any question - I'll automatically route it to the right specialist! (e.g., 'I need a refund', 'How do I fix my login?', 'Write a blog post about AI')"
    )


if __name__ == "__main__":
    main()

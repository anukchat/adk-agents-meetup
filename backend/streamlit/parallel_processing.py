"""
Student-Friendly Parallel Research with LLM-generated Report
"""

from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
import operator
from src.utils.llm import call_llm
from src.tools.serper_search import serper_search

# ---- STATE ----
class ResearchState(TypedDict):
    user_query: str
    sub_queries: Annotated[List[str], operator.add]
    notes: Annotated[List[str], operator.add]
    report_md: str

# ---- NODES ----
def plan_queries(state: ResearchState) -> ResearchState:
    """LLM creates a few search queries from the user query."""
    prompt = [
        {"role": "system", "content": "Turn the user question into 3-5 useful web search queries."},
        {"role": "user", "content": state["user_query"]}
    ]
    resp = call_llm(prompt)
    queries = [q.strip("-• ") for q in resp.choices[0].message.content.splitlines() if q.strip()]
    return {"sub_queries": queries[:5]}

def dispatch_research(state: ResearchState):
    """Send each query to a parallel research worker."""
    return [Send("research_worker", {"sub_queries": [q]}) for q in state["sub_queries"]]

def research_worker(state: ResearchState) -> ResearchState:
    """Run a single search query and summarize results."""
    q = state["sub_queries"][0]
    results = serper_search(q).get("organic", [])[:3]  # take top 3 results
    
    # Prepare text with URLs for LLM
    text_with_urls = []
    for r in results:
        title = r.get('title', '')
        snippet = r.get('snippet', '')
        url = r.get('link', '')
        text_with_urls.append(f"- {title}: {snippet}\n  URL: {url}")
    
    text = "\n".join(text_with_urls)
    
    prompt = [
        {"role": "system", "content": "Summarize these search results in 3-4 bullet points and include citations with the provided URLs."},
        {"role": "user", "content": text}
    ]
    summary = call_llm(prompt).choices[0].message.content.strip()
    
    return {"notes": [f"### {q}\n{summary}\n"]}

def aggregate(state: ResearchState) -> ResearchState:
    """Use LLM to write a detailed research report in Markdown."""
    all_notes = "\n".join(state["notes"])
    prompt = [
        {"role": "system", "content": (
            "You are a senior research writer. Write a **detailed Markdown research report including citations urls** "
            "based on the notes. Include:\n"
            "- Title\n"
            "- Executive Summary\n"
            "- Key Findings\n"
            "- Analysis & Discussion\n"
            "- Risks or Gaps\n"
            "- Recommendations / Next Steps\n"
            "- References (with clickable URLs)\n\n"
            "IMPORTANT: Make sure to include ALL the URLs from the research notes as clickable links in markdown format [text](url). "
            "Create a References section at the end with all source URLs."
        )},
        {"role": "user", "content": f"User Query: {state['user_query']}\n\nResearch Notes:\n{all_notes}"}
    ]
    resp = call_llm(prompt)
    return {"report_md": resp.choices[0].message.content.strip()}

# ---- GRAPH BUILDER ----
def build_graph():
    g = StateGraph(ResearchState)
    g.add_node("plan_queries", plan_queries)
    g.add_node("research_worker", research_worker)
    g.add_node("aggregate", aggregate)

    g.add_edge(START, "plan_queries")
    g.add_conditional_edges(
        "plan_queries", 
        dispatch_research,
        # This path mapping helps visualization
        path_map=["research_worker"]
    )
    g.add_edge("research_worker", "aggregate")
    g.add_edge("aggregate", END)

    return g.compile()

# ---- RUNNER ----
def run(user_query: str) -> str:
    graph = build_graph()
    init = {"user_query": user_query, "sub_queries": [], "notes": [], "report_md": ""}
    final = graph.invoke(init)
    return final["report_md"]

# ---- STREAMLIT INTERFACE ----
def main():
    """Streamlit interface for parallel research workflow."""
    import streamlit as st
    
    st.title("🔍 Parallel Research with LangGraph")
    st.write("Enter a research question to generate a comprehensive report using parallel web searches.")
    
    # Show workflow graph visualization
    if st.checkbox("📊 Show Workflow Graph", value=True):
        try:
            graph = build_graph()
            mermaid_png = graph.get_graph().draw_mermaid_png()
            st.image(mermaid_png, caption="LangGraph Workflow Visualization", width=200)
            
            # Add explanation of parallel execution
            st.info("""
            **📝 How Parallel Execution Works:**
            1. **plan_queries** → breaks down the research question into multiple search queries
            2. **research_worker** → runs in parallel for each query (multiple instances simultaneously)  
            3. **aggregate** → combines all parallel results into a final report
            
            *Note: The graph shows one 'research_worker' node, but it executes in parallel instances based on the number of queries generated.*
            """)
        except Exception as e:
            st.warning(f"Could not generate graph visualization: {e}")
    
    # Input
    user_query = st.text_input(
        "Research Question", 
        placeholder="e.g., Impact of renewable energy on global economy 2025",
        help="Enter any topic you'd like to research. The system will break it down into multiple search queries and run them in parallel."
    )
    
    if st.button("🚀 Generate Research Report", type="primary"):
        if not user_query.strip():
            st.warning("Please enter a research question.")
            return
            
        try:
            # Create containers for step-by-step visualization
            step1_container = st.container()
            step2_container = st.container()
            step3_container = st.container()
            step4_container = st.container()
            
            with step1_container:
                st.markdown("### 🔍 Step 1: Query Planning")
                with st.spinner("Breaking down your question into focused search queries..."):
                    # Execute just the planning step
                    graph = build_graph()
                    init_state = {"user_query": user_query, "sub_queries": [], "notes": [], "report_md": ""}
                    
                    # Get planned queries
                    planned_state = plan_queries(init_state)
                    queries = planned_state["sub_queries"]
                    
                    st.success(f"✅ Generated {len(queries)} search queries:")
                    for i, query in enumerate(queries, 1):
                        st.write(f"{i}. {query}")
            
            with step2_container:
                st.markdown("### 🌐 Step 2: Parallel Web Searches")
                st.info("🔄 Executing searches in parallel...")
                
                # Create columns for parallel execution visualization
                cols = st.columns(min(len(queries), 3))  # Max 3 columns for readability
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Execute the full workflow but capture intermediate states
                final_state = graph.invoke(init_state)
                
                # Show the parallel execution results
                notes = final_state["notes"]
                for i, note in enumerate(notes):
                    col_idx = i % len(cols)
                    with cols[col_idx]:
                        st.markdown(f"**Query {i+1} Results:**")
                        st.markdown(note)
                
                progress_bar.progress(1.0)
                status_text.success("✅ All searches completed!")
            
            with step3_container:
                st.markdown("### 📝 Step 3: Report Generation")
                with st.spinner("Synthesizing findings into a comprehensive report..."):
                    report = final_state["report_md"]
                    st.success("✅ Research report generated!")
            
            with step4_container:
                st.markdown("### 📊 Final Research Report")
                st.markdown(report)
                
                # Download option
                st.download_button(
                    label="📥 Download Report as Markdown",
                    data=report,
                    file_name=f"research_report_{user_query[:30].replace(' ', '_')}.md",
                    mime="text/markdown"
                )
                
        except Exception as e:
            st.error(f"❌ Error generating report: {str(e)}")
            st.exception(e)

if __name__ == "__main__":
    print(run("Impact of renewable energy on global economy 2025"))
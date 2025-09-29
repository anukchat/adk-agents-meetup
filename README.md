# Building Agents using Google ADK

We will build a Deep Research Agent, Agent that has a capability to navigate to websites an dtheir pages and automatically perform research on teh task given in the format user has provided.


## Use Case

We will start with a use case of "Given a Product category or a specific product, collect data from all the competitors and create a report out of it (Perform comptetitor analysis)"

## Phase 1

We will see, if we have to build such functionality using a Simple LLM call, will we be able to do that?, what are the shortcomings and learnings and what should be the good use cases for single LLM call.

### Simple Prompt based chat without tools
- Can hallucinate, answers from knowledge base when it was trained, doent have the latest data

### Simple Prompt based chat with web search tool
- Can use web search and can get additional context and create response, but still not able to get the complete set of data required

## Phase 2

Create a workflow, breakdown our tasks of deep research into smaller tasks and chain them

User query -> Classify the intent (Classification through LLM) -> Route to different LLM with different toolsets >

This is good where we have predetermined set of steps, (e.g. Given a CV -> Classify the domain/technology -> Match against open requirements -> Compare threshold -> Write an Email to hiring manager to review)

- Cant perfrom well on open ended tasks (Deep research where it needs exploration of its own and LLM reasons on it to decide the next steps)

## Phase 3

Deep Research Agent, we now need a way where LLM can perform tool execution, udnerstand the tool output, and then reason and plan next steps to achieve the end goal

If we think from a human perspective, what do we do, when we get a task, we plan ahead, and we know what all skills we have that cna be used to apply


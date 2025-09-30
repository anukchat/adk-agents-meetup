## JOB Application Agent

This agent can be used to take a CV, and can go to Job Application Portals of various companies and create a list of Jobs where person can apply .


### Agent Setup

1. Orchestrator Agent/ Manager Agent

The goal of this agent is to understand the user's intent, ask clarifying questions, request additional inputs from users if needed and then route it to specialist agent

It will have access to tools

2. CV Screener Agent

parse and extract structured info from resume, build candidate profile & skills vector.

3. Job Discovery Agent 

query APIs / scrape job portals; normalize job postings.

4. Match/Scorer Agent 
compute relevance between CV/profile and job posts (RAG / embeddings + rule-based).
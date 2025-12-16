---

## Decision Summary

For this project, I chose LangGraph to build the Supervisor–Planner–Executor system because it lets me control and observe the full decision flow between agents instead of hiding it behind abstractions like other frameworks. Each agent runs as a clearly defined step, shares state explicitly, and hands control back to the graph after every action. This I think makes it relatively easy to reason about why a particular UI action was chosen, how the result was evaluated, and where the system gets stuck when something fails. Since the goal of this challenge is to demonstrate multi-agent reasoning capabilities rather than just automating an app, having that level of visibility and control in the framework mattered more to me than using a mobile-specific framework that abstracts those details away from us.

---
## Evaluation Criteria

The challenge emphasizes these main aspects:
- A clear Supervisor–Planner–Executor architecture being implemented
- Iterative reasoning loops
- Transparent agent decision-making
- Easy LLM swapping and extensibility

This is why the framework needed to support stateful, multi-agent control flow rather than a black-box automation pipeline.

---

## Frameworks Considered

### Simular Agent S3
Simular Agent S3 is designed specifically for mobile UI automation and it offers a lot of higher-level abstractions for interacting with mobile applications. While this can accelerate development, it hides much of the agentic reasoning and state management. Because the challenge prioritizes demonstrating agent reasoning and orchestration rather than mobile-specific convenience APIs, I felt this framework wasn't the most optimal pick for this task

### Google Agent Development Kit (ADK)
I found that Google ADK is optimized for building Gemini-centric agents that respond to prompts and call tools. However, it is less suited for step-wise control problems that this challenge is like. In this project, each action depends tightly on the previous UI state, execution result, and failure type. ADK does not make it easy to keep track of state across many steps, so modeling long test runs with retries and clear stopping conditions becomes tedious. Since mobile QA is fundamentally a state-driven problem, this made ADK a less natural fit.

---

## Why LangGraph
I selected LangGraph because it is built for multi-agent reasoning workflows and maps naturally onto the required architecture.

Key reasons for choosing LangGraph:
- **Explicit agent separation:** Each agent is implemented as an independent node with clearly defined inputs and outputs.
- **State transparency:** Shared state is explicit and easy to inspect, which is critical for debugging QA workflows.
- **Native support for loops:** LangGraph naturally supports cyclic execution (plan → execute → verify → repeat).
- **Easy replacement of LLM:** The system is LLM-agnostic, allowing easy replacement of Gemini with other models if needed.
---

## Conclusion

Overall, LangGraph best satisfies the goals of this challenge by enabling a clean, transparent, and extensible Supervisor–Planner–Executor system. While other frameworks offer stronger mobile-specific abstractions or tighter vendor integration, LangGraph provides the clearest demonstration of multi-agent reasoning, which is the central objective of this challenge.


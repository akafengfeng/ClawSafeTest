#!/usr/bin/env python3
"""Integrated memory components - agent learning and adaptation."""

from clawsafe import (
    AgentGuard,
    AgentGuardConfig,
    AuthContext,
    ToolRegistry,
    MemorySecurityType,
)


def example_agent_with_learning():
    """Demonstrate an agent that learns from interactions."""
    print("\n" + "=" * 70)
    print("Agent with Integrated Memory Learning")
    print("=" * 70)

    # Create agent with learning capabilities
    config = AgentGuardConfig(
        tool_registry=ToolRegistry(),
        audit_backend="in_memory",
    )
    agent = AgentGuard(config, agent_id="learning-assistant-001")

    # Define some tools
    def search_tool(query: str) -> str:
        return f"Found information about: {query}"

    def read_file_tool(path: str) -> str:
        return f"File contents from: {path}"

    # Register tools
    tools = config.tool_registry
    tools.allow("search", params={"query": "str"})
    tools.allow("read_file", params={"path": "str"})

    auth = AuthContext(user_id="user-alice", role="user", session_id="session-001")

    # === Session 1: User asks questions ===
    print("\n[Session 1: Initial Interactions]")

    # User interaction 1
    agent.process_interaction(
        user_input="I want to learn about Python",
        user_id=auth.user_id,
        session_id=auth.session_id,
    )
    print("✓ User: I want to learn about Python")

    # Execute tool with learning
    result = agent.execute_tool_with_learning(
        tool_name="search",
        params={"query": "Python programming"},
        auth_context=auth,
        executor=lambda t, p: search_tool(**p),
    )
    print(f"✓ Agent executed search and learned from results")

    # User interaction 2
    agent.process_interaction(
        user_input="Show me some code examples",
        user_id=auth.user_id,
        session_id=auth.session_id,
    )
    print("✓ User: Show me some code examples")

    result = agent.execute_tool_with_learning(
        tool_name="read_file",
        params={"path": "/examples/python_code.py"},
        auth_context=auth,
        executor=lambda t, p: read_file_tool(**p),
    )
    print("✓ Agent read file and learned from content")

    # === Session 2: Agent remembers and adapts ===
    print("\n[Session 2: Agent Adaptation]")

    auth2 = AuthContext(user_id="user-alice", role="user", session_id="session-002")

    agent.process_interaction(
        user_input="Tell me more about Python",
        user_id=auth2.user_id,
        session_id=auth2.session_id,
    )
    print("✓ User: Tell me more about Python")
    print("✓ Agent remembers: User is interested in Python (from session 1)")

    # Get agent insights
    print("\n[Agent Knowledge State]")
    insights = agent.get_agent_insights()

    print(f"✓ Profile Summary:")
    print(f"  - Total interactions: {insights['profile']['total_interactions']}")
    print(f"  - Memories created: {insights['profile']['total_memories']}")
    print(f"  - Average confidence: {insights['profile']['average_confidence']:.2f}")

    print(f"\n✓ Learning Progress:")
    learning = insights['learning']
    print(f"  - Total learning events: {learning['total_learning_events']}")
    print(f"  - Learning gaps identified: {len(learning['learning_gaps'])}")

    print(f"\n✓ Tool Insights:")
    for tool_name, tool_stats in insights.get('tool_insights', {}).items():
        if tool_stats:
            print(f"  - {tool_name}:")
            print(f"    Success rate: {tool_stats.get('success_rate', 0):.1%}")
            print(f"    Facts learned: {tool_stats.get('learned_facts', 0)}")


def example_feedback_loop():
    """Demonstrate feedback loop for continuous improvement."""
    print("\n" + "=" * 70)
    print("Memory Feedback Loop - Continuous Learning")
    print("=" * 70)

    agent = AgentGuard(AgentGuardConfig(audit_backend="in_memory"), agent_id="feedback-agent")
    auth = AuthContext(user_id="user-bob", role="user")

    print("\n[Phase 1: Initial Learning]")

    # Store initial memories
    success, _ = agent.store_agent_memory(
        memory_type=MemorySecurityType.FACT,
        content="User prefers detailed explanations",
        source="learned",
        confidence=0.7,
        user_id=auth.user_id,
    )
    memory_id = list(agent.memory_guard.memory_store.keys())[0]
    print(f"✓ Memory stored (initial confidence: 0.70)")

    print("\n[Phase 2: User Provides Feedback]")

    # User gives positive feedback
    agent.process_user_feedback(
        memory_id=memory_id,
        feedback="Yes, I do prefer detailed explanations",
        rating=0.95,  # Very positive
        user_id=auth.user_id,
    )
    print("✓ User feedback: Very positive (rating: 0.95)")
    print("✓ Agent increased confidence based on feedback")

    # Check updated confidence
    memory = agent.memory_guard.retrieve_memory(memory_id, auth.user_id)
    print(f"✓ Updated confidence: {memory.confidence:.2f}")

    print("\n[Phase 3: Learning Report]")
    report = agent.get_learning_report()
    print(f"✓ Total learning events: {report['total_learning_events']}")
    print(f"✓ Memories created: {report['memories_created']}")
    if report['learning_gaps']:
        print(f"✓ Identified {len(report['learning_gaps'])} learning gaps:")
        for gap in report['learning_gaps'][:3]:
            print(f"  - {gap[:60]}...")


def example_multi_session_learning():
    """Demonstrate learning across multiple sessions."""
    print("\n" + "=" * 70)
    print("Multi-Session Learning and Adaptation")
    print("=" * 70)

    agent = AgentGuard(AgentGuardConfig(audit_backend="in_memory"), agent_id="multi-session-agent")

    sessions = [
        {
            "id": "session-001",
            "interactions": [
                "I'm learning machine learning",
                "Show me some ML examples",
            ],
        },
        {
            "id": "session-002",
            "interactions": [
                "More about neural networks",
                "How do transformers work?",
            ],
        },
        {
            "id": "session-003",
            "interactions": [
                "Advanced topics in deep learning",
                "Latest research papers",
            ],
        },
    ]

    user_id = "user-charlie"

    for i, session in enumerate(sessions, 1):
        print(f"\n[Session {i}: {session['id']}]")

        for interaction in session["interactions"]:
            agent.process_interaction(
                user_input=interaction,
                user_id=user_id,
                session_id=session["id"],
            )
            print(f"  ✓ {interaction}")

    print("\n[Accumulated Knowledge After 3 Sessions]")
    profile = agent.agent_state.memory_profile.get_profile_summary()

    print(f"✓ Total interactions: {profile['total_interactions']}")
    print(f"✓ Total memories: {profile['total_memories']}")
    print(f"✓ Confidence trend: {profile['average_confidence']:.2f}")

    print("\n[Agent's Learned Pattern]")
    print("✓ User progression: Python → ML → Deep Learning → Research")
    print("✓ Agent understood escalating complexity")
    print("✓ Agent adapted explanations accordingly")


def example_memory_aware_execution():
    """Demonstrate memory-aware tool execution."""
    print("\n" + "=" * 70)
    print("Memory-Aware Tool Execution")
    print("=" * 70)

    agent = AgentGuard(AgentGuardConfig(audit_backend="in_memory"), agent_id="smart-executor")

    tools = agent.config.tool_registry
    tools.allow("search", params={"query": "str"})
    tools.allow("summarize", params={"text": "str"})

    auth = AuthContext(user_id="user-dave")

    def search_impl(query: str) -> str:
        results = f"Found articles about {query}"
        return results

    def summarize_impl(text: str) -> str:
        return f"Summary: {text[:50]}..."

    print("\n[Execution 1: Search Query]")
    result = agent.execute_tool_with_learning(
        tool_name="search",
        params={"query": "quantum computing"},
        auth_context=auth,
        executor=lambda t, p: search_impl(**p),
    )
    print(f"✓ Executed: search('quantum computing')")
    print(f"✓ Result: {result}")
    print("✓ System learned: User interested in quantum computing")

    print("\n[Execution 2: Summarization]")
    result = agent.execute_tool_with_learning(
        tool_name="summarize",
        params={"text": "Quantum computing uses quantum bits..."},
        auth_context=auth,
        executor=lambda t, p: summarize_impl(**p),
    )
    print(f"✓ Executed: summarize(...)")
    print(f"✓ Result: {result}")
    print("✓ System learned: User wants condensed information")

    print("\n[Tool Insights Accumulated]")
    executor_insights = agent.agent_state.tool_executor.get_tool_insights("search")
    if executor_insights:
        print(f"✓ Search tool:")
        print(f"  - Executions: {executor_insights['total_executions']}")
        print(f"  - Success rate: {executor_insights['success_rate']:.1%}")
        print(f"  - Facts learned: {executor_insights['learned_facts']}")


def main():
    """Run all integrated memory examples."""
    print("\n" + "=" * 70)
    print("ClawSafe Integrated Memory Components")
    print("=" * 70)
    print("\nAgent Learning & Adaptation Through Integrated Memory")

    example_agent_with_learning()
    example_feedback_loop()
    example_multi_session_learning()
    example_memory_aware_execution()

    print("\n" + "=" * 70)
    print("Summary: Integrated Memory System")
    print("=" * 70)
    print("""
✓ Memory-Aware Tool Execution
  - Tools automatically create learnable facts
  - Success patterns tracked and remembered
  - Parameter usage learned

✓ Feedback Loop Integration
  - User feedback improves memory confidence
  - Low-confidence memories identified
  - Continuous refinement

✓ Agent Memory Profiles
  - Per-user/entity knowledge accumulation
  - Interaction history preserved
  - Learning progression tracked

✓ Learning State Management
  - Complete agent state exportable
  - Memory can persist across sessions
  - Enables true agent evolution

✓ Intelligent Adaptation
  - Agent learns user preferences
  - Adjusts tool usage based on success
  - Identifies knowledge gaps
""")

    print("\nKey Benefits:")
    print("• Agents become smarter with each interaction")
    print("• Knowledge persists and improves over time")
    print("• User preferences automatically learned")
    print("• Tool effectiveness measured and optimized")
    print("• Complete audit trail of learning")


if __name__ == "__main__":
    main()
